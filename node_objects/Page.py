"""
AUTOR: David Martín Castro
This script contains the PageNode class, which is used to represent a page node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class PageNode:

    # Constructor definition
    def __init__(self, pageID: str, frameID: str, url: str, loaderID: str, timestamp: int) -> None:
        self.nodeType = "page"
        self.pageID = pageID
        self.frameID = frameID
        self.url = url
        self.loaderID = loaderID
        self.timestamp = timestamp

    # str method definition, used to print the object
    def __str__(self) -> str:

        page_str = f"Node {self.nodeType}:\n\
            \t- pageID: {self.pageID}\n\
            \t- frameID: {self.frameID}\n\
            \t- url: {self.url}\n\
            \t- loaderID: {self.loaderID}\n\
            \t- timestamp: {self.timestamp}\n"
        
        return page_str
    
    # method used to convert the object to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "pageID": self.pageID,
            "frameID": self.frameID,
            "url": self.url,
            "loaderID": self.loaderID,
            "timestamp": self.timestamp
        }

        return dict