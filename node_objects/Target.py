"""
AUTOR: David Martín Castro
This script contains the TargetNode class, which is used to represent a target node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class TargetNode:

    # Constructor definition
    def __init__(self, targetID: str, type: str, event: str, url: str, timestamp: int) -> None:

        self.nodeType = "target"
        self.targetID = targetID
        self.type = type
        self.event = event
        self.url = url
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        target_str = f"Node {self.nodeType}:\n\
            \t- targetID: {self.targetID}\n\
            \t- type: {self.type}\n\
            \t- event: {self.event}\n\
            \t- url: {self.url}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return target_str

    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "targetID": self.targetID,
            "type": self.type,
            "event": self.event,
            "url": self.url,
            "timestamp": self.timestamp
        }
        return dict