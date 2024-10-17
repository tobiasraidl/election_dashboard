import networkx as nx
import pandas as pd

class PlatformGraph:
    
    def __init__(self, df):
        self.df = df
        self.G = self.__create_graph()
        
    def _filter_df(self):
        hash_platforms_counts = self.df.groupby('hash')['platform'].nunique()
        valid_hashes = hash_platforms_counts[hash_platforms_counts >= 3].index
        return self.df[self.df['hash'].isin(valid_hashes)]
        
    def __create_graph(self):
        filtered_df = self._filter_df()
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
    