from dash.dependencies import Input, Output, State
from dash import callback, dcc, html
import pandas as pd
import dash
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from utils.platform_view_graph import PlatformGraph, TimespanGraph

def register_platform_view_callbacks(df):
    
    @callback(
        [Output('df-k-most-freq-hashes', 'data'),
         Output('bar-chart-wrapper', 'children')],
         Input('config-store', 'data')
    )
    def generate_barchart(config):
        # x ... 10 most shared images; y ... num of shares; stacked y and color ... platform
        if config is not None:
            k=20
            hash_counts = df['hash'].value_counts()
            top_hashes = hash_counts.iloc[0:k]
            most_shared_images = df[df['hash'].isin(list(top_hashes.index))]
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
                title="Most Shared Images by Platform",
                xaxis_title="Hash",
                yaxis_title="Count",
                xaxis={'categoryorder': 'total descending'},
            )
            
            bar_chart = dcc.Graph(figure=fig, id='bar-chart')
            
            return most_shared_images.to_dict(), bar_chart
        return {}
    
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