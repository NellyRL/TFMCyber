import dearpygui.dearpygui as dpg
from tkinter import filedialog
import tkinter as tk
import os
import asyncio
import threading
from src.orchestrator import main
from src.model.predict import predict
from src.manual.session import ManualSession, STEP_LABELS

selected_output_dir = ""
last_w, last_h = 0, 0

# Manual-analysis tab state
manual_output_dir = ""
manual_session = None

# Maps the radio labels shown in the manual tab to ManualSession mitm modes.
MANUAL_MITM_LABELS = {
    "Externa (yo lanzo mitmproxy en 127.0.0.1:8081)": "external",
    "Gestionada (la herramienta lanza mitmdump)": "managed",
    "Sin captura": "off",
}

def select_file_callback():
    root = tk.Tk()
    root.withdraw()
    extension_path = filedialog.askopenfilename(filetypes=[("Extensiones", "*.crx *.zip")])
    root.destroy()

    if extension_path:
        dpg.set_value("selected_file", extension_path)
        dpg.set_value("status_text", "Archivo seleccionado, listo para analizar.")
    else:
        dpg.set_value("status_text", "No se seleccionó ningún archivo.")

def select_output_dir_callback():
    global selected_output_dir
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    root.destroy()

    if folder_selected:
        selected_output_dir = folder_selected
        dpg.set_value("selected_output_dir", folder_selected)
    else:
        dpg.set_value("selected_output_dir", "No se seleccionó ninguna carpeta.")

def confirm_callback():
    dpg.set_value("status_text", "Clasificación iniciada...")
    clase, p_assistant, p_other = predict(selected_output_dir + "/webGraphDiff.gexf")

    dpg.set_value("resultado_clase", f"Predicción: {clase.upper()}")
    dpg.set_value("prob_assistant", p_assistant)
    dpg.set_value("prob_other", p_other)

    dpg.configure_item("prob_assistant", overlay=f"Probabilidad assistant: {p_assistant:.2%}")
    dpg.configure_item("prob_other", overlay=f"Probabilidad other: {p_other:.2%}")

    # Color según clase
    if clase == "assistant":
        dpg.configure_item("resultado_clase", color=(0, 255, 0))  # Verde
    else:
        dpg.configure_item("resultado_clase", color=(255, 100, 100))  # Rojo claro

    dpg.delete_item("alert_popup")
    dpg.set_value("status_text", "Clasificación finalizada, resultados disponibles")


def exit_callback():
    dpg.stop_dearpygui()

def show_alert_popup():
    with dpg.window(label="Análisis Completado", modal=True, tag="alert_popup", no_resize=True, no_move=True, width=400, height=200, pos=(300, 250)):
        dpg.add_text("¿Deseas realizar una clasificación del grafo resultante?", wrap=350)
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Confirmar", width=120, callback=confirm_callback)
            dpg.add_button(label="Salir", width=120, callback=exit_callback)

def execute_analysis():
    extension_path = dpg.get_value("selected_file")
    if not extension_path or not os.path.exists(extension_path):
        dpg.set_value("status_text", "Error: Selecciona un archivo válido primero.")
        return

    dpg.set_value("status_text", "Analizando...")
    asyncio.run(main(extension_path, selected_output_dir))
    dpg.set_value("status_text", "Análisis completado correctamente.")
    show_alert_popup()

# ========== MANUAL ANALYSIS TAB ==========

def manual_select_file_callback():
    root = tk.Tk()
    root.withdraw()
    extension_path = filedialog.askopenfilename(filetypes=[("Extensiones", "*.crx *.zip")])
    root.destroy()
    if extension_path:
        dpg.set_value("manual_selected_file", extension_path)
        dpg.set_value("manual_status", "Extensión seleccionada, lista para la sesión manual.")
    else:
        dpg.set_value("manual_status", "No se seleccionó ninguna extensión.")

def manual_select_output_dir_callback():
    global manual_output_dir
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    root.destroy()
    if folder_selected:
        manual_output_dir = folder_selected
        dpg.set_value("manual_selected_output_dir", folder_selected)
    else:
        dpg.set_value("manual_selected_output_dir", "No se seleccionó ninguna carpeta.")

def _manual_start_worker():
    global manual_session
    extension_path = dpg.get_value("manual_selected_file")
    if not extension_path or not os.path.exists(extension_path):
        dpg.set_value("manual_status", "Error: selecciona una extensión válida primero.")
        return
    if manual_session is not None:
        dpg.set_value("manual_status", "Ya hay una sesión en curso. Pulsa 'Finalizar sesión' antes de iniciar otra.")
        return
    mitm_mode = MANUAL_MITM_LABELS.get(dpg.get_value("manual_mitm_mode"), "external")
    dpg.set_value("manual_status", "Iniciando sesión manual (sembrando canarios, lanzando navegador)...")
    try:
        session = ManualSession(extension_path, manual_output_dir, mitm_mode=mitm_mode)
        brief = session.start()
    except Exception as e:
        dpg.set_value("manual_status", f"Error al iniciar la sesión: {e}")
        return
    manual_session = session
    # Reset the checklist and fill the per-run detail
    for i in range(len(STEP_LABELS)):
        dpg.set_value(f"manual_step_{i}", False)
    dpg.set_value("manual_steps", "\n\n".join(brief["steps"]))
    dpg.set_value("manual_snippet", brief["console_snippet"])
    status = "Sesión manual EN CURSO. Conduce el navegador y pulsa 'Finalizar sesión' al terminar."
    if brief.get("external_capture_hint"):
        status += ("\nCaptura EXTERNA: tu mitmproxy ya está en uso. Para el mismo "
                   f".flow que el modo gestionado, lánzalo con:\n  {brief['external_capture_hint']}")
    if brief["warnings"]:
        status = "[!] " + " | ".join(brief["warnings"]) + "\n" + status
    dpg.set_value("manual_status", status)

def manual_start_callback():
    threading.Thread(target=_manual_start_worker, daemon=True).start()

def _manual_finish_worker():
    global manual_session
    if manual_session is None:
        dpg.set_value("manual_status", "No hay ninguna sesión activa.")
        return
    ticked = [dpg.get_value(f"manual_step_{i}") for i in range(len(STEP_LABELS))]
    try:
        log_path = manual_session.finish(ticked)
    except Exception as e:
        dpg.set_value("manual_status", f"Error al finalizar la sesión: {e}")
        return
    manual_session = None
    dpg.set_value("manual_status", f"Sesión finalizada. Log escrito en: {log_path}")

def manual_finish_callback():
    threading.Thread(target=_manual_finish_worker, daemon=True).start()

def manual_copy_snippet_callback():
    snippet = dpg.get_value("manual_snippet")
    if snippet:
        dpg.set_clipboard_text(snippet)
        dpg.set_value("manual_status", "Snippet copiado al portapapeles (solo dentro de la VM).")

# Adaptación al redimensionamiento

def resize_main_window():
    width = dpg.get_viewport_client_width()
    height = dpg.get_viewport_client_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)
    dpg.set_item_pos("main_window", (0, 0))

def check_viewport_resize():
    global last_w, last_h
    w = dpg.get_viewport_client_width()
    h = dpg.get_viewport_client_height()
    if w != last_w or h != last_h:
        resize_main_window()
        last_w, last_h = w, h

# ========== GUI ==========

def launch():

    dpg.create_context()

    with dpg.font_registry():
        try:
            default_font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 18)
        except:
            default_font = None

    with dpg.theme() as custom_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 120, 120, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 140, 140, 255))

    dpg.create_viewport(title="Analizador de Extensiones", width=1000, height=700, resizable=True)

    with dpg.window(tag="main_window", no_title_bar=True, no_resize=True, no_move=True,
                    pos=(0, 0), width=1000, height=700):
        with dpg.tab_bar():

            with dpg.tab(label="Análisis de Extensión"):
                dpg.add_spacer(height=30)
                with dpg.group(horizontal=False):
                    dpg.add_text("1. Selecciona una extensión (.crx o .zip)", bullet=True)
                    dpg.add_button(label="Seleccionar archivo", callback=select_file_callback, width=250)
                    dpg.add_input_text(tag="selected_file", readonly=True, width=600, hint="Ruta del archivo")

                    dpg.add_spacer(height=15)
                    dpg.add_text("2. Selecciona la carpeta de salida", bullet=True)
                    dpg.add_button(label="Seleccionar carpeta de salida", callback=select_output_dir_callback, width=250)
                    dpg.add_input_text(tag="selected_output_dir", readonly=True, width=600, hint="Ruta de salida")

                    dpg.add_spacer(height=20)
                    dpg.add_button(label="Ejecutar análisis", callback=execute_analysis, width=250)

                    dpg.add_spacer(height=25)
                    dpg.add_text("Estado:")
                    dpg.add_text("Esperando archivo...", tag="status_text")

            with dpg.tab(label="Resultados del Análisis"):
                dpg.add_text("Resultado del modelo:", tag="resultado_clase", color=(200, 200, 200))
                dpg.add_spacer(height=10)
                dpg.add_progress_bar(default_value=0.0, tag="prob_assistant", overlay="Probabilidad assistant: 0.0", width=400)
                dpg.add_progress_bar(default_value=0.0, tag="prob_other", overlay="Probabilidad other: 0.0", width=400)
                dpg.add_spacer(height=10)

            with dpg.tab(label="Análisis Manual"):
                dpg.add_spacer(height=15)
                dpg.add_text(
                    "Sesión manual: navegador normal (Chromium) con la extensión cargada, "
                    "sin Playwright/CDP ni tiempo de espera impuesto. Tú conduces y cierras.",
                    wrap=900,
                )
                dpg.add_spacer(height=15)

                dpg.add_text("1. Selecciona una extensión (.crx o .zip)", bullet=True)
                dpg.add_button(label="Seleccionar archivo", callback=manual_select_file_callback, width=250)
                dpg.add_input_text(tag="manual_selected_file", readonly=True, width=600, hint="Ruta del archivo")

                dpg.add_spacer(height=10)
                dpg.add_text("2. Carpeta de salida (opcional; por defecto output\\manual\\)", bullet=True)
                dpg.add_button(label="Seleccionar carpeta de salida", callback=manual_select_output_dir_callback, width=250)
                dpg.add_input_text(tag="manual_selected_output_dir", readonly=True, width=600, hint="Ruta de salida")

                dpg.add_spacer(height=10)
                dpg.add_text("3. Captura de tráfico", bullet=True)
                dpg.add_radio_button(
                    list(MANUAL_MITM_LABELS.keys()),
                    tag="manual_mitm_mode",
                    default_value="Externa (yo lanzo mitmproxy en 127.0.0.1:8081)",
                )
                dpg.add_text(
                    "Modo EXTERNA (por defecto): arranca tú el proxy ANTES de iniciar, p.ej.\n"
                    "  mitmweb --listen-port 8081 --web-port 8082\n"
                    "  (o)  mitmdump --listen-port 8081 -w output\\captures\\<sample>.flow\n"
                    "y confía en la CA (certutil -addstore -f Root ...mitmproxy-ca-cert.cer).\n"
                    "Si nada escucha en 8081, la sesión NO arranca.",
                    wrap=900, color=(170, 170, 170),
                )

                dpg.add_spacer(height=15)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Iniciar sesión manual", callback=manual_start_callback, width=220)
                    dpg.add_button(label="Finalizar sesión", callback=manual_finish_callback, width=220)

                dpg.add_spacer(height=15)
                dpg.add_text("Pasos de esta ejecución:")
                dpg.add_input_text(tag="manual_steps", multiline=True, readonly=True, width=900, height=180,
                                   hint="Inicia una sesión para ver los pasos con las URLs/tokens de esta ejecución.")

                dpg.add_spacer(height=10)
                dpg.add_text("Checklist (marca lo que vayas completando; se guarda en el log):")
                for i, label in enumerate(STEP_LABELS):
                    dpg.add_checkbox(label=label, tag=f"manual_step_{i}", default_value=False)

                dpg.add_spacer(height=10)
                dpg.add_text("Snippet para la consola de DevTools (siembra los canarios):")
                dpg.add_input_text(tag="manual_snippet", multiline=True, readonly=True, width=900, height=130,
                                   hint="Disponible tras iniciar la sesión.")
                dpg.add_button(label="Copiar snippet", callback=manual_copy_snippet_callback, width=200)

                dpg.add_spacer(height=15)
                dpg.add_text("Estado:")
                dpg.add_text("Esperando extensión...", tag="manual_status", wrap=900)

    # === Lanzamiento de DearPyGui ===
    dpg.setup_dearpygui()
    dpg.bind_theme(custom_theme)
    if default_font:
        dpg.bind_font(default_font)
    resize_main_window()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        check_viewport_resize()
        dpg.render_dearpygui_frame()

    # If a manual session is still active when the app closes, stop its servers
    # (PHP / mitmdump) so they are not left orphaned. The browser is the operator's.
    if manual_session is not None:
        try:
            manual_session.finish()
        except Exception:
            pass

    dpg.destroy_context()
