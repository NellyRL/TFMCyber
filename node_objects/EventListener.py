"""
AUTOR: David Martín Castro
This script contains the EventListenersNode class, which is used to represent an event listener node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class EventListenerNode:

    def __init__(self, type: str, useCapture: bool, once: bool, scriptID: str, timestamp: int) -> None:

        self.nodeType = "eventListener"
        self.type = type
        self.useCapture = useCapture
        self.once = once
        self.scriptID = "script" + scriptID
        self.timestamp = timestamp

    # str method, used to print the node
    def __str__(self) -> str:

        eventListener_str = f"Node {self.nodeType}:\n"\
            f"\t- type: {self.type}\n"\
            f"\t- useCapture: {self.useCapture}\n"\
            f"\t- once: {self.once}\n"\
            f"\t- scriptID: {self.scriptID}\n"\
            f"\t- timestamp: {self.timestamp}\n"
        
        return eventListener_str
    
    # to_dict method, used to convert the node to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "type": self.type,
            "useCapture": self.useCapture,
            "once": self.once,
            "scriptID": self.scriptID,
            "timestamp": self.timestamp
        }

        return dict