"""
AUTOR: David Martín Castro
This script contains the ExtensionNode class, which is used to represent an extension node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class ExtensionNode:

    # Constructor definition
    def __init__(self, extensionID: str, executionContextID: str, name: str, timestamp: int) -> None:

        self.nodeType = "extension"
        self.extensionID = extensionID
        self.executionContextID = executionContextID
        self.name = name
        self.timestamp = timestamp

    # str method definition, used to print the node
    def __str__(self) -> str:

        extension_str = f"Node {self.nodeType}:\n\
            \t- extensionID: {self.extensionID}\n\
            \t- executionContextID: {self.executionContextID}\n\
            \t- name: {self.name}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return extension_str
    
    # method to convert the node to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "extensionID": self.extensionID,
            "executionContextID": self.executionContextID,
            "name": self.name,
            "timestamp": self.timestamp
        }
        
        return dict