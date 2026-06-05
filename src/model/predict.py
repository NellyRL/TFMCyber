import sys
import torch
import networkx as nx
from torch_geometric.data import Data
import torch.nn.functional as F
import pickle

from src.common import paths
from src.model.architecture import SimpleGCN

# === Función para convertir GEXF a Data ===

def gexf_to_pyg_data(path, attr_names):
    G = nx.read_gexf(path)
    G = nx.convert_node_labels_to_integers(G)

    node_features = []
    for i in range(len(G.nodes)):
        attrs = G.nodes[i]
        feat = []
        for name in attr_names:
            val = attrs.get(name, 0.0)
            try:
                feat.append(float(val))
            except:
                feat.append(0.0)
        node_features.append(feat)

    x = torch.tensor(node_features, dtype=torch.float)
    x = (x - x.mean(dim=0)) / (x.std(dim=0) + 1e-6)

    edge_index = torch.tensor(list(G.edges)).t().contiguous()
    if edge_index.numel() == 0:
        edge_index = torch.empty((2, 0), dtype=torch.long)

    y = torch.tensor([0], dtype=torch.long)  # etiqueta dummy
    data = Data(x=x, edge_index=edge_index, y=y)
    data.batch = torch.zeros(data.num_nodes, dtype=torch.long)  # todos los nodos pertenecen al mismo grafo
    return data

# === Clasificación ===

def predict(path_gexf, model_path=None, attr_path=None):
    # Use the default data/models paths when none are provided
    if model_path is None:
        model_path = paths.get_model_path()
    if attr_path is None:
        attr_path = paths.get_attr_names_path()
    # Cargar atributos
    with open(attr_path, "rb") as f:
        attr_names = pickle.load(f)

    # Preparar datos
    data = gexf_to_pyg_data(path_gexf, attr_names)

    # Cargar modelo
    model = SimpleGCN(input_dim=len(attr_names))
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()

    # Clasificar
    with torch.no_grad():
        output = model(data)
        pred = output.argmax(dim=1).item()
        prob = F.softmax(output, dim=1).squeeze().tolist()

    clase = "assistant" if pred == 0 else "other"
    print(f"Archivo: {path_gexf}")
    print(f"Predicción: {clase}")
    print(f"Probabilidades: assistant={prob[0]:.4f}, other={prob[1]:.4f}")
    return clase, round(prob[0], 4), round(prob[1], 4)
