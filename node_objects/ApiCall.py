"""
AUTOR: David Martín Castro
This script contains the ApiCallsNode class, which is used to represent api call nodes in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class ApiCallNode:

    # Constructor definition
    def __init__(self, apiCall: str, scriptID: str, timestamp: int) -> None:

        self.nodeType = "apiCall"
        self.apiCall = apiCall
        self.scriptID = "script" + scriptID
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        apiCall_str = f"Node {self.nodeType}:\n\
            \t- apiCall: {self.apiCall}\n\
            \t- scriptID: {self.scriptID}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return apiCall_str
    
    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "apiCall": self.apiCall,
            "scriptID": self.scriptID,
            "timestamp": self.timestamp
        }

        return dict