"""
AUTOR: David Martín Castro
This script is used to create node timestamps.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import time

#------------------------------ GLOBAL VARIABLES -------------------------

start_time = 0

#------------------------------- TIME FUNCTIONS --------------------------

def get_current_time() -> float:

    """Returns the current time in seconds."""
    current_time = time.time()
    return current_time

def generate_timestamp() -> int:

    """Generates a timestamp in milliseconds."""
    current_time = time.time()
    timestamp = int((current_time - start_time) * 1000)
    return timestamp