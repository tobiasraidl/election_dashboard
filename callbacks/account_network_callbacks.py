from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html, ctx
import dash_bootstrap_components as dbc
from utils.image_loader import generate_image_grid


def register_account_network_callbacks(df, config, account_graph):
    
    @callback(
        Output("account-graph", "elements"),
        [
            State("min-same-imgs-shared-slider", "value"),
            State("party-filter-checklist-col1", "value"),
            State("party-filter-checklist-col2", "value"),
            State("highlight-cross-party-connections-toogle", "value"),
            State("iteration-slider", "value"),
            State("k-slider", "value")
        ],
        Input("apply-button", "n_clicks"),
        prevent_initial_call=True
    )
    def update_elements(min_same_imgs_shared, selected_parties_1, selected_parties_2, cross_party_connections_toggle, iterations, k, n_clicks):
        elements = account_graph.gen_cytoscape_elements(
            min_same_imgs_shared = min_same_imgs_shared, 
            parties = selected_parties_1 + selected_parties_2,
            iterations = iterations,
            k=k,
            highlight_cross_party_connections = len(cross_party_connections_toggle) != 0,
        )
        return elements
    
    @callback(
        Output("on-click-output-card", "children", allow_duplicate=True),
        [Input("account-graph", "tapNodeData")],
        prevent_initial_call=True
    )
    def display_node_details(tap_node_data):
        G = account_graph.get_G()
        user_id = tap_node_data['id']
        node = G.nodes[user_id]
        account_name = node['name']
        account_party = node['party']
        account_num_posts = node['num_posts']
        account_num_neighbors = G.degree(user_id)
        
        neighbors = G.neighbors(user_id)
        num_cross_party_connections = sum(1 for neighbor in neighbors if G.nodes[neighbor].get("party") != account_party)
        
        element = dbc.CardBody([
            html.H5(account_name),
            dbc.Alert(f"This account has shared the same image as {num_cross_party_connections} accounts with different party affiliations.") if num_cross_party_connections != 0 else [],
            html.P([f"Party affiliation: ", html.Strong(account_party)]),
            html.P([f"Images posted: ", html.Strong(account_num_posts)]),
            html.P([f"Num. accounts that shared same images: ", html.Strong(account_num_neighbors)]),
            dbc.FormText(
                "Account details are not influenced by the graph view settings above.",
                style={"fontSize": "0.9rem", "color": "#A0A0A0"}
            ),
        ])
            
        return element
        
    @callback(
        Output("on-click-output-card", "children", allow_duplicate=True),
        [Input("account-graph", "tapEdgeData")],
        prevent_initial_call=True
    )
    def display_edge_details(tap_edge_data):
        G = account_graph.get_G()
        
        user1_id = tap_edge_data['source']
        acc1_node = G.nodes[user1_id]
        acc1_name = acc1_node['name']
        
        user2_id = tap_edge_data['target']
        acc2_node = G.nodes[user2_id]
        acc2_name = acc2_node['name']
        
        same_shared_images = list(set(acc1_node['img_hashes']) & set(acc2_node['img_hashes']))
        num_same_shared_imgs = len(same_shared_images)
        
        element = generate_image_grid(same_shared_images)
        return element
    
    # @callback(
    #     Output("on-click-output-card", "children"),
    #     [Input("account-graph", "tapNodeData"), Input("account-graph", "tapEdgeData")],
    #     prevent_initial_call=True
    # )
    # def display_click_data(tap_node_data, tap_edge_data):
    #     print(ctx)
    #     # if not ctx.triggered:
    #     #     return "No input has triggered the callback"
    #     if tap_node_data:
    #         G = account_graph.get_G()
    #         user_id = tap_node_data['id']
    #         node = G.nodes[user_id]
    #         account_name = node['name']
    #         account_party = node['party']
    #         account_num_posts = node['num_posts']
    #         account_num_neighbors = G.degree(user_id)
            
    #         neighbors = G.neighbors(user_id)
    #         num_cross_party_connections = sum(1 for neighbor in neighbors if G.nodes[neighbor].get("party") != account_party)
            
    #         element = dbc.CardBody([
    #             html.H5(account_name),
    #             dbc.Alert(f"This account has shared the same image as {num_cross_party_connections} accounts with different party affiliations.") if num_cross_party_connections != 0 else [],
    #             html.P([f"Party affiliation: ", html.Strong(account_party)]),
    #             html.P([f"Images posted: ", html.Strong(account_num_posts)]),
    #             html.P([f"Num. accounts that shared same images: ", html.Strong(account_num_neighbors)]),
    #             dbc.FormText(
    #                 "Account details are not influenced by the graph view settings above.",
    #                 style={"fontSize": "0.9rem", "color": "#A0A0A0"}
    #             ),
    #         ])
            
    #         return element
    #     elif tap_edge_data:
    #         G = account_graph.get_G()
            
    #         user1_id = tap_edge_data['source']
    #         acc1_node = G.nodes[user1_id]
    #         acc1_name = acc1_node['name']
            
    #         user2_id = tap_edge_data['target']
    #         acc2_node = G.nodes[user2_id]
    #         acc2_name = acc2_node['name']
            
    #         same_shared_images = list(set(acc1_node['img_hashes']) & set(acc2_node['img_hashes']))
    #         num_same_shared_imgs = len(same_shared_images)
            
    #         element = generate_image_grid(same_shared_images)
    #         return element
    #     return "Click node or edge for details."