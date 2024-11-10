import networkx as nx
import pandas as pd
from itertools import combinations
from datetime import datetime
from collections import defaultdict

class AccountsGraph:
    
    def __init__(self, df, config):
        self.df = df
        self.G = self.__create_graph()
        self.config = config
        
    # def __create_graph(self):
    #     G = nx.Graph()
        
    #     # Group by 'hash' to identify which users have shared the same image
    #     image_groups = self.df.groupby('hash')['user_id'].apply(list)
        
    #     # Loop over each group of users that shared the same image
    #     for users in image_groups:
    #         # Create edges between all user pairs in this group
    #         for i in range(len(users)):
    #             for j in range(i + 1, len(users)):
    #                 u1, u2 = users[i], users[j]
    #                 if G.has_edge(u1, u2):
    #                     # If edge already exists, increment the weight
    #                     G[u1][u2]['weight'] += 1
    #                 else:
    #                     # If edge does not exist, create it with weight 1
    #                     if u1 != u2:
    #                         G.add_edge(u1, u2, weight=1)
        
    #     return G
    
    def __create_graph(self):
        # Initialize a graph
        G = nx.Graph()

        # Create a dictionary to count shared images between user pairs
        image_shares = defaultdict(lambda: defaultdict(int))

        # Populate the dictionary with shared images
        for _, row in self.df.iterrows():
            user_id = row['user_id']
            image_hash = row['hash']
            # Add the user to the graph (if not already added)
            if user_id not in G:
                G.add_node(user_id, party=row['party'])

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
                    G.add_edge(user1, user2, weight=weight)
        return G

    def gen_cytoscape_elements(self, min_same_imgs_shared=1):
        # Filter out edges with weight < min_same_imgs_shared
        edges_to_keep = [(u, v) for u, v, data in self.G.edges(data=True) if data['weight'] >= min_same_imgs_shared]
        filtered_graph = self.G.edge_subgraph(edges_to_keep)
        
        # Get subgraph that filters out nodes with deg<0
        nodes_with_edges = [node for node, degree in filtered_graph.degree() if degree > 0]
        filtered_graph = filtered_graph.subgraph(nodes_with_edges)

        
        # Convert the nodes of the network into the Cytoscape format
        nodes = []
        for node in filtered_graph.nodes():
            nodes.append({
                'data': {'id': node}, 
                'style': {'background-color': self.config["party_color_map"][filtered_graph.nodes[node]['party']]}
            })

        # Convert the edges of the network into the Cytoscape format
        edges = []
        for u1, u2 in filtered_graph.edges():
            if filtered_graph[u1][u2]['weight'] >= min_same_imgs_shared:
                edges.append({
                    'data': {'source': u1, 'target': u2, 'weight': filtered_graph[u1][u2]['weight']}, 
                    'style': {
                        'opacity': filtered_graph[u1][u2]['weight']/10,
                        'width': 3,
                    }
                })

        return nodes + edges