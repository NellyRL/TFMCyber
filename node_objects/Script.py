"""
AUTOR: David Martín Castro
This script contains the ScriptNode class, which is used to represent a script node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class ScriptNode:

    # Constructor definition
    def __init__(self, scriptID: str, url: str, executionContextID: int, type: str, initiator: str, timestamp: int) -> None:

        self.nodeType = "script"
        self.scriptID = "script" + scriptID
        self.url = url
        self.executionContextID = "executionContext" + str(executionContextID)
        self.type = type
        self.initiator = initiator
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        script_str = f"Node {self.nodeType}:\n"\
            f"\t- scriptID: {self.scriptID}\n"\
            f"\t- url: {self.url}\n"\
            f"\t- executionContextID: {self.executionContextID}\n"\
            f"\t- type: {self.type}\n"\
            f"\t- initiator: {self.initiator}\n"\
            f"\t- timestamp: {self.timestamp}\n"
            
        return script_str
    
    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "scriptID": self.scriptID,
            "url": self.url,
            "executionContextID": self.executionContextID,
            "type": self.type,
            "initiator": self.initiator,
            "timestamp": self.timestamp
        }

        return dict