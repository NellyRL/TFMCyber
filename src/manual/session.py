"""
AUTHOR: Nelly Ramos

Playwright-free, human-driven analysis session for the "Análisis Manual" tab.

Google blocks sign-in in any CDP/automation-controlled browser, so the automated
tool cannot drive samples that require a Google login (e.g. Gemini, Formula Rush);
it is also the universal fallback for any sample when the automated path misbehaves.

This module seeds the SAME CanarySet as the automated run, starts the local PHP
test server and (optionally) a mitmdump capture, side-loads the unpacked extension
into a throwaway bundled-Chromium profile, and hands the browser to the operator.
There is NO scripted dwell: the session lasts exactly as long as the operator keeps
the browser open, and `finish()` runs when they click "Finalizar sesión". Every run
writes a session log (.md + .json) so the experiment is documented and repeatable.

No CDP, no asyncio: every external process is a non-blocking subprocess.Popen, so
the DearPyGui render loop is never blocked.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone

from src.common import paths
from src.common import files as fileUtils
from src.common.canaries import CanarySet
from src.common.colours import *

#---------------------------- TOOL RESOLUTION ----------------------------

def _resolve_chromium() -> str:
    """Path to Playwright's bundled Chromium (engine parity with automated runs)."""
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    try:
        return p.chromium.executable_path
    finally:
        p.stop()


def _resolve_mitmdump() -> str | None:
    """
    Locate mitmdump robustly: PATH first, then next to the running interpreter
    (covers a venv where mitmproxy is installed but PATH is not activated).
    Returns None if not found, so the caller can degrade to a no-capture session.
    """
    exe = shutil.which("mitmdump")
    if exe:
        return exe
    cand = os.path.join(os.path.dirname(sys.executable), "Scripts", "mitmdump.exe")
    return cand if os.path.exists(cand) else None


# Capture modes for the manual session:
#   "off"      -> no proxy, no capture
#   "managed"  -> the tool spawns/kills mitmdump and owns the .flow file
#   "external" -> the operator started mitmproxy separately; the tool only routes
#                 the browser through it and never starts/stops a proxy
MITM_MODES = ("off", "managed", "external")
DEFAULT_PROXY_ADDR = "127.0.0.1:8081"


def _port_open(addr: str, timeout: float = 0.5) -> bool:
    """True if something is accepting TCP connections at host:port (addr)."""
    try:
        host, port = addr.rsplit(":", 1)
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


# Generic checklist labels (no per-run tokens). The token/URL-filled detail lives
# in `steps_detail()`. Kept here so the GUI can pre-create the checkboxes on the
# main thread and the log can record which ones the operator ticked.
STEP_LABELS = [
    "1. Navegador abierto en la página de lectura.",
    "2. Snippet pegado en DevTools > Console (siembra los canarios).",
    "3. Función principal de la extensión activada.",
    "4. Artículo desplazado y un párrafo seleccionado en #reader-text.",
    "5. Visitadas en orden las 3 URLs de historial.",
    "6. Sesión conducida a tu ritmo (sin tiempo de espera impuesto).",
    "7. Navegador cerrado manualmente.",
]


#---------------------------- MANUAL SESSION -----------------------------

class ManualSession:
    """One human-driven analysis of a single extension. Build → start() → finish()."""

    def __init__(self, extension_path: str, output_dir: str = "",
                 mitm_mode: str = "external", proxy_addr: str = DEFAULT_PROXY_ADDR,
                 use_mitm: bool | None = None):
        self.extension_path = extension_path
        self.sample         = os.path.splitext(os.path.basename(extension_path))[0]
        base                = output_dir or paths.get_output_path()
        self.session_dir    = os.path.join(base, "manual", self.sample)
        self.unpacked_dir   = os.path.join(self.session_dir, "unpacked")

        # Back-compat shim: legacy callers passed use_mitm (True/False).
        if use_mitm is not None:
            mitm_mode = "managed" if use_mitm else "off"
        if mitm_mode not in MITM_MODES:
            raise ValueError(f"mitm_mode debe ser uno de {MITM_MODES}, no {mitm_mode!r}")
        self.mitm_mode  = mitm_mode
        self.proxy_addr = proxy_addr

        # The tool only owns a .flow file in 'managed' mode; in 'external' the
        # operator's own mitmproxy writes it (suggested path below), in 'off' none.
        self.flow_path  = os.path.join(paths.get_captures_path(), f"{self.sample}.flow") \
                          if mitm_mode == "managed" else None
        # Path we recommend the operator pass to `mitmdump -w` so the artifact
        # matches the managed-mode location.
        self.suggested_flow = os.path.join(paths.get_captures_path(), f"{self.sample}.flow")

        self.canaries: CanarySet | None = None
        self.warnings: list[str] = []
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None

        self._php      = None
        self._mitm     = None
        self._browser  = None
        self._crx_zip  = None
        self._chromium = ""
        self._browser_args: list[str] = []

    #------------------------ LIFECYCLE ----------------------------------

    def start(self) -> dict:
        """Seed canaries, start servers, unpack + side-load the extension, launch
        the browser. Returns a brief dict the GUI renders. Raises on fatal setup
        errors (missing php / failed unpack), leaving nothing half-started."""
        os.makedirs(self.session_dir, exist_ok=True)
        paths.ensure_output_dir()  # guarantees output\ + captures\
        self.started_at = datetime.now(timezone.utc)

        # 1. Canaries (same contract Proposal E will read)
        self.canaries = CanarySet.new()
        self.canaries.save(self.session_dir)

        # 2. Local PHP test server (verbatim invocation from orchestrator.main)
        php = shutil.which("php")
        if not php:
            raise RuntimeError("php no encontrado en PATH: no se puede servir la página local.")
        self._php = subprocess.Popen(
            [php, "-S", "127.0.0.1:8080", "-t", paths.get_web_page_dir()],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

        # 3. Capture, per mode:
        #    - managed : the tool spawns mitmdump and owns the .flow file
        #    - external: the operator started mitmproxy separately; we only verify
        #                it is listening and REFUSE to start if it is not
        #    - off     : nothing
        if self.mitm_mode == "managed":
            mitm = _resolve_mitmdump()
            if mitm:
                port = self.proxy_addr.rsplit(":", 1)[-1]
                self._mitm = subprocess.Popen(
                    [mitm, "--listen-port", port, "-w", self.flow_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
            else:
                self.mitm_mode = "off"
                self.flow_path = None
                self.warnings.append(
                    "mitmdump no encontrado: la sesión continúa SIN captura de tráfico."
                )
        elif self.mitm_mode == "external":
            if not _port_open(self.proxy_addr):
                self._terminate_servers()
                raise RuntimeError(
                    f"Modo externo: no hay ningún proxy escuchando en {self.proxy_addr}. "
                    f"Arranca mitmproxy primero, p.ej.:\n"
                    f"  mitmweb --listen-port {self.proxy_addr.rsplit(':', 1)[-1]} --web-port 8082\n"
                    f"  (o)  mitmdump --listen-port {self.proxy_addr.rsplit(':', 1)[-1]} -w \"{self.suggested_flow}\"\n"
                    f"y asegúrate de haber confiado en la CA de mitmproxy."
                )

        # 4. Unpack the extension into its OWN dir (never the shared automated dir)
        if os.path.exists(self.unpacked_dir):
            shutil.rmtree(self.unpacked_dir, ignore_errors=True)
        os.makedirs(self.unpacked_dir, exist_ok=True)
        try:
            if self.extension_path.endswith(".crx"):
                self._crx_zip = fileUtils.decompress_crx(self.extension_path, self.unpacked_dir)
            else:
                fileUtils.decompress_extension(self.extension_path, self.unpacked_dir)
        except Exception as e:
            self._terminate_servers()
            raise RuntimeError(f"No se pudo descomprimir la extensión: {e}")

        # 5. Launch a throwaway, optionally-proxied Chromium (NO CDP, NO automation)
        self._chromium = _resolve_chromium()
        profile = os.path.join(os.environ.get("TEMP", self.session_dir), "tfm_manual_profile")
        self._browser_args = [
            self._chromium,
            f"--user-data-dir={profile}",
            f"--load-extension={self.unpacked_dir}",
        ]
        if self.mitm_mode in ("managed", "external"):
            self._browser_args.append(f"--proxy-server={self.proxy_addr}")
        self._browser_args.append(self.canaries.reading_url())
        self._browser = subprocess.Popen(self._browser_args)

        return self._brief()

    def finish(self, ticked: list | None = None) -> str:
        """Stop capture + servers (NOT the browser — the operator closes it), then
        write the session log. Returns the .md log path."""
        self.ended_at = datetime.now(timezone.utc)
        self._terminate_servers()
        if self._crx_zip:
            fileUtils.remove_crx_zip(self._crx_zip)
        return self._write_log(ticked)

    #------------------------ INTERNALS ----------------------------------

    def _terminate_servers(self) -> None:
        for proc in (self._mitm, self._php):
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass

    def console_snippet(self) -> str:
        """DevTools snippet that seeds the same channels as web_actions.actions_on_web
        (selectors verified against assets/web_page/reading.php)."""
        c = self.canaries
        return (
            f"document.querySelector('#content-canary').textContent = '{c.content_token}';\n"
            f"document.querySelector('#auth-canary').value          = '{c.auth_token}';\n"
            f"document.querySelector('#compose').value              = '{c.form_token}';\n"
            f"document.querySelector('#search').value               = '{c.search_token}';\n"
            f"localStorage.setItem('auth_token', '{c.auth_token}');\n"
            f"document.cookie = 'session_canary={c.cookie_token}; path=/';"
        )

    def steps_detail(self) -> list:
        """Token/URL-filled version of the checklist, shown read-only in the GUI and
        stored in the log for reproducibility."""
        urls = self.canaries.history_urls()
        return [
            f"1. El navegador se ha abierto en la página de lectura: {self.canaries.reading_url()}",
            "2. Abre DevTools (F12) > Console, pega el snippet y pulsa Enter "
            "(siembra content/auth/form/search + localStorage + cookie).",
            "3. Activa la función principal de la extensión (lectura en voz alta / "
            "reestilizado de dislexia / sidebar).",
            "4. Desplázate por el artículo de arriba a abajo y SELECCIONA un párrafo "
            "dentro de #reader-text (lectura por selección).",
            f"5. Visita en orden cada URL de historial:\n     - {urls[0]}\n     - {urls[1]}\n     - {urls[2]}",
            "6. Conduce la extensión A TU RITMO; NO hay tiempo de espera impuesto. "
            "La sesión dura lo que mantengas el navegador abierto.",
            "7. Al terminar, CIERRA la ventana del navegador y pulsa 'Finalizar sesión' "
            "para detener la captura/servidores y escribir el log.",
        ]

    def _brief(self) -> dict:
        return {
            "sample": self.sample,
            "reading_url": self.canaries.reading_url(),
            "history_urls": self.canaries.history_urls(),
            "console_snippet": self.console_snippet(),
            "steps": self.steps_detail(),
            "mitm_mode": self.mitm_mode,
            "proxy_addr": self.proxy_addr if self.mitm_mode in ("managed", "external") else None,
            "mitm_capture": self.mitm_mode != "off",
            "flow_path": self.flow_path,
            "external_capture_hint": (
                f'mitmdump --listen-port {self.proxy_addr.rsplit(":", 1)[-1]} '
                f'-w "{self.suggested_flow}"'
                if self.mitm_mode == "external" else None
            ),
            "session_dir": self.session_dir,
            "warnings": self.warnings,
        }

    def _sha256(self, path: str) -> str:
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _manifest_summary(self) -> dict:
        try:
            with open(os.path.join(self.unpacked_dir, "manifest.json"), encoding="utf-8") as f:
                m = json.load(f)
            return {
                "name": m.get("name"),
                "version": m.get("version"),
                "manifest_version": m.get("manifest_version"),
                "permissions": m.get("permissions"),
                "host_permissions": m.get("host_permissions"),
            }
        except Exception:
            return {}

    def _write_log(self, ticked: list | None) -> str:
        duration = None
        if self.started_at and self.ended_at:
            duration = int((self.ended_at - self.started_at).total_seconds())
        ticked = ticked or []
        ticked_labels = [STEP_LABELS[i] for i, v in enumerate(ticked) if v and i < len(STEP_LABELS)]

        data = {
            "sample": self.sample,
            "extension_path": self.extension_path,
            "extension_sha256": self._sha256(self.extension_path),
            "manifest": self._manifest_summary(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": duration,
            "mitm_mode": self.mitm_mode,
            "proxy_addr": self.proxy_addr if self.mitm_mode in ("managed", "external") else None,
            "mitm_capture": self.mitm_mode != "off",
            "flow_path": self.flow_path if self.mitm_mode == "managed" else None,
            "suggested_flow": self.suggested_flow if self.mitm_mode == "external" else None,
            "canaries_path": os.path.join(self.session_dir, "canaries.json"),
            "canaries": self.canaries.as_dict() if self.canaries else {},
            "browser_executable": self._chromium,
            "browser_args": self._browser_args,
            "reading_url": self.canaries.reading_url() if self.canaries else None,
            "history_urls": self.canaries.history_urls() if self.canaries else [],
            "console_snippet": self.console_snippet() if self.canaries else "",
            "steps": self.steps_detail() if self.canaries else [],
            "steps_completed": ticked_labels,
            "warnings": self.warnings,
        }

        os.makedirs(self.session_dir, exist_ok=True)
        json_path = os.path.join(self.session_dir, "session_log.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        md_path = os.path.join(self.session_dir, "session_log.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._render_md(data))
        return md_path

    def _render_md(self, d: dict) -> str:
        m = d["manifest"] or {}
        lines = [
            f"# Manual session — {d['sample']}",
            "",
            f"- **Extension file:** `{d['extension_path']}`",
            f"- **SHA-256:** `{d['extension_sha256']}`",
            f"- **Manifest:** {m.get('name')} v{m.get('version')} (MV{m.get('manifest_version')})",
            f"- **Permissions:** {m.get('permissions')}",
            f"- **Host permissions:** {m.get('host_permissions')}",
            f"- **Started:** {d['started_at']}",
            f"- **Ended:** {d['ended_at']}",
            f"- **Duration (s):** {d['duration_seconds']}",
            f"- **mitmproxy capture:** {d['mitm_capture']} (modo: {d['mitm_mode']}"
            + (f", proxy: `{d['proxy_addr']}`" if d.get('proxy_addr') else "") + ")",
            f"- **Flow file:** `{d['flow_path'] or d.get('suggested_flow') or '—'}`"
            + (" _(lo escribe tu mitmproxy externo)_" if d['mitm_mode'] == 'external' else ""),
            f"- **Canaries:** `{d['canaries_path']}`",
            f"- **Browser:** `{d['browser_executable']}`",
            "",
            "## Steps (this run)",
            "",
        ]
        lines += [f"{s}" for s in d["steps"]]
        lines += [
            "",
            "## Steps marked completed",
            "",
        ]
        lines += ([f"- {s}" for s in d["steps_completed"]] or ["- (none marked)"])
        lines += [
            "",
            "## Console snippet (seed canaries)",
            "",
            "```js",
            d["console_snippet"],
            "```",
            "",
            "## Observations",
            "",
            "_Fill in by hand after reviewing the capture._",
            "",
            "## Evidence table (one row per channel that leaked)",
            "",
            "| Channel | Leaked? | Destination (eTLD+1) | Party | Method | Encoding | Declared in policy? | Verdict |",
            "|---|---|---|---|---|---|---|---|",
            "| page content | | | | | | | |",
            "| editable form | | | | | | | |",
            "| search input | | | | | | | |",
            "| browsing history (set) | | | | | | | |",
            "| auth token / localStorage | | | | | | | |",
            "| cookie | | | | | | | |",
            "| URL (`ref`) | | | | | | | |",
            "",
            "**Malicious / abusive criterion:** a canary reaching a **third party** not "
            "disclosed in the extension's privacy policy / T&C.",
            "",
            f"_Next: run the leak scanner on `{d['flow_path'] or d.get('suggested_flow')}` once `scan_leaks.py` exists._",
            "",
        ]
        if d["warnings"]:
            lines += ["## Warnings", ""] + [f"- {w}" for w in d["warnings"]] + [""]
        return "\n".join(lines)
