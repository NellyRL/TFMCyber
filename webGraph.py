"""
AUTOR: David Martín Castro
This script create the WG (Web Graph) from the report.json created based on the navigation
events captured by CDP (Chrome DevTools Protocol).
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import networkx as nx

#--------------------------- GRAPH CREATION ------------------------------

def create_graph(report: dict, extension:bool, selected_output_dir: str):
    # Create a directed graph
    graph = nx.DiGraph()
    # Adding all the nodes to the graph
    for node in report:
        type = node["nodeType"]
        if type == "apiCall":
            graph.add_node(node["apiCall"], nodeType="apiCall", timestamp=node["timestamp"], viz={"color": {"r": 255, "g": 0, "b": 46}})
        elif type == "domElement":
            graph.add_node(node["elementID"], nodeType="domElement", type=node["type"], name=node["name"], timestamp=node["timestamp"],
                            viz={"color": {"r": 255, "g": 197, "b": 0}})
        elif type == "eventListener":
            graph.add_node(node["type"], nodeType="eventListener", type=node["type"], useCapture=node["useCapture"], once=node["once"],
                             timestamp=node["timestamp"], viz={"color": {"r": 205, "g": 255, "b": 0}})
        elif type == "executionContext":
            graph.add_node(node["executionContextID"], nodeType="executionContext", origin=node["origin"], name=node["name"], type=node["type"],
                            timestamp=node["timestamp"], viz={"color": {"r": 0, "g": 255, "b": 0}})
        elif type == "extension":
            graph.add_node(node["extensionID"],nodeType="extension", extensionID=node["extensionID"], name=node["name"], 
                           timestamp=node["timestamp"], viz={"color": {"r": 0, "g": 0, "b": 255}})
        elif type == "network":
            graph.add_node(node["requestID"], nodeType="network", requestID=node["requestID"], timestamp=node["timestamp"],
                            viz={"color": {"r": 0, "g": 255, "b": 189}})
        elif type == "page":
            graph.add_node(node["pageID"], nodeType="page", url=node["url"], timestamp=node["timestamp"],
                            viz={"color": {"r": 0, "g": 209, "b": 255}})
        elif type == "script":
            graph.add_node(node["scriptID"], nodeType="script", url=node["url"], type=node["type"], timestamp=node["timestamp"],
                            viz={"color": {"r": 255, "g": 0, "b": 143}})
        elif type == "target":
            if node["event"] == "create":
                graph.add_node(node["targetID"], nodeType="target", type=node["type"], url=node["url"], timestamp=node["timestamp"],
                                viz={"color": {"r": 144, "g": 144, "b": 144}})

    # Adding all the edges to the graph
    for node in report:
        type = node["nodeType"]
        if type == "page":
            try:
                # Add edge from target (frameID) to page
                graph.add_edge(node["frameID"], node["pageID"], label="loads")
            except Exception as e:
                print("Page edge creation error" + e)
                pass
        elif type == "executionContext":
            try:
                # Add edge from page to executionContext
                graph.add_edge(node["pageID"], node["executionContextID"], label="spawns")
            except Exception as e:
                print("Execution Context edge creation error" + e)
                pass
        elif type == "extension":
            try:
                # Add edge from executionContext to extension
                graph.add_edge(node["executionContextID"], node["extensionID"], label="belongsTo")
            except Exception as e:
                print("Extension edge creation error" + e)
                pass
        elif type == "script":
            try:
                # Add edge from executionContext to script
                graph.add_edge(node["executionContextID"], node["scriptID"], label="executes")
                if node["initiator"]:
                    graph.add_edge(node["initiator"], node["scriptID"], label="triggers")
            except Exception as e:
                print("Script edge creation error" + e)
                pass
        elif type == "domElement":
            try:
                graph.add_edge(node["initiator"], node["elementID"], label="inserts")
            except Exception as e:
                print("DOM Element edge creation error" + e)
                pass
        elif type == "apiCall":
            try:
                graph.add_edge(node["scriptID"], node["apiCall"], label="invokes")
            except Exception as e:
                print("Api Call edge creation error" + e)
                pass
        elif type == "eventListener":
            try:
                graph.add_edge(node["scriptID"], node["type"], label="attaches")
            except Exception as e:
                print("Event Listener edge creation error" + e)
                pass
        elif type == "network":
            try:
                if "page" in node["initiator"]:
                    graph.add_edge(node["senderUrl"], node["requestID"], label="initiates")
                elif "script" in node["initiator"]:
                    graph.add_edge(node["initiator"], node["requestID"], label="initiates")
                
                if "page" in node["targetUrl"]:
                    graph.add_edge(node["requestID"], node["targetUrl"], label="loads")
                else: 
                    scriptID = None
                    for node2 in report:
                        if (node2["nodeType"] == "script") and (node["targetUrl"] == node2["url"]) \
                        and (node["timestamp"] < node2["timestamp"]):
                            scriptID = node2["scriptID"]
                            graph.add_edge(node["requestID"], scriptID, label="triggers")
                            break
                    
                    if scriptID == None:
                        graph.add_edge(node["requestID"], node["targetUrl"], label="loads")
                        
            except Exception as e:
                print("Network edge creation error" + e)
                pass
            

    # Export the graph to a gexf file (for Gephi visualitation)
    if extension:
        nx.write_gexf(graph, selected_output_dir + "\webGraph.gexf")
        nx.write_gexf(graph, "webGraph.gexf")
        return graph
    else:
        nx.write_gexf(graph, "webGraphWithoutExtension.gexf")
        return graph
