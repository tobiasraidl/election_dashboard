from utils.accounts_network_graph_creation import query_clusters_by_min_size
import networkx as nx
import itertools
import pandas as pd

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
                'width': 1
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
    
    for path in shortest_paths:
        previous_node = None
        for node in path:
            elements.append({
                'data': {'id': node, 'name': G_accounts.nodes[node]["name"], 'party': G_accounts.nodes[node]["party"]},
                'style': {'backgroundColor': config["party_color_map"][G_accounts.nodes[node]["party"]]}, 
            })
            if previous_node != None:
                elements.append({'data': {'source': str(previous_node), 'target': str(node)}, 'style': {'width': 1}})
            previous_node = node
        # Connect cluster_1 id with all first nodes in path and all last nodes with cluster_2 id
        elements.append({
            'data': {'source': f'cluster-left', 'target': path[0]}, 
            'style': {'width': 1}
        })
        elements.append({
            'data': {'source': path[-1], 'target': f'cluster-right'}, 
            'style': {'width': 1}
        })
    
    return elements

def generate_cluster_inspection_graph_elements(accounts, df):
    # print(accounts)
    # grouped = df.groupby('user_id')
    # for (key1, row1), (key2, row2) in itertools.combinations(grouped, 2):
    #     print(key1, key2)

    filtered_df = df[df['user_id'].isin(accounts)]
    merged = filtered_df.merge(df, on='hash')

    # Filter out pairs where user_id_x >= user_id_y to avoid duplicate pairs and self-pairs
    filtered = merged[merged['user_id_x'] < merged['user_id_y']]

    # Group by (user_id_x, user_id_y) and count occurrences of each pair
    result = filtered.groupby(['user_id_x', 'user_id_y']).size().reset_index(name='shared_hash_count')
    result = result.sort_values(by='shared_hash_count')
    elements = [
        {'data': {'id': 'A', 'label': 'Node A'}, 'position': {'x': 50, 'y': 50}},
        {'data': {'id': 'B', 'label': 'Node B'}, 'position': {'x': 150, 'y': 150}},
        {'data': {'id': 'C', 'label': 'Node C'}, 'position': {'x': 250, 'y': 250}},
        {'data': {'source': 'A', 'target': 'B'}},
        {'data': {'source': 'B', 'target': 'C'}}
    ]
    
    print(result)
    return elements