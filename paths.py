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

def get_report_path() -> str:

    """
    Returns the path where the report.json file will be stored.
    """
    actual_path = get_actual_path()
    report_path = actual_path + "\\report.json"

    return report_path

def get_report_without_extension_path() -> str:

    """
    Returns the path where the report_without_extension.json file will be stored.
    """
    actual_path = get_actual_path()
    report_path = actual_path + "\\report_without_extension.json"

    return report_path

def get_user_data_path() -> str:

    """
    Returns the path where the navegation user data will be stored.
    """

    actual_path = get_actual_path()
    user_data_path = actual_path + "\\user_data_dir"

    return user_data_path

def get_extension_path() -> str:

    """
    Return the path where the extension is stored.
    """

    actual_path = get_actual_path()
    extension_path = actual_path + "\\chrome-extension-directory"
    
    return extension_path