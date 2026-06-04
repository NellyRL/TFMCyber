import os
import torch
import networkx as nx
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool
import torch.nn.functional as F
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import StratifiedKFold
from collections import Counter

# === Cargar dataset ===

assistant_dir = "graphs/assistant-extensions"
other_dir = "graphs/other-extensions"
paths_labels = []

for filename in os.listdir(assistant_dir):
    if filename.endswith(".gexf"):
        paths_labels.append((os.path.join(assistant_dir, filename), 0))

for filename in os.listdir(other_dir):
    if filename.endswith(".gexf"):
        paths_labels.append((os.path.join(other_dir, filename), 1))

def collect_all_node_attributes(paths_labels):
    attr_names = set()
    for path, _ in paths_labels:
        G = nx.read_gexf(path)
        for _, attrs in G.nodes(data=True):
            attr_names.update(attrs.keys())
    return sorted(attr_names)

def gexf_to_pyg_data(path, label, attr_names):
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
    x = (x - x.mean(dim=0)) / (x.std(dim=0) + 1e-6)  # Normalización

    edge_index = torch.tensor(list(G.edges)).t().contiguous()
    if edge_index.numel() == 0:
        edge_index = torch.empty((2, 0), dtype=torch.long)

    y = torch.tensor([label], dtype=torch.long)
    return Data(x=x, edge_index=edge_index, y=y)

# === Procesar grafos ===

attr_names = collect_all_node_attributes(paths_labels)
data_list = [gexf_to_pyg_data(path, label, attr_names) for path, label in paths_labels]
labels = [data.y.item() for data in data_list]

# === Modelo GNN con Dropout ===

class SimpleGCN(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super(SimpleGCN, self).__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(p=0.3)
        self.lin = nn.Linear(hidden_dim, 2)

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.conv2(x, edge_index))
        x = self.dropout(x)
        x = global_mean_pool(x, batch)
        return self.lin(x)

# === Cross-Validation ===

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("Distribución de clases:", Counter(labels))

accuracies = []
for fold, (train_idx, test_idx) in enumerate(skf.split(data_list, labels)):
    print(f"\n--- Fold {fold+1} ---")

    train_data = [data_list[i] for i in train_idx]
    test_data = [data_list[i] for i in test_idx]

    train_loader = DataLoader(train_data, batch_size=8, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=8)

    model = SimpleGCN(input_dim=train_data[0].x.shape[1]).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()

    def train():
        model.train()
        total_loss = 0
        for data in train_loader:
            data = data.to(device)
            optimizer.zero_grad()
            out = model(data)
            loss = criterion(out, data.y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / len(train_loader)

    def test(loader):
        model.eval()
        correct = 0
        for data in loader:
            data = data.to(device)
            out = model(data)
            pred = out.argmax(dim=1)
            correct += (pred == data.y).sum().item()
        return correct / len(loader.dataset)

    for epoch in range(1, 31):
        loss = train()
        acc = test(test_loader)
        print(f"Epoch {epoch}, Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")

    acc = test(test_loader)
    accuracies.append(acc)
    print(f"Precisión del Fold {fold+1}: {acc:.4f}")


print(f"\nPrecisión media en los 5 folds: {sum(accuracies)/len(accuracies):.4f}")

torch.save(model.state_dict(), "gnn_model.pth")
import pickle
with open("attr_names.pkl", "wb") as f:
    pickle.dump(attr_names, f)