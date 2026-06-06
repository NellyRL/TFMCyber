"""
AUTHOR: Nelly Ramos
This script contains the functions that were automatically made on the test page
Script extended to implement the TTS/dyslexia scenario's canary (honey token) seeding and user-like interactions.

Each run plants a set of unique, random, NON-SENSITIVE tokens (one per data
channel). The scenario seeds them in PLAINTEXT into the page/URL/inputs/cookie,
because plaintext is what an extension actually reads. The leak detector
later scans outbound traffic for each token AND its common
obfuscated encodings, so a token is recognized even if the
extension encodes it before exfiltrating.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import base64
import gzip
import json
import os
import secrets
from dataclasses import dataclass, asdict, field
from urllib.parse import quote

#---------------------------- TOKEN HELPERS ------------------------------

CANARY_PREFIX  = "cnry"
# Distinct topical pages visited to build a multi-page browsing history.
HISTORY_TOPICS = ("salud", "noticias", "compras")

def _new_token() -> str:
    """Returns a unique, recognizable, non-sensitive canary token."""
    return f"{CANARY_PREFIX}{secrets.token_hex(8)}"

def _new_history_tokens() -> list:
    """One token per page in the simulated browsing history (URL/history channel)."""
    return [_new_token() for _ in HISTORY_TOPICS]

#---------------------------- CANARY SET ---------------------------------

@dataclass
class CanarySet:
    """
    One random token per data channel relevant to the TTS/dyslexia scope.

    Channel separation is deliberate: only `url_token` is placed in the visited
    URL, so a leak maps unambiguously to a single channel.
    """
    url_token:        str  = field(default_factory=_new_token)           # visited URL query string
    content_token:    str  = field(default_factory=_new_token)           # page article body (DOM)
    form_token:       str  = field(default_factory=_new_token)           # editable textarea
    search_token:     str  = field(default_factory=_new_token)           # on-page search input
    auth_token:       str  = field(default_factory=_new_token)           # localStorage + hidden DOM field
    cookie_token:     str  = field(default_factory=_new_token)           # session cookie (set via Playwright)
    web_search_token: str  = field(default_factory=_new_token)           # real search engine query (Optional B)
    history_tokens:   list = field(default_factory=_new_history_tokens)  # multi-page browsing history

    @classmethod
    def new(cls) -> "CanarySet":
        """Factory: a fresh set of unique tokens."""
        return cls()

    #------------------------ SEEDING HELPERS ----------------------------

    def reading_url(self, base: str = "http://localhost:8080/reading.php") -> str:
        """Local reading page URL carrying ONLY the url_token (URL/history channel)."""
        return f"{base}?ref={self.url_token}"

    def search_url(self, engine: str = "duckduckgo") -> str:
        """
        Natural, sensitive-topic query that embeds the web_search_token so a leak
        is both realistic and provable (Optional B).
        """
        query = f"comprar {self.web_search_token} medicamento para dislexia precio"
        if engine == "google":
            return "https://www.google.com/search?q=" + quote(query)
        return "https://duckduckgo.com/?q=" + quote(query)

    def history_urls(self, base: str = "http://localhost:8080/topic.php") -> list:
        """
        Distinct local pages, each carrying ONLY its own history token in the URL.
        A leak of the SET of these tokens proves the extension harvests the
        browsing sequence, not just the current page.
        """
        return [
            f"{base}?t={topic}&ref={token}"
            for topic, token in zip(HISTORY_TOPICS, self.history_tokens)
        ]

    def cookie(self) -> dict:
        """Canary session cookie for the local origin (set via Playwright add_cookies)."""
        return {
            "name": "session_canary",
            "value": self.cookie_token,
            "url": "http://localhost:8080",
        }

    #------------------------ PERSISTENCE --------------------------------

    def as_dict(self) -> dict:
        return asdict(self)

    def save(self, output_dir: str) -> str:
        """Writes canaries.json (the contract Proposal E reads). Returns its path."""
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "canaries.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.as_dict(), file, indent=2)
        return path

    #------------------------ ENCODINGS -----------------

    @staticmethod
    def encodings(token: str) -> dict:
        """
        Common obfuscated representations of a token, mirroring the encodings from
        the privacy-diffusion paper. Provided here; the matching that consumes them
        belongs to Proposal E. NOTE for E: base64 of a substring shifts with byte
        alignment, so E should also decode-then-search candidate blobs, not only
        encode-then-match.
        """
        raw = token.encode()
        return {
            "plain": token,
            "url": quote(token),
            "base64": base64.b64encode(raw).decode(),
            "base64x2": base64.b64encode(base64.b64encode(raw)).decode(),
            "hex": raw.hex(),
            "gzip_b64": base64.b64encode(gzip.compress(raw)).decode(),
            "json": json.dumps(token),
        }
