"""
AUTOR: David Martín Castro
This script contains the NetworkNode class, which is used to represent a network node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class NetworkNode:

    # Constructor definition
    def __init__(self, requestID: str, senderUrl: str, targetUrl: str, frameID: str, initiator: str, timestamp: int) -> None:

        self.nodeType = "network"
        self.requestID = requestID
        self.senderUrl = senderUrl
        self.targetUrl = targetUrl
        self.frameID = frameID
        self.initiator = initiator
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        network_str = f"Node {self.nodeType}:\n\
            \t- requestID: {self.requestID}\n\
            \t- senderUrl: {self.senderUrl}\n\
            \t- targetUrl: {self.targetUrl}\n\
            \t- frameID: {self.frameID}\n\
            \t- initiator: {self.initiator}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return network_str
    
    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "requestID": self.requestID,
            "senderUrl": self.senderUrl,
            "targetUrl": self.targetUrl,
            "frameID": self.frameID,
            "initiator": self.initiator,
            "timestamp": self.timestamp
        }
        
        return dict