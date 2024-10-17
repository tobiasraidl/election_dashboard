import networkx as nx
import pandas as pd
from itertools import combinations
from datetime import datetime

class PlatformGraph:
    
    def __init__(self, df):
        self.df = df
        self.G = self.__create_graph()
        
    def __filter_df(self):
        hash_platforms_counts = self.df.groupby('hash')['platform'].nunique()
        valid_hashes = hash_platforms_counts[hash_platforms_counts >= 3].index
        return self.df[self.df['hash'].isin(valid_hashes)]
        
    def __create_graph(self):
        filtered_df = self.__filter_df()
        G = nx.Graph()
        graph_id_mapping = {}
        grouped = filtered_df.groupby(['platform', 'hash'])
        for (platform, hash), group in grouped:
            posts = group.shape[0]
            G.add_node(f"{platform}-{hash}", platform=platform, hash=hash, posts=posts)
            
        for node1, data1 in G.nodes(data=True):
            for node2, data2 in G.nodes(data=True):
                if node1 < node2:  # Ensure each pair is considered only once (node1 < node2)
                    if data1.get('hash') == data2.get('hash'):
                        G.add_edge(node1, node2)
        return G
                
    def gen_cytoscape_elements(self):
        elements = []
        for node, data in self.G.nodes(data=True):
            color = {"fb": "blue", "ig": "red", "tw": "black"}
            elements.append({
                'data': {'id': node, 'platform': data.get('platform'), 'hash': data.get('hash'), 'posts': data.get('posts')},
                'style': {
                    'width': 20 + data.get('posts') * 2,
                    'height': 20 + data.get('posts') * 2,
                    'background-color': color[data.get('platform')]
                }
            })
            
        for u, v in self.G.edges():
            elements.append({
                'data': {'source': str(u), 'target': str(v)},
                'style': {
                    'width': 1
                }
            })
        return elements
    
    
# Generate the entire graph
# When generating cytoscape elements only send the selected timespan
class TimespanGraph:
    def __init__(self, df):
        self.df = df.groupby('hash').filter(lambda x: len(x) > 1)
        self.G = self.__create_graph()
        
    def __filter_by_timepsan(self, start, end):
        
        filtered_nodes = [n for n, data in self.G.nodes(data=True) if data['timestamp'] > start and data['timestamp'] < end]
        subgraph = self.G.subgraph(filtered_nodes)
        nodes_with_degree_0 = [node for node, degree in subgraph.degree() if degree == 0]
        subgraph = subgraph.copy()
        subgraph.remove_nodes_from(nodes_with_degree_0)
        return subgraph
        
    def __create_graph(self):
        G = nx.Graph()
        for _, row in self.df.iterrows():
            date_format = "%Y-%m-%dT%H:%M:%S" 
            timestamp = datetime.strptime(row['timestamp'], date_format)
            G.add_node(row['id_user_post'], user_id=row['user_id'], platform=row['platform'], timestamp=timestamp, party=['party'], hash=row['hash'])
        grouped = self.df.groupby(['hash'])
        i = 0
        for hash, group in grouped:
            print(i, len(grouped))
            i+=1
            for row1, row2 in combinations(group.itertuples(index=False), 2):
                G.add_edge(row1.id_user_post, row2.id_user_post)
        print(G)
        return G
                
    # start and end need to be in datetime format
    def gen_cytoscape_elements(self, start, end):
        subgraph = self.__filter_by_timepsan(start, end)
        elements = []
        for node, data in subgraph.nodes(data=True):
            color = {"fb": "blue", "ig": "red", "tw": "black"}
            elements.append({
                'data': {
                    'id': node, 
                    'user_id': data.get('user_id'), 
                    'platform': data.get('platform'), 
                    'timestamp': data.get('timestamp'),
                    'party': data.get('party'),
                    'hash': data.get('hash'),
                },
                'style': {
                    'background-color': color[data.get('platform')]
                }
            })
            
        for u, v in subgraph.edges():
            elements.append({
                'data': {'source': str(u), 'target': str(v)},
                'style': {
                    'width': 1
                }
            })
        return elements