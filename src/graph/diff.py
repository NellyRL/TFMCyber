import networkx as nx

from src.common import paths


def graph_diff(selected_output_dir):
    # Load the graphs
    G1 = nx.read_gexf(paths.get_webgraph_without_extension_path())
    G2 = nx.read_gexf(paths.get_webgraph_path())

    # Creating a new graph
    G_diff = nx.Graph()

    # Nodes in G2 and not in G1
    for node in G2.nodes:
        if node not in G1:
            G_diff.add_node(node, **G2.nodes[node])

    # Edges in G2 and not in G1
    for u, v in G2.edges:
        if not G1.has_edge(u, v):
            for node in (u, v):
                if node not in G_diff:
                    G_diff.add_node(node, **G2.nodes[node])
            G_diff.add_edge(u, v, **G2.edges[u, v])

    # Save the graph
    nx.write_gexf(G_diff, selected_output_dir + "\webGraphDiff.gexf")
