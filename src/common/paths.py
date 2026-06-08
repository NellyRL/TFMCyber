"""
AUTOR: David Martín Castro
This script is used to find and create the paths we need in the program.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import os

#---------------------------- PATH CREATION ------------------------------

def get_actual_path() -> str:

    """
    Returns the current working directory path.

    This function utilizes the os module to obtain the absolute path
    of the current working directory where the script is executed.
    """

    actual_path = os.getcwd()
    return actual_path

#---------------------------- OUTPUT DIRECTORY ---------------------------

def get_output_path() -> str:

    """
    Returns the path of the output directory, where all the files generated
    during an execution are stored.
    """

    actual_path = get_actual_path()
    output_path = actual_path + "\\output"

    return output_path

def ensure_output_dir() -> None:

    """
    Creates the output directory (and the captures sub-directory) if they do
    not exist yet.
    """

    os.makedirs(get_output_path(), exist_ok=True)
    os.makedirs(get_captures_path(), exist_ok=True)

def get_captures_path() -> str:

    """
    Returns the path of the captures directory inside output, where mitmproxy
    flow files (.flow) for a capture session are stored.
    """

    captures_path = get_output_path() + "\\captures"

    return captures_path

#---------------------------- GENERATED FILES ----------------------------

def get_report_path() -> str:

    """
    Returns the path where the report.json file will be stored.
    """
    report_path = get_output_path() + "\\report.json"

    return report_path

def get_report_without_extension_path() -> str:

    """
    Returns the path where the report_without_extension.json file will be stored.
    """
    report_path = get_output_path() + "\\report_without_extension.json"

    return report_path

def get_user_data_path() -> str:

    """
    Returns the path where the navegation user data will be stored.
    """

    user_data_path = get_output_path() + "\\user_data_dir"

    return user_data_path

def get_extension_path() -> str:

    """
    Return the path where the extension is stored.
    """

    extension_path = get_output_path() + "\\chrome-extension-directory"

    return extension_path

def get_webgraph_path() -> str:

    """
    Returns the path where the webGraph.gexf file (with extension) will be stored.
    """
    webgraph_path = get_output_path() + "\\webGraph.gexf"

    return webgraph_path

def get_webgraph_without_extension_path() -> str:

    """
    Returns the path where the webGraphWithoutExtension.gexf file will be stored.
    """
    webgraph_path = get_output_path() + "\\webGraphWithoutExtension.gexf"

    return webgraph_path

#---------------------------- STATIC RESOURCES ---------------------------

def get_hooks_path() -> str:

    """
    Returns the path of the hooks.js file injected into the browser.
    """
    hooks_path = get_actual_path() + "\\src\\capture\\hooks.js"

    return hooks_path

def get_web_page_dir() -> str:

    """
    Returns the path of the local test web page served during the analysis.
    """
    web_page_dir = get_actual_path() + "\\assets\\web_page"

    return web_page_dir

#---------------------------- OFFLINE DATA -------------------------------

def get_model_path() -> str:

    """
    Returns the path of the trained GNN model.
    """
    model_path = get_actual_path() + "\\data\\models\\gnn_model.pth"

    return model_path

def get_attr_names_path() -> str:

    """
    Returns the path of the pickled list of node attribute names.
    """
    attr_names_path = get_actual_path() + "\\data\\models\\attr_names.pkl"

    return attr_names_path

def get_graphs_dir() -> str:

    """
    Returns the path of the directory that contains the training graphs.
    """
    graphs_dir = get_actual_path() + "\\data\\graphs"

    return graphs_dir
