import networkx as nx

def create_accounts_graph(df):
    # Create a NetworkX graph based on the relationships (user_id, hash)
    G = nx.Graph()

    # Add nodes and edges
    for _, group in df.groupby('hash'):
        users = group['user_id'].tolist()
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                if users[i] != users[j]:  # Check to avoid self-loops
                    G.add_edge(users[i], users[j])
                
    for _, row in df.iterrows():
        if row["user_id"] in G:
            G.nodes[row["user_id"]]["name"] = row["name"]
            G.nodes[row["user_id"]]["party"] = row["party"]
            
    return G

# cluster needs to be a list of user_ids
def _get_party_ratio_of_cluster(G_accounts, cluster):
    parties = [G_accounts.nodes[node]['party'] for node in cluster]
    party_labels = ['afd', 'spd', 'die_gruenen', 'die_linke', 'cdu_csu', 'fdp', 'unknown']
    party_ratios = {party: 0 for party in party_labels}
    
    for party in parties:
        if party in party_ratios:
            party_ratios[party] += 1
            
    total_nodes = len(cluster)
    party_ratios = {party: (count / total_nodes) * 100 for party, count in party_ratios.items()}
    return party_ratios

# min_cluster size is the minimum it will ever be retreived
# max_connection_length is the max path length between any 2 clusters to add an edge
def create_cluster_graph(G_accounts, min_cluster_size):
    all_clusters = list(nx.find_cliques(G_accounts))
    
    clusters = [cluster for cluster in all_clusters if len(cluster) >= min_cluster_size]
    clusters_mapping = enumerate(clusters)
    # print("# relevant clusters", len(clusters), "of", len(all_clusters))
    
    G_clusters = nx.Graph()
    for i, cluster in clusters_mapping:
        G_clusters.add_node(i, 
            nodes=cluster, 
            size=len(cluster),
            party_ratios=_get_party_ratio_of_cluster(G_accounts, cluster)
        )
    
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            cluster_a = clusters[i]
            cluster_b = clusters[j]
            if any(nx.has_path(G_accounts, node_a, node_b) for node_a in cluster_a for node_b in cluster_b):
                G_clusters.add_edge(i, j)
                
    return G_clusters
    
def query_clusters_by_min_size(G_clusters, min_cluster_size):
    relevant_clusters = []
    for i, cluster in enumerate(G_clusters):
        if len(G_clusters.nodes[i]["nodes"]) >= min_cluster_size:
            relevant_clusters.append(cluster)
    return relevant_clusters
