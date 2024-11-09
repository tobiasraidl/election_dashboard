from utils.accounts_network_graph_creation import query_clusters_by_min_size
import networkx as nx
import itertools
import pandas as pd
import hashlib

# min_deg: number between 100 and 200; all nodes with lower degree are ignored
def generate_cluster_graph_elements(config, G_clusters, min_size):
    
    relevant_clusters = query_clusters_by_min_size(G_clusters, min_size)
    H = G_clusters.subgraph(relevant_clusters).copy()
    
    elements = []
    for node in H.nodes():
        node_info = H.nodes[node]
        elements.append({
            'data': {'id': str(node), 'size': node_info["size"], 'accounts': node_info["nodes"], 'party_ratios': node_info["party_ratios"]},
            'style': {
                'width': node_info["size"]*2,
                'height': node_info["size"]*2,
                'background-color': f'{config["party_color_map"]["unknown"]}',
                'pie-size': '90%',
                'pie-1-background-color': config["party_color_map"]["afd"],
                'pie-1-background-size': f'{node_info["party_ratios"]["afd"]}%',
                'pie-2-background-color': config["party_color_map"]["spd"],
                'pie-2-background-size': f'{node_info["party_ratios"]["spd"]}%',
                'pie-3-background-color': config["party_color_map"]["die_gruenen"],
                'pie-3-background-size': f'{node_info["party_ratios"]["die_gruenen"]}%',
                'pie-4-background-color': config["party_color_map"]["die_linke"],
                'pie-4-background-size': f'{node_info["party_ratios"]["die_linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu_csu"],
                'pie-5-background-size': f'{node_info["party_ratios"]["cdu_csu"]}%',
                'pie-6-background-color': config["party_color_map"]["fdp"],
                'pie-6-background-size': f'{node_info["party_ratios"]["fdp"]}%',
                'pie-7-background-color': config["party_color_map"]["unknown"],
                'pie-7-background-size': f'{node_info["party_ratios"]["unknown"]}%',
            }
        })
        
    for edge in H.edges():
        elements.append({
            'data': {'source': str(edge[0]), 'target': str(edge[1])},
            'style': {
                'width': 1,
                'opacity': 0.5
            }
        })
        
    return elements

# clusters must be a tuple of size 2
def generate_connection_graph_elements(config, G_accounts, cluster1_details, cluster2_details):
    elements = [
        {
            'data': {
                'id': f'cluster-left', 
                'cluster-graph-id': cluster1_details["id"], 
                'label': f'Cluster {cluster1_details["id"]}', 
                'party_ratios': cluster1_details["party_ratios"], 
                'size': cluster1_details["size"]
            },
            'style': {
                'font-size': '50px',
                'width': cluster1_details["size"]*3,
                'height': cluster1_details["size"]*3,
                'background-color': f'{config["party_color_map"]["unknown"]}',
                'pie-size': '90%',
                'pie-1-background-color': config["party_color_map"]["afd"],
                'pie-1-background-size': f'{cluster1_details["party_ratios"]["afd"]}%',
                'pie-2-background-color': config["party_color_map"]["spd"],
                'pie-2-background-size': f'{cluster1_details["party_ratios"]["spd"]}%',
                'pie-3-background-color': config["party_color_map"]["die_gruenen"],
                'pie-3-background-size': f'{cluster1_details["party_ratios"]["die_gruenen"]}%',
                'pie-4-background-color': config["party_color_map"]["die_linke"],
                'pie-4-background-size': f'{cluster1_details["party_ratios"]["die_linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu_csu"],
                'pie-5-background-size': f'{cluster1_details["party_ratios"]["cdu_csu"]}%',
                'pie-6-background-color': config["party_color_map"]["fdp"],
                'pie-6-background-size': f'{cluster1_details["party_ratios"]["fdp"]}%',
                'pie-7-background-color': config["party_color_map"]["unknown"],
                'pie-7-background-size': f'{cluster1_details["party_ratios"]["unknown"]}%',
            }
        },
        {
            'data': {
                'id': f'cluster-right', 
                'cluster-graph-id': cluster2_details["id"], 
                'label': f'Cluster {cluster2_details["id"]}', 
                'party_ratios': cluster2_details["party_ratios"], 
                'size': cluster2_details["size"]
            },
            'style': {
                'font-size': '50px',
                'width': cluster2_details["size"]*3,
                'height': cluster2_details["size"]*3,
                'background-color': f'{config["party_color_map"]["unknown"]}',
                'pie-size': '90%',
                'pie-1-background-color': config["party_color_map"]["afd"],
                'pie-1-background-size': f'{cluster2_details["party_ratios"]["afd"]}%',
                'pie-2-background-color': config["party_color_map"]["spd"],
                'pie-2-background-size': f'{cluster2_details["party_ratios"]["spd"]}%',
                'pie-3-background-color': config["party_color_map"]["die_gruenen"],
                'pie-3-background-size': f'{cluster2_details["party_ratios"]["die_gruenen"]}%',
                'pie-4-background-color': config["party_color_map"]["die_linke"],
                'pie-4-background-size': f'{cluster2_details["party_ratios"]["die_linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu_csu"],
                'pie-5-background-size': f'{cluster2_details["party_ratios"]["cdu_csu"]}%',
                'pie-6-background-color': config["party_color_map"]["fdp"],
                'pie-6-background-size': f'{cluster2_details["party_ratios"]["fdp"]}%',
                'pie-7-background-color': config["party_color_map"]["unknown"],
                'pie-7-background-size': f'{cluster2_details["party_ratios"]["unknown"]}%',
            }
        }
    ]
    
    shortest_paths = []
    min_distance = float("inf")
    
    for node1 in cluster1_details["nodes"]:
        for node2 in cluster2_details["nodes"]:
            try:
                path = nx.shortest_path(G_accounts, source=node1, target=node2)
                # print(path)
                distance = len(path)
                if distance == min_distance:
                    shortest_paths.append(path)
                elif distance < min_distance:
                    min_distance = distance
                    shortest_paths = [path]
            except nx.NetworkXNoPath:
                continue
    
    unique_nodes = set()
    unique_edges = set()

    for path in shortest_paths:
        previous_node = None
        for node in path:
            # Add node only if it's not already in unique_nodes
            if node not in unique_nodes:
                elements.append({
                    'data': {'id': node, 'name': G_accounts.nodes[node]["name"], 'party': G_accounts.nodes[node]["party"]},
                    'style': {'backgroundColor': config["party_color_map"][G_accounts.nodes[node]["party"]]}, 
                })
                unique_nodes.add(node)  # Track node to avoid duplicates

            # Add edge only if it’s not already in unique_edges
            if previous_node is not None:
                edge = (str(previous_node), str(node))  # Define edge as a tuple of (source, target)
                if edge not in unique_edges:
                    elements.append({'data': {'source': edge[0], 'target': edge[1]}, 'style': {'width': 3}})
                    unique_edges.add(edge)  # Track edge to avoid duplicates

            previous_node = node

        # Add edges connecting to cluster nodes only if they are unique
        start_edge = (f'cluster-left', path[0])
        if start_edge not in unique_edges:
            elements.append({'data': {'source': start_edge[0], 'target': start_edge[1]}, 'style': {'width': 3}})
            unique_edges.add(start_edge)

        end_edge = (path[-1], f'cluster-right')
        if end_edge not in unique_edges:
            elements.append({'data': {'source': end_edge[0], 'target': end_edge[1]}, 'style': {'width': 3}})
            unique_edges.add(end_edge)

    return elements

# min_same_shared_images is the amount of same images two accounts need to have shared in order to display the edge
def generate_cluster_inspection_graph_elements(accounts, df, config, min_same_shared_images=1):

    filtered_df = df[df['user_id'].isin(accounts)]
    merged = filtered_df.merge(filtered_df, on='hash')
    
    # Filter out pairs where user_id_x >= user_id_y to avoid duplicate pairs and self-pairs
    filtered = merged[merged['user_id_x'] < merged['user_id_y']]
    
    # Ensure the hash column is retained
    filtered = filtered[['user_id_x', 'user_id_y', 'hash'] + [col for col in filtered.columns if col not in ['user_id_x', 'user_id_y', 'hash']]]

    # Group by (user_id_x, user_id_y) and count occurrences of each pair
    edges_df = filtered.groupby(['user_id_x', 'user_id_y'])['hash'].nunique().reset_index(name='shared_hash_count')

    edges_df = edges_df.sort_values(by='shared_hash_count')
    
    elements = []
    for account in accounts:
        acc_row = df[df['user_id'] == account].iloc[0]
        elements.append({
            'data': {'id': str(account), 'name': str(acc_row['name']), 'party': str(acc_row['party'])},
            'style': {'background-color': config["party_color_map"][acc_row['party']]}, 
        })
    edges_df = edges_df[edges_df['shared_hash_count'] >= min_same_shared_images]
    for _, row in edges_df.iterrows():
        elements.append({
            'data': {'source': str(row['user_id_x']), 'target': str(row['user_id_y']), 'weight': row['shared_hash_count']},
            'style': {
                'width': 1,
                'opacity': row['shared_hash_count'] / edges_df['shared_hash_count'].max()
            }
        })
    return elements