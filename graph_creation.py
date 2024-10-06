import networkx as nx
import pandas as pd
import numpy as np

def load_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["hash"]).reset_index()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    
    values = ["afd", "spd", "grüne", "linke", "cdu", "fdp", "linke", "unknown"]
    df["party"] = np.random.choice (values, size=len(df))
    party_color_map = {
        "afd": "blue",
        "spd": "red",
        "grüne": "green",
        "linke": "purple",
        "cdu": "black",
        "fdp": "yellow",
        "unknown": "gray" 
    }
    df['color'] = df['party'].map(party_color_map)
    
    return df

def create_graph(df, min_threshold):
    # Create a NetworkX graph based on the relationships (user_id, hash)
    G = nx.Graph()

    # Add nodes and edges
    for _, group in df.groupby('hash'):
        users = group['user_id'].tolist()
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                G.add_edge(users[i], users[j])
                
    for _, row in df.iterrows():
        if row["user_id"] in G and G.degree[row["user_id"]] >= min_threshold:
            G.nodes[row["user_id"]]["name"] = row["name"]
            G.nodes[row["user_id"]]["party"] = row["party"]
            G.nodes[row["user_id"]]["color"] = row["color"]
                
    return G

def query_nodes_with_min_deg(G, min_degree):
    return [node for node, degree in dict(G.degree()).items() if degree > min_degree]

# def get_coords(G):
#     pos = nx.spring_layout(G, center=[0, 0], scale=500, k=10)
#     return pos

# # For dynamic layout calculation on every threshold change
# def get_coords_of_subgraph(G, min_degree):
#     relevant_nodes = query_nodes_with_min_deg(G, min_degree)
#     subgraph = G.subgraph(relevant_nodes)
#     return get_coords(subgraph)