"""
AUTOR: David Martín Castro
This script contains the main function, which is used to run the program.

Adapted By: Nelly Ramos
Script extended to implement the TTS/dyslexia scenario's canary seeding and user-like interactions.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

# External modules
import asyncio
import subprocess
from playwright.async_api import async_playwright, Playwright

# Own modules
from src.common import paths
from src.common import files as fileUtils
from src.common import times as timeUtils
from src.capture import cdp as cdpUtils
from src.graph.builder import create_graph
from src.graph.diff import graph_diff
from src.capture.web_actions import actions_on_web
from src.common.colours import *
from src.common.canaries import CanarySet

#------------------------- PREVIOUS INFORMATION DELETION -----------------

print(f"{greenColour}[+]{endColour}{grayColour} Deleting previous information...{endColour}")
fileUtils.remove_report()
fileUtils.remove_user_data()

#------------------------------ MAIN FUNCTION ----------------------------

print(f"{greenColour}[+]{endColour}{grayColour} Starting program...{endColour}")
# Start time of the program
timeUtils.start_time = timeUtils.get_current_time()

async def run(playwright: Playwright, extension_path: str, selected_output_dir: str, canaries: CanarySet) -> None:
    # Descompress the extension
    if extension_path.endswith(".crx"):
        crx_zip = fileUtils.decompress_crx(extension_path)
    else:
        fileUtils.decompress_extension(extension_path)
    # Create a new browser context
    context = await playwright.chromium.\
        launch_persistent_context(paths.get_user_data_path(), headless=False, \
        args=[f"--disable-extensions-except={paths.get_extension_path()}",\
        f"--load-extension={paths.get_extension_path()}"])
    
    # Seed the canary session cookie on the local origin (credential-theft probe)
    await context.add_cookies([canaries.cookie()])

    # We will use the first page created by the browser context
    page = context.pages[0]

    # Create a new CDP (Chrome DevTools Protocol) session
    cdp_session = await context.new_cdp_session(page)

    # Enable the events that we want to capture
    await cdpUtils.enable_events(cdp_session)

    # Set the breakpoints needed
    await cdpUtils.set_breakpoints(cdp_session)
    # Event listener events
    await cdpUtils.event_listener_events(cdp_session)
    async def api_call_detected(api_name):
        cdpUtils.apiCallName = api_name
        
    # Expose the api_call_detected, so it can be called from hooks.js
    await context.expose_function("pyNotify", api_call_detected)
    # Read the javascript file where the proxy is defined
    with open(paths.get_hooks_path(), "r", encoding="utf-8") as file:
            hooks = file.read()
    # Add the proxy and hooks to the context
    await context.add_init_script(hooks)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame != page.main_frame:
            return
        try:
            await cdpUtils.enable_events(cdp_session)
            await cdpUtils.set_breakpoints(cdp_session)
            await cdpUtils.event_listener_events(cdp_session)
            await context.add_init_script(hooks)
        except Exception as e:
            print(f"{yellowColour}[!]{endColour}{grayColour} re-arm after navigation skipped: {e}{endColour}")
    
    # Calling get_targets at the beginning of the program
    targets = await cdp_session.send("Target.getTargets")
    cdpUtils.get_targets(targets)

    # Call CDP functions
    cdpUtils.target_events(cdp_session)
    cdpUtils.page_events(cdp_session)
    cdpUtils.network_events(cdp_session)
    cdpUtils.execution_context_events(cdp_session)
    cdpUtils.script_events(cdp_session)
    cdpUtils.DOM_events(cdp_session)
    cdpUtils.paused_events(cdp_session)

    page.on("framenavigated", on_frame_navigated)

    # Navigation activities
    await actions_on_web(page, canaries)

    # We used a try to avoid errors when closing the context
    await asyncio.sleep(2)
    
    try:
        await context.close()
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour}{e}{endColour}")

    # Delete user data
    fileUtils.remove_user_data()

    # Generation of the json report
    await cdpUtils.generate_json_report(True)

    # Remove the extension
    fileUtils.remove_extension()
    # Remove the crx.zip file (if it exists)
    if extension_path.endswith(".crx"):
        fileUtils.remove_crx_zip(crx_zip)

    # Generation of Web Graph
    print(f"{greenColour}[+]{endColour}{grayColour} Creating Web Graph...{endColour}")
    create_graph(cdpUtils.report_json, True, selected_output_dir)
    print(f"{greenColour}[+]{endColour}{grayColour} Web Graph finished{endColour}")
    

    print(f"{greenColour}[+]{endColour}{grayColour} Program finished{endColour}")


#-------------------------- RUN WITHOUT EXTENSION ------------------------
async def run_without_extension(playwright: Playwright, canaries: CanarySet) -> None:

    cdpUtils.report_json = []
    # Create a new browser context
    context = await playwright.chromium.launch(headless=False)
    
    # We will use the first page created by the browser context
    page = await context.new_page()

    # Same canary cookie as the with-extension pass, so the diff stays valid
    await page.context.add_cookies([canaries.cookie()])

    # Create a new CDP (Chrome DevTools Protocol) session
    cdp_session = await page.context.new_cdp_session(page)

    # Enable the events that we want to capture
    await cdpUtils.enable_events(cdp_session)

    # Set the breakpoints needed
    await cdpUtils.set_breakpoints(cdp_session)
    # Event listener events
    await cdpUtils.event_listener_events(cdp_session)
    async def api_call_detected(api_name):
        cdpUtils.apiCallName = api_name
        
    # Expose the api_call_detected, so it can be called from hooks.js
    await page.context.expose_function("pyNotify", api_call_detected)
    # Read the javascript file where the proxy is defined
    with open(paths.get_hooks_path(), "r", encoding="utf-8") as file:
            hooks = file.read()
    # Add the proxy and hooks to the context
    await page.context.add_init_script(hooks)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame != page.main_frame:
            return
        try:
            await cdpUtils.enable_events(cdp_session)
            await cdpUtils.set_breakpoints(cdp_session)
            await cdpUtils.event_listener_events(cdp_session)
            await page.context.add_init_script(hooks)
        except Exception as e:
            print(f"{yellowColour}[!]{endColour}{grayColour} re-arm after navigation skipped: {e}{endColour}")
    
    # Calling get_targets at the beginning of the program
    targets = await cdp_session.send("Target.getTargets")
    cdpUtils.get_targets(targets)

    # Call CDP functions
    cdpUtils.target_events(cdp_session)
    cdpUtils.page_events(cdp_session)
    cdpUtils.network_events(cdp_session)
    cdpUtils.execution_context_events(cdp_session)
    cdpUtils.script_events(cdp_session)
    cdpUtils.DOM_events(cdp_session)
    cdpUtils.paused_events(cdp_session)

    page.on("framenavigated", on_frame_navigated)

    # Navigation activities
    await actions_on_web(page, canaries)
    # Stop re-arming on navigation before teardown to avoid closed-target errors
    try:
        page.remove_listener("framenavigated", on_frame_navigated)
    except Exception:
        pass

    # We used a try to avoid errors when closing the context
    await asyncio.sleep(2)
    
    try:
        await context.close()
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour}{e}{endColour}")

    # Delete user data
    fileUtils.remove_user_data()

    # Generation of the json report
    await cdpUtils.generate_json_report(False)

    # Generation of Web Graph
    create_graph(cdpUtils.report_json, False, None)

#--------------------------- MAIN FUNCTION CALL --------------------------

def _suppress_target_closed(loop, context) -> None:
    """
    Loop-level exception handler. When the context closes, Playwright rejects every
    in-flight CDP send with TargetClosedError; those rejections are dispatched by
    pyee straight into the event loop (not through our try/except), producing a wall
    of 'exception was never retrieved' tracebacks at shutdown. They are benign
    teardown noise, so we drop them here and defer everything else to the default
    handler.
    """
    exc = context.get("exception")
    if exc is not None and type(exc).__name__ == "TargetClosedError":
        return
    loop.default_exception_handler(context)


async def main(extension_path: str, selected_output_dir: str):
    # Make sure the output directory for generated files exists
    paths.ensure_output_dir()

    # Silence benign TargetClosedError teardown noise from in-flight CDP sends.
    asyncio.get_running_loop().set_exception_handler(_suppress_target_closed)

    # Generate one canary set per run and persist it
    canaries = CanarySet.new()
    canaries.save(paths.get_output_path())
    if selected_output_dir:
        canaries.save(selected_output_dir)
    print(f"{greenColour}[+]{endColour}{grayColour} Canaries seeded for this run{endColour}")

    # We start a local page as a testing web
    php_server = subprocess.Popen(
        ["php", "-S", "127.0.0.1:8080", "-t", paths.get_web_page_dir()],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )

    try:
        async with async_playwright() as playwright:
            await run(playwright, extension_path, selected_output_dir, canaries)
            await run_without_extension(playwright, canaries)
        graph_diff(selected_output_dir)

    finally:
        print("acabando servidor php")
        php_server.terminate()