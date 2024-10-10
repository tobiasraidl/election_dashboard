from graph_creation import query_clusters_by_min_size

# min_deg: number between 100 and 200; all nodes with lower degree are ignored
def generate_elements(config, G, min_size):
    
    relevant_clusters = query_clusters_by_min_size(G, min_size)
    H = G.subgraph(relevant_clusters).copy()
    
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
