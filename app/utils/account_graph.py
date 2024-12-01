import json
import os
import networkx as nx
import pandas as pd
from itertools import combinations
from datetime import datetime
from collections import defaultdict
import numpy as np
from fa2_modified import ForceAtlas2

class AccountGraph:
    
    def __init__(self, df, config):
        self.df = df
        self.G = self.__create_graph()
        self.config = config
    
    def __create_graph(self):
        # Initialize a graph
        G = nx.Graph()

        # Create a dictionary to count shared images between user pairs
        image_shares = defaultdict(lambda: defaultdict(int))

        accs_img_hashes = self.df.groupby('user_id')['hash'].apply(list).to_dict()
        party_affiliations = pd.Series(self.df.party.values, index=self.df.user_id).to_dict()
        
        # Populate the dictionary with shared images
        for _, row in self.df.iterrows():
            user_id = row['user_id']
            image_hash = row['hash']
            # Add the user to the graph (if not already added)
            if user_id not in G:
                G.add_node(user_id, name=row['name'], party=row['party'], img_hashes=accs_img_hashes.get(user_id, []), num_posts=len(accs_img_hashes.get(user_id, [])))
        
        for node1, node2 in combinations(G.nodes, 2):
            # Get the hashes of each node
            hashes1 = set(G.nodes[node1]["img_hashes"])
            hashes2 = set(G.nodes[node2]["img_hashes"])

            # Find the common hashes
            common_hashes = hashes1.intersection(hashes2)

            # If there are common hashes, add an edge with weight equal to the number of common hashes
            if common_hashes:
                cross_party = party_affiliations[node1] != party_affiliations[node2]
                G.add_edge(node1, node2, weight=len(common_hashes), cross_party=cross_party)
        
        return G
    
    def get_G(self):
        return self.G

    # parties ... Array of strings. values can include any of the parties defined in the config file; if None -> all parties
    # iterations ... 50 to 100 -> lower is faster but higher is better looking layout
    # highlight_cross_party_connections ... If True highlights edges that connect accounts affilliated to different parties
    # element_list_path ... loads pre-calculated elements list instead of generating new ()
    def gen_cytoscape_elements(self, min_same_imgs_shared=1, parties=None, highlight_cross_party_connections=False, scaling_ratio=5.0, iterations=100, element_list_path=None):
        max_weight = max(data['weight'] for _, _, data in self.G.edges(data=True))
        max_weight_log = np.log10(max_weight)
        save_as_initial_element_list = False
        # Load json
        if element_list_path != None:
            if os.path.exists(element_list_path):
                with open(element_list_path, 'r') as file:
                    elements = json.load(file)
                    return elements
            else:
                save_as_initial_element_list = True
                
        # Filter out nodes that are not in the parties list parameter
        filtered_graph = self.G
        if parties != None:
            nodes_to_keep = [node for node, data in filtered_graph.nodes(data=True) if data['party'] in parties]
            filtered_graph = filtered_graph.subgraph(nodes_to_keep)
        
        # Filter out edges with weight < min_same_imgs_shared
        edges_to_keep = [(u, v) for u, v, data in filtered_graph.edges(data=True) if data['weight'] >= min_same_imgs_shared]
        filtered_graph = filtered_graph.edge_subgraph(edges_to_keep)
        
        # Get subgraph that filters out nodes with deg<0
        nodes_with_edges = [node for node, degree in filtered_graph.degree() if degree > 0]
        filtered_graph = filtered_graph.subgraph(nodes_with_edges)
        
        forceatlas2 = ForceAtlas2(
            outboundAttractionDistribution=True,
            linLogMode=False,
            adjustSizes=False,
            edgeWeightInfluence=1.0,
            jitterTolerance=1.0,
            barnesHutOptimize=True,
            barnesHutTheta=2,
            scalingRatio=scaling_ratio,
            strongGravityMode=False,
            gravity=1.0
        )
        positions = forceatlas2.forceatlas2_networkx_layout(filtered_graph, iterations=iterations)
        
        min_distance = 50

        # Function to check and adjust positions
        def adjust_positions(positions, min_distance):
            nodes = list(positions.keys())
            adjusted_positions = positions.copy()

            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    node_i, node_j = nodes[i], nodes[j]
                    pos_i, pos_j = adjusted_positions[node_i], adjusted_positions[node_j]
                    dist = np.linalg.norm(np.array(pos_i) - np.array(pos_j))

                    # If the nodes are too close, move them apart
                    if dist < min_distance:
                        # Calculate the direction vector
                        direction = np.array(pos_j) - np.array(pos_i)
                        direction /= np.linalg.norm(direction)  # Normalize

                        # Move nodes apart by the difference needed to achieve min_distance
                        adjustment = (min_distance - dist) / 2
                        adjusted_positions[node_i] -= direction * adjustment
                        adjusted_positions[node_j] += direction * adjustment

            return adjusted_positions

        # Adjust the positions based on the minimum distance if not enough nodes for automatic spacing
        if len(filtered_graph.nodes()) < 500:
            positions = adjust_positions(positions, min_distance)
        
        # Convert the nodes of the network into the Cytoscape format
        nodes = []
        for node in filtered_graph.nodes():
            nodes.append({
                'data': {'id': node}, 
                'position': {'x': positions[node][0], 'y': positions[node][1]},
                'style': {
                    'background-color': self.config["party_color_map"][filtered_graph.nodes[node]['party']]
                    }
            })

        # Convert the edges of the network into the Cytoscape format
        edges = []
        if highlight_cross_party_connections:
            for u1, u2 in filtered_graph.edges():
                if filtered_graph[u1][u2]['weight'] >= min_same_imgs_shared:
                    if filtered_graph[u1][u2]['cross_party']:
                        # Highlight cross party edges
                        edges.append({
                            'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                            'style': {
                                'opacity': 1,
                                'width': 20,
                                'z-index': 2,
                                'line-color': 'white',
                            }
                        })
                    else:
                        # Do not highlight cross party edges
                        edges.append({
                            'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                            'style': {
                                'opacity': (np.log10(filtered_graph[u1][u2]['weight']) / (max_weight_log/2)) + 0.5,
                                'width': 3,
                            }
                        })
        else:
            for u1, u2 in filtered_graph.edges():
                if filtered_graph[u1][u2]['weight'] >= min_same_imgs_shared:
                    edges.append({
                        'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                        'style': {
                            'opacity': (np.log10(filtered_graph[u1][u2]['weight']) / (max_weight_log/2)) + 0.5,
                            'width': 3,
                        }
                    })

        if save_as_initial_element_list:
            with open(element_list_path, 'w') as file:
                json.dump(nodes + edges, file, indent=4)  # indent=4 makes the output more readable
            
        return nodes + edges