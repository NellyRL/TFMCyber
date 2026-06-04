"""
AUTOR: David Martín Castro
This script contains the main function, which is used to run the program.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

# External modules
import asyncio
import subprocess
from playwright.async_api import async_playwright, Playwright

# Own modules
import paths
import utils.fileUtils as fileUtils
import utils.timeUtils as timeUtils
import utils.cdpUtils as cdpUtils
from webGraph import create_graph
from graph_diff import graph_diff
from utils.webActions import actions_on_web
from colours import *

#------------------------- PREVIOUS INFORMATION DELETION -----------------

print(f"{greenColour}[+]{endColour}{grayColour} Deleting previous information...{endColour}")
fileUtils.remove_report()
fileUtils.remove_user_data()

#------------------------------ MAIN FUNCTION ----------------------------

print(f"{greenColour}[+]{endColour}{grayColour} Starting program...{endColour}")
# Start time of the program
timeUtils.start_time = timeUtils.get_current_time()


async def run(playwright: Playwright, extension_path: str, selected_output_dir: str) -> None:

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
    with open("hooks.js", "r", encoding="utf-8") as file:
            hooks = file.read()
    # Add the proxy and hooks to the context
    await context.add_init_script(hooks)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame == page.main_frame:
                await cdpUtils.enable_events(cdp_session)
                await cdpUtils.set_breakpoints(cdp_session)
                await cdpUtils.event_listener_events(cdp_session)
                await context.add_init_script(hooks)
    
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
    await actions_on_web(page)

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
async def run_without_extension(playwright: Playwright) -> None:

    cdpUtils.report_json = []
    # Create a new browser context
    context = await playwright.chromium.launch(headless=False)
    
    # We will use the first page created by the browser context
    page = await context.new_page()

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
    with open("hooks.js", "r", encoding="utf-8") as file:
            hooks = file.read()
    # Add the proxy and hooks to the context
    await page.context.add_init_script(hooks)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame == page.main_frame:
                await cdpUtils.enable_events(cdp_session)
                await cdpUtils.set_breakpoints(cdp_session)
                await cdpUtils.event_listener_events(cdp_session)
                await page.context.add_init_script(hooks)
    
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
    await actions_on_web(page)

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

async def main(extension_path: str, selected_output_dir: str):
    # We start a local page as a testing web
    php_server = subprocess.Popen(
        ["php", "-S", "127.0.0.1:8080", "-t", "web_page"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )

    try:
        async with async_playwright() as playwright:
            await run(playwright, extension_path, selected_output_dir)
            await run_without_extension(playwright)
        graph_diff(selected_output_dir)

    finally:
        print("acabando servidor php")
        php_server.terminate()