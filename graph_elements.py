from graph_creation import query_nodes_with_min_deg

# min_deg: number between 100 and 200; all nodes with lower degree are ignored
def generate_elements(G, min_deg):
    
    relevant_nodes = query_nodes_with_min_deg(G, min_deg)
    H = G.subgraph(relevant_nodes).copy()
    
    elements = []
    for node in H.nodes():
        node_info = H.nodes[node]
        elements.append({
            'data': {'id': str(node), 'name': node_info["name"], "party": node_info["party"]}, 
            'style': {"backgroundColor": node_info["color"]}
        })
        
    # relevant_edges = [(u, v) for u, v in H.edges() if u in relevant_nodes and v in relevant_nodes]
    for edge in H.edges():
        elements.append({
            'data': {'source': str(edge[0]), 'target': str(edge[1])}
        })
    
    return elements
