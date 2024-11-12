from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html


def register_account_network_callbacks(df, config, account_graph):
    
    @callback(
        Output("account-graph", "elements"),
        [
            Input("min-same-imgs-shared-slider", "value"),
            Input("party-filter-checklist-col1", "value"),
            Input("party-filter-checklist-col2", "value"),
            Input("highlight-cross-party-connections-toogle", "value")
        ],
        prevent_initial_call=True
    )
    def update_elements(min_same_imgs_shared, selected_parties_1, selected_parties_2, cross_party_connections_toggle):
        elements = account_graph.gen_cytoscape_elements(
            min_same_imgs_shared = min_same_imgs_shared, 
            parties = selected_parties_1 + selected_parties_2, 
            highlight_cross_party_connections = len(cross_party_connections_toggle) != 0
        )
        return elements