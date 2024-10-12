from graph_creation import query_clusters_by_min_size
import networkx as nx

# min_deg: number between 100 and 200; all nodes with lower degree are ignored
def generate_cluster_graph_elements(config, G_clusters, min_size):
    
    relevant_clusters = query_clusters_by_min_size(G_clusters, min_size)
    H = G_clusters.subgraph(relevant_clusters).copy()
    
    elements = []
    for node in H.nodes():
        node_info = H.nodes[node]
        elements.append({
            'data': {'id': str(node), 'size': node_info["size"], 'people': node_info["nodes"], 'party_ratios': node_info["party_ratios"]},
            'style': {
                'width': node_info["size"]*2,
                'height': node_info["size"]*2,
                'background-color': f'{config["party_color_map"]["unknown"]}',
                'pie-size': '90%',
                'pie-1-background-color': config["party_color_map"]["afd"],
                'pie-1-background-size': f'{node_info["party_ratios"]["afd"]}%',
                'pie-2-background-color': config["party_color_map"]["spd"],
                'pie-2-background-size': f'{node_info["party_ratios"]["spd"]}%',
                'pie-3-background-color': config["party_color_map"]["gruene"],
                'pie-3-background-size': f'{node_info["party_ratios"]["gruene"]}%',
                'pie-4-background-color': config["party_color_map"]["linke"],
                'pie-4-background-size': f'{node_info["party_ratios"]["linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu"],
                'pie-5-background-size': f'{node_info["party_ratios"]["cdu"]}%',
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
def generate_connection_graph_elements(config, G_people, cluster1_details, cluster2_details):
    elements = [
        {
            'data': {'id': f'cluster-left', 'label': f'Cluster {cluster1_details["id"]}'},
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
                'pie-3-background-color': config["party_color_map"]["gruene"],
                'pie-3-background-size': f'{cluster1_details["party_ratios"]["gruene"]}%',
                'pie-4-background-color': config["party_color_map"]["linke"],
                'pie-4-background-size': f'{cluster1_details["party_ratios"]["linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu"],
                'pie-5-background-size': f'{cluster1_details["party_ratios"]["cdu"]}%',
                'pie-6-background-color': config["party_color_map"]["fdp"],
                'pie-6-background-size': f'{cluster1_details["party_ratios"]["fdp"]}%',
                'pie-7-background-color': config["party_color_map"]["unknown"],
                'pie-7-background-size': f'{cluster1_details["party_ratios"]["unknown"]}%',
            }
        },
        {
            'data': {'id': f'cluster-right', 'label': f'Cluster {cluster2_details["id"]}'},
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
                'pie-3-background-color': config["party_color_map"]["gruene"],
                'pie-3-background-size': f'{cluster2_details["party_ratios"]["gruene"]}%',
                'pie-4-background-color': config["party_color_map"]["linke"],
                'pie-4-background-size': f'{cluster2_details["party_ratios"]["linke"]}%',
                'pie-5-background-color': config["party_color_map"]["cdu"],
                'pie-5-background-size': f'{cluster2_details["party_ratios"]["cdu"]}%',
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
                path = nx.shortest_path(G_people, source=node1, target=node2)
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
                'data': {'id': node, 'name': G_people.nodes[node]["name"], 'party': G_people.nodes[node]["party"]},
                'style': {'backgroundColor': config["party_color_map"][G_people.nodes[node]["party"]]}, 
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