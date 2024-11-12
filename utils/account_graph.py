import json
import os
import networkx as nx
import pandas as pd
from itertools import combinations
from datetime import datetime
from collections import defaultdict

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

            # Increment shared image count between pairs of users
            for _, other_row in self.df[self.df['hash'] == image_hash].iterrows():
                other_user_id = other_row['user_id']
                if user_id != other_user_id:
                    image_shares[user_id][other_user_id] += 1

        # Add edges to the graph based on shared images
        for user1, connections in image_shares.items():
            for user2, weight in connections.items():
                if G.has_edge(user1, user2):
                    # If edge exists, update weight (i.e., increment shared image count)
                    G[user1][user2]['weight'] += weight
                else:
                    # If no edge exists, create a new one with the weight (number of shared images)
                    cross_party = party_affiliations[user1] != party_affiliations[user2]
                    G.add_edge(user1, user2, weight=weight, cross_party=cross_party)
        return G
    
    def get_G(self):
        return self.G

    # parties ... Array of strings. values can include any of the parties defined in the config file; if None -> all parties
    # iterations ... 50 to 100 -> lower is faster but higher is better looking layout
    # highlight_cross_party_connections ... If True highlights edges that connect accounts affilliated to different parties
    # element_list_path ... loads pre-calculated elements list instead of generating new ()
    def gen_cytoscape_elements(self, min_same_imgs_shared=1, parties=None, highlight_cross_party_connections=False, iterations=100, k=0.2, element_list_path=None):
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
        
        positions = nx.spring_layout(filtered_graph, k=k, iterations=iterations)
        # positions = nx.kamada_kawai_layout(filtered_graph)
        # positions = nx.fruchterman_reingold_layout(filtered_graph)
        
        # Convert the nodes of the network into the Cytoscape format
        nodes = []
        for node in filtered_graph.nodes():
            nodes.append({
                'data': {'id': node}, 
                'position': {'x': positions[node][0]*5000, 'y': positions[node][1]*5000},
                'style': {
                    # 'width': f'{filtered_graph.nodes[node].get("num_posts", 10)}px',  # Ensure it's numeric with 'px'
                    # 'height': f'{filtered_graph.nodes[node].get("num_posts", 10)}px',  # Same for height
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
                                'line-color': 'white',
                            }
                        })
                    else:
                        # Do not highlight cross party edges
                        edges.append({
                            'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                            'style': {
                                'opacity': filtered_graph[u1][u2]['weight']/10,
                                'width': 3,
                            }
                        })
        else:
            for u1, u2 in filtered_graph.edges():
                if filtered_graph[u1][u2]['weight'] >= min_same_imgs_shared:
                    edges.append({
                        'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                        'style': {
                            'opacity': filtered_graph[u1][u2]['weight']/10,
                            'width': 3,
                        }
                    })

        if save_as_initial_element_list:
            with open(element_list_path, 'w') as file:
                json.dump(nodes + edges, file, indent=4)  # indent=4 makes the output more readable
            
        return nodes + edges