from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html
import pandas as pd
import dash
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from utils.platform_view_graph import PlatformGraph, TimespanGraph

def register_platform_view_callbacks(df):
    
    def gen_barchart(config, filtered_df):
        k=20
        hash_counts = filtered_df['hash'].value_counts()
        top_hashes = hash_counts.iloc[0:k]
        most_shared_images = filtered_df[filtered_df['hash'].isin(list(top_hashes.index))]
        counts = most_shared_images.groupby(['hash', 'platform'])['platform'].count()

        df_temp = counts.unstack(fill_value=0)

        fig = go.Figure()

        platform_colors = {
            'Facebook': config['platform_color_map']['Facebook'],
            'Instagram': config['platform_color_map']['Instagram'],
            'Twitter': config['platform_color_map']['Twitter']
        }

        for platform in df_temp.columns:
            fig.add_trace(go.Bar(
                x=df_temp.index,
                y=df_temp[platform],
                name=platform,
                marker_color=platform_colors[platform]
            ))

        fig.update_layout(
            barmode='stack',
            # title="Most Shared Images by Platform",
            xaxis_title="Hash",
            yaxis_title="Count",
            xaxis={'categoryorder': 'total descending'},
        )
            
        bar_chart = dcc.Graph(figure=fig, id='bar-chart')
            
        return most_shared_images.to_dict(), bar_chart
    
    @callback(
        [Output('df-k-most-freq-hashes', 'data'),
         Output('bar-chart-wrapper', 'children')],
        [Input('config-store', 'data'),
         Input("switches", "value")],
        State('config-store', 'data'),
        prevent_initial_call=True
    )
    def update_bar_chart(config_data, selected_values, current_values):
        ctx = callback_context
        if not ctx.triggered:
            return {}, None

        # Get the id of the triggered input
        triggered_input = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_input == "config-store":
            # This is the first callback functionality (init_barchart)
            if config_data is not None:
                most_shared_images_dict, bar_chart = gen_barchart(config_data, df)
                return most_shared_images_dict, bar_chart
            return {}, None

        elif triggered_input == "switches":
            # This is the second callback functionality (enforce_two_switches)
            hash_platform_counts = df.groupby('hash')['platform'].apply(set)

            required_platforms = set(selected_values)  # Platforms to include
            excluded_platforms = {"Facebook", "Instagram", "Twitter"} - required_platforms  # Platforms to exclude

            # Filter hashes based on selected values
            valid_hashes = hash_platform_counts[
                hash_platform_counts.apply(
                    lambda x: required_platforms.issubset(x) and not any(platform in x for platform in excluded_platforms)
                )
            ].index

            # Step 2: Filter the original dataframe to include only these valid hashes
            filtered_df = df[df['hash'].isin(valid_hashes)]
        
            most_shared_images_dict, bar_chart = gen_barchart(config_data, filtered_df)
            return most_shared_images_dict, bar_chart

        # Fallback return in case something goes wrong
        return {}, None
    
    # @callback(
    #     [Output('df-k-most-freq-hashes', 'data'),
    #      Output('bar-chart-wrapper', 'children')],
    #      Input('config-store', 'data'),
    #      allow_duplicate=True
    # )
    # def init_barchart(config):
    #     # x ... 10 most shared images; y ... num of shares; stacked y and color ... platform
    #     if config is not None:
    #         most_shared_images_dict, bar_chart = gen_barchart(config, df)
    #         return most_shared_images_dict, bar_chart
    #     return {}
    
    # @callback(
    #     [Output('df-k-most-freq-hashes', 'data'),
    #      Output('bar-chart-wrapper', 'children')],
    #     Input("switches", "value"),
    #     State('config', 'data'),
    #     prevent_initial_call=True,
    #     allow_duplicate=True
    # )
    # def apply_filter_on_barchart(selected_values, current_values, config):
    #     print(selected_values)
    #     hash_platform_counts = df.groupby('hash')['platform'].apply(set)

    #     # Keep only hashes that contain both 'Instagram' and 'Facebook' but exclude 'Twitter'
    #     valid_hashes = hash_platform_counts[
    #         hash_platform_counts.apply(lambda x: 'Instagram' in x and 'Facebook' in x and 'Twitter' not in x)
    #     ].index

    #     # Step 2: Filter the original dataframe to include only these valid hashes
    #     filtered_df = df[df['hash'].isin(valid_hashes)]
        
    #     most_shared_images_dict, bar_chart = gen_barchart(config, filtered_df)
    #     return most_shared_images_dict, bar_chart
    
    @callback(
        [Output('image-details', 'is_open'),
         Output('image-timeline', 'figure'),
         Output('image-details-text', 'children'),
         Output('image-party-ratios', 'figure')],
         Input('bar-chart', 'clickData'),
        [State('image-details', 'is_open'),
         State('df-k-most-freq-hashes', 'data'),
         State('config-store', 'data')]
    )
    def toggle_modal(clickData, is_open, df_dict, config):
        if clickData:
            image_hash_clicked = clickData['points'][0]['x']
            selected_hash = image_hash_clicked
            df = pd.DataFrame(df_dict)
            df_one_hash = df[df['hash'] == selected_hash]

            # Sort data by timestamp to connect dots chronologically
            df_filtered = df_one_hash.sort_values(by='timestamp')

            # Define the order of platforms
            platform_order = ['Instagram', 'Facebook', 'Twitter']  # Change to your specific platform codes if different

            # Convert platform to categorical type with a specific order
            df_filtered['platform'] = pd.Categorical(df_filtered['platform'], categories=platform_order, ordered=True)

            # Add a line trace with dark grey color connecting temporal succeeding dots (line comes first)
            fig_timeline = px.line(
                df_filtered, 
                x='timestamp', 
                y='platform',  # Use platform directly (no jitter)
                line_shape='linear',
                title=f'Image Share Timeline',
            ).update_traces(line_color='darkgrey')

            # Now add the scatter plot on top (for bigger dots and color by platform)
            scatter_fig = px.scatter(
                df_filtered,
                x='timestamp',             # Time of the post
                y='platform',              # Use platform directly (no jitter)
                color='platform',          # Color each point by platform (Instagram, Facebook, Twitter)
                color_discrete_map={
                    'Facebook': config['platform_color_map']['Facebook'],
                    'Instagram': config['platform_color_map']['Instagram'],
                    'Twitter': config['platform_color_map']['Twitter'],
                },
                hover_data=['img_id', 'party', 'name'],  # Additional hover data
                labels={'platform': 'Platform'},
                height=600,
                width=1000
            ).update_traces(marker=dict(size=12))  # Increase marker size here

            # Combine the two plots: Line first, dots on top
            fig_timeline.add_traces(scatter_fig.data)

            # Update layout for better readability
            fig_timeline.update_layout(
                yaxis_title='Platform',
                yaxis=dict(tickvals=list(range(len(platform_order))), ticktext=platform_order),  # Set y-ticks to fixed order
                xaxis_title='Time',
                legend_title='Platform',
                hovermode='closest',
            )
            
            party_ratios = df_one_hash['party'].value_counts()
            
            df_party_ratios = party_ratios.reset_index()
            df_party_ratios.columns = ['party', 'count']

            fig_party_ratios = px.bar(df_party_ratios, x='party', y='count',
                labels={'party': 'Party', 'count': 'Frequency'},
                title='Platform Frequency',
                color='party',
                color_discrete_map=config['party_color_map'])
            
            image_details_text = [
                html.P(f"Image Hash: {selected_hash}"),
                html.P(f"Times Shared: {df_one_hash.shape[0]}"),
            ]
            
            return True, fig_timeline, image_details_text, fig_party_ratios
    
        return is_open, dash.no_update, [], {}
    