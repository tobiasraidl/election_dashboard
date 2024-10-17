import networkx as nx
import pandas as pd

class PlatformGraph:
    
    def __init__(self, df):
        self.df = df
        self.G = self._create_graph()
        
    def _filter_df(self):
        hash_platforms_counts = self.df.groupby('hash')['platform'].nunique()
        valid_hashes = hash_platforms_counts[hash_platforms_counts >= 3].index
        return self.df[self.df['hash'].isin(valid_hashes)]
        
    def _create_graph(self):
        filtered_df = self._filter_df()
        G = nx.Graph()
        graph_id_mapping = {}
        for i, row in self.filtered_df.iterrows():
            graph_id_mapping['id_user_post'] = i
            G.add_node(i, platform=)
            # TODO: iterate through all use posts and aggregate posts where hash is same AND platform is same
        return G
                
    def gen_cytoscape_elements(self):
        return {}
    