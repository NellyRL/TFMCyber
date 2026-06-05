"""
AUTOR: David Martín Castro
This script contains the ExecutionContextNode class, which is used to represent a
execution context node in the graph
"""

#-------------------------------------- CLASS DEFINITION ---------------------------------

class ExecutionContextNode:

    # Constructor definition
    def __init__(self, executionContextID: int, origin: str, pageID: str, name: str, type: str, frameID: str, timestamp: int) -> None:

        self.nodeType = "executionContext"
        self.executionContextID = "executionContext" + str(executionContextID)
        self.origin = origin
        self.pageID = pageID
        self.name = name
        self.type = type
        self.frameID = frameID
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        executionContext_str = f"Node {self.nodeType}:\n\
            \t- executionContextID: {self.executionContextID}\n\
            \t- pageID: {self.pageID}\n\
            \t- origin: {self.origin}\n\
            \t- name: {self.name}\n\
            \t- type: {self.type}\n\
            \t- frameID: {self.frameID}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return executionContext_str

    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "executionContextID": self.executionContextID,
            "origin": self.origin,
            "pageID": self.pageID,
            "name": self.name,
            "type": self.type,
            "frameID": self.frameID,
            "timestamp": self.timestamp
        }
        
        return dict
