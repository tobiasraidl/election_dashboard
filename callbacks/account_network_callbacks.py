from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html, ctx, ALL, MATCH
import dash_bootstrap_components as dbc
from utils.image_loader import generate_image_grid
from utils.helper import create_image_details_items
import dash

def register_account_network_callbacks(df, df_base_posts, config, account_graph):
    
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
            dbc.Alert([html.B("Cross Party Partisan"), html.P(f"This account has shared the same image as {num_cross_party_connections} accounts with different party affiliations.")], color="dark") if num_cross_party_connections != 0 else [],
            html.H5(f"Account Name: {account_name}"),
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
        element = dbc.CardBody([
            html.P(["This edge connects ", html.B(acc1_name), " and ", html.B(acc2_name)]),
            html.P(f"The following {num_same_shared_imgs} image(s) where shared by both."),
            # generate_image_grid(same_shared_images)
        ] + generate_image_grid(same_shared_images))
            # element = generate_image_grid(same_shared_images)
        return element
    
    @callback(
        [
            Output('image-details-account-page', 'is_open'),
            Output('image-timeline-account-page', 'figure'),
            Output("image-details-text-account-page", "children"),
            Output("image-party-ratios-account-page", "figure"),
            Output("image-details-image-account-page", "src")
        ],
        State('image-details-account-page', 'is_open'),
        Input({"type": "image", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def display_img_details(is_open, n_clicks):
        if not any(n_clicks):  # No image has been clicked
            return is_open, dash.no_update, [], {}, 'assets/placeholder.jpg'
        else: 
            triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]
            img_hash = triggered_input.split('"')[3]
            
            fig_timeline_plot, image_details_text, fig_party_ratios, img_data = create_image_details_items(df_base_posts, config, img_hash)
            return True, fig_timeline_plot, image_details_text, fig_party_ratios, img_data
        
    
    # @callback(
    #     [Output('image-details', 'is_open'),
    #      Output('image-timeline', 'figure'),
    #      Output('image-details-text', 'children'),
    #      Output('image-party-ratios', 'figure'),
    #      Output('image', 'src')],
    #     #  Input('bar-chart', 'clickData'),
    #     # [State('image-details', 'is_open'),
    #     #  State('df-k-most-freq-hashes', 'data'),
    #     #  State('config-store', 'data')]
    # )
    # def toggle_modal(clickData, is_open, df_dict, config):
    #     pass