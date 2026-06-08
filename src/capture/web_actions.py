"""
AUTOR: David Martín Castro
This script contains the functions that were automatically made on the test page

Adapted By: Nelly Ramos
Script extended to implement the TTS/dyslexia scenario's canary seeding and user-like interactions.
"""

#--------------------- LIBRARIES IMPORTS -------------------

from playwright.async_api import Page
import asyncio

from src.common.canaries import CanarySet
from src.common.colours import *

#--------------------- SCENARIO TUNING ---------------------

EXTRA_TAB_WAIT_SECONDS = 5               # wait for the extension to open onboarding/extra tabs, then close them
SETTLE_SECONDS         = 2               # let content scripts / dyslexia restyling apply after load
DWELL_SECONDS          = 300             # manual-interaction window: log into Gmail, click sign-in, open sidebar; also lets async exfiltration fire before closing
SCROLL_STEPS           = 4               # number of scroll increments to simulate reading
ENABLE_WEB_SEARCH      = False           # Optional: real sensitive-topic search engine query
SEARCH_ENGINE          = "duckduckgo"    # "duckduckgo" | "google"

#--------------------- FUNCTIONS ---------------------------

async def actions_on_web(page: Page, canaries: CanarySet):
    """
    Deterministic, bounded scripted session for TTS/dyslexia extensions.

    Drives the local reading page, seeds the canary tokens (in plaintext) across
    their channels, simulates reading/selection/composing/searching, then dwells
    so async extension traffic is captured. Never waits for a manual window close;
    every step is tolerant so a missing selector or a navigation can't hang/abort.
    Both passes (with and without extension) call this with the SAME CanarySet so
    the diff stays valid.
    """

    # 0. Some extensions open onboarding/welcome tabs on load. Wait for them to
    #    appear, then close every tab except the one we drive so they don't pollute
    #    the capture.
    await asyncio.sleep(EXTRA_TAB_WAIT_SECONDS)
    for other in list(page.context.pages):
        if other != page:
            try:
                await other.close()
                print(f"{yellowColour}[!]{endColour}{grayColour} closed extra tab: {other.url}{endColour}")
            except Exception:
                pass

    # 1. Navigate to the local reading page (only the URL carries the url_token)
    try:
        await page.goto(canaries.reading_url(), wait_until="domcontentloaded")
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour} goto reading page: {e}{endColour}")

    # 2. Settle: give content scripts time to run / dyslexia aids to restyle
    await asyncio.sleep(SETTLE_SECONDS)

    # 3. Seed the DOM/localStorage canaries (kept out of the URL for channel separation)
    try:
        await page.evaluate(
            """(t) => {
                const c = document.querySelector('#content-canary');
                if (c) c.textContent = t.content;
                const a = document.querySelector('#auth-canary');
                if (a) a.value = t.auth;
                try { localStorage.setItem('auth_token', t.auth); } catch (e) {}
            }""",
            {"content": canaries.content_token, "auth": canaries.auth_token},
        )
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour} seeding DOM canaries: {e}{endColour}")

    # 4. Simulate reading: scroll through the article in steps
    for _ in range(SCROLL_STEPS):
        try:
            await page.mouse.wheel(0, 600)
            await asyncio.sleep(0.5)
        except Exception:
            pass

    # 5. Select a paragraph (drives selection-based TTS read-aloud behavior)
    try:
        await page.evaluate(
            """() => {
                const el = document.querySelector('#reader-text p');
                if (!el) return;
                const r = document.createRange();
                r.selectNodeContents(el);
                const s = window.getSelection();
                s.removeAllRanges();
                s.addRange(r);
            }"""
        )
        await asyncio.sleep(1)
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour} text selection: {e}{endColour}")

    # 6. Compose: type the form canary into the editable area
    try:
        await page.fill("#compose", canaries.form_token)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour} compose fill: {e}{endColour}")

    # 7. On-page search box: seed the search canary (no submit; value is enough)
    try:
        await page.fill("#search", canaries.search_token)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour} search fill: {e}{endColour}")

    # 8. Multi-page history probe: visit distinct local pages, each carrying its own
    #    history token in the URL only. Leak of the SET proves browsing-history harvest.
    for url in canaries.history_urls():
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"{yellowColour}[!]{endColour}{grayColour} history visit (skipped): {e}{endColour}")

    # 9. Optional: real sensitive-topic search (tolerant, non-blocking, navigates last)
    if ENABLE_WEB_SEARCH:
        try:
            await page.goto(canaries.search_url(SEARCH_ENGINE), wait_until="domcontentloaded")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"{yellowColour}[!]{endColour}{grayColour} web search (skipped): {e}{endColour}")

    # 10. Dwell so asynchronous extension exfiltration has time to be captured
    await asyncio.sleep(DWELL_SECONDS)
