from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html
import pandas as pd
import dash
import plotly.graph_objects as go
import plotly.express as px
import os

from utils.image_loader import load_image

def register_platform_view_callbacks(df):
    
    def gen_barchart(config, filtered_df):
        k=20
        hash_counts = filtered_df['hash'].value_counts()
        top_hashes = hash_counts.iloc[0:k]
        most_shared_images = filtered_df[filtered_df['hash'].isin(list(top_hashes.index))]
        counts = most_shared_images.groupby(['hash', 'platform'])['platform'].count()

        df_temp = counts.unstack(fill_value=0)

        df_temp['row_sum'] = df_temp.sum(axis=1)

        # Sort the DataFrame by 'row_sum' in descending order
        df_temp = df_temp.sort_values(by='row_sum', ascending=False)

        # Optionally, drop the 'row_sum' column if it's no longer needed
        df_temp = df_temp.drop(columns=['row_sum'])


        fig = go.Figure()

        platform_colors = {
            'Facebook': config['platform_color_map']['Facebook'],
            'Instagram': config['platform_color_map']['Instagram'],
            'Twitter': config['platform_color_map']['Twitter']
        }

        for platform in df_temp.columns:
            fig.add_trace(go.Bar(
                x=df_temp.index,  # Use the number list as x-axis values
                y=df_temp[platform],
                name=platform,
                marker_color=platform_colors[platform],
            ))

        fig.update_layout(
            template='plotly_dark',
            barmode='stack',
            xaxis_title="Image",
            yaxis_title="Times Shared",
            showlegend=False,
            xaxis=dict(showticklabels=False),
            plot_bgcolor=config['style']['foreground_color'],
            paper_bgcolor=config['style']['foreground_color'],
        )
        fig.update_xaxes(showticklabels=False)

        # Prepare images under the bars
        image_elements = []
        placeholder_image = './assets/placeholder.jpg'  # Placeholder image path
        image_width = '4%'  # Set a smaller fixed width for all images (adjusted here)

        for hash in df_temp.index:
            image_path = f'./assets/{hash}.jpg'  # Path to your image files
            # Check if the image exists
            if not os.path.exists(f'./assets/{hash}.jpg'):
                image_path = placeholder_image  # Use placeholder if not found
                
            image_elements.append(html.Img(src=image_path, style={'width': image_width, 'height': 'auto', 'object-fit': 'contain', 'display': 'block', 'margin': '0 auto'}))
            
        # Create the layout with the bar chart and images
        bar_chart = dcc.Graph(figure=fig, id='bar-chart')

        return most_shared_images.to_dict(), html.Div([
            bar_chart,
            html.Div(image_elements, 
                style={
                        'display': 'flex', 
                        'justify-content': 'space-between',
                        'padding-left': '80px',  # Adjust how far right the images start
                        'padding-right': '80px',  # Adjust how far left the images end
                        'padding-bottom': '80px',
                }
            )
        ])
    
    @callback(
        [Output('df-k-most-freq-hashes', 'data'),
         Output('bar-chart-wrapper', 'children')],
        [Input('config-store', 'data'),
         Input("switches", "value")],
        # State('config-store', 'data'),
    )
    def update_bar_chart(config_data, selected_values):
        if len(selected_values) < 2:
            return {}, html.P('Select at least two platforms')
        if config_data is not None:
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
    
    @callback(
        [Output('image-details', 'is_open'),
         Output('image-timeline', 'figure'),
         Output('image-details-text', 'children'),
         Output('image-party-ratios', 'figure'),
         Output('image', 'src')],
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
            # Sort by timestamp as before
            # Sort by timestamp as before
            df_filtered = df_one_hash.sort_values(by='timestamp')
            
            # Dynamically get the unique platforms in the order they appear
            platform_order = df_filtered['platform'].unique()
            
            # Convert platform to a categorical type with a dynamic order
            df_filtered['platform'] = pd.Categorical(df_filtered['platform'], categories=platform_order, ordered=True)
            
            # Add the line trace with dark grey color connecting temporal succeeding dots, hide legend
            fig_timeline = px.line(
                df_filtered, 
                x='timestamp', 
                y='platform',  # Use platform directly (no jitter)
                line_shape='linear',
                title='Image Share Timeline',
            ).update_traces(line_color='darkgrey', showlegend=False)  # Hide legend for line
            
            # Add the scatter plot on top, hide legend
            scatter_fig = px.scatter(
                df_filtered,
                x='timestamp',             # Time of the post
                y='platform',              # Use platform directly (no jitter)
                color='platform',          # Color each point by platform (Instagram, Facebook, Twitter)
                color_discrete_map={
                    'Facebook': config['platform_color_map'].get('Facebook', 'blue'),  # Default to blue if color not found
                    'Instagram': config['platform_color_map'].get('Instagram', 'purple'),  # Default to purple
                    'Twitter': config['platform_color_map'].get('Twitter', 'cyan'),  # Default to cyan
                },
                hover_data=['img_id', 'party', 'name'],  # Additional hover data
                labels={'platform': 'Platform'},
                height=600,
                width=1000
            ).update_traces(marker=dict(size=12), showlegend=False)  # Increase marker size and hide legend
            
            # Combine the two plots: Line first, dots on top
            fig_timeline.add_traces(scatter_fig.data)
            
            # Update layout with dynamic tick values
            fig_timeline.update_layout(
                yaxis_title='Platform',
                yaxis=dict(tickvals=list(range(len(platform_order))), ticktext=platform_order),  # Dynamically set y-ticks
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
            
            img_data = load_image(image_hash_clicked)

            
            return True, fig_timeline, image_details_text, fig_party_ratios, img_data
    
        return is_open, dash.no_update, [], {}, 'assets/placeholder.jpg'
    