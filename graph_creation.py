import networkx as nx
import pandas as pd
import numpy as np

def load_data(file_path, config):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["hash"]).reset_index()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    
    values = ["afd", "spd", "grüne", "linke", "cdu", "fdp", "linke", "unknown"]
    df["party"] = np.random.choice (values, size=len(df))
    
    party_color_map = {
        "afd":      config["party_color_map"]["afd"],     # Light Blue
        "spd":      config["party_color_map"]["spd"],     # Light Red
        "grüne":    config["party_color_map"]["gruene"],   # Light Green
        "linke":    config["party_color_map"]["linke"],   # Thistle (Light Purple)
        "cdu":      config["party_color_map"]["cdu"],     # Gray (Light Black)
        "fdp":      config["party_color_map"]["fdp"],     # Light Yellow
        "unknown":  config["party_color_map"]["unknown"]  # Light Gray
    }
    df['color'] = df['party'].map(party_color_map)
    return df

def create_people_graph(df):
    # Create a NetworkX graph based on the relationships (user_id, hash)
    G = nx.Graph()

    # Add nodes and edges
    for _, group in df.groupby('hash'):
        users = group['user_id'].tolist()
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                if users[i] != users[j]:  # Check to avoid self-loops
                    G.add_edge(users[i], users[j])
                
    # for _, row in df.iterrows():
    #     G.nodes[row["user_id"]]["name"] = row["name"]
    #     G.nodes[row["user_id"]]["party"] = row["party"]
    #     G.nodes[row["user_id"]]["color"] = row["color"]
            
    return G

# min_cluster size is the minimum it will ever be retreived
def create_cluster_graph(G_people, min_cluster_size):
    all_clusters = list(nx.find_cliques(G_people))
    
    clusters = [cluster for cluster in all_clusters if len(cluster) >= min_cluster_size]
    clusters_mapping = enumerate(clusters)
    print("# relevant clusters", len(clusters), "of", len(all_clusters))
    
    G_clusters = nx.Graph()
    for i, cluster in clusters_mapping:
        G_clusters.add_node(i, nodes=cluster, size=len(cluster))
    
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            cluster_a = clusters[i]
            cluster_b = clusters[j]
            
            if any(nx.has_path(G_people, node_a, node_b) for node_a in cluster_a for node_b in cluster_b):
                G_clusters.add_edge(i, j)
                
    
    print(len(G_clusters.nodes()), len(G_clusters.edges()))
    return G_clusters
    
def query_clusters_by_min_size(G_clusters, min_cluster_size):
    relevant_clusters = []
    for i, cluster in enumerate(G_clusters):
        if len(G_clusters[i]["nodes"]) >= min_cluster_size:
            relevant_clusters.append(cluster)
    return relevant_clusters