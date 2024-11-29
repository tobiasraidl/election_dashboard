from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, dcc, html
import pandas as pd
import dash
import plotly.graph_objects as go
import os
from utils.helper import create_image_details_items

def register_platform_view_callbacks(df):
    
    def gen_barchart(config, filtered_df):
        k=20
        hash_counts = filtered_df['hash'].value_counts()
        top_hashes = hash_counts.iloc[0:k]
        most_shared_images = filtered_df[filtered_df['hash'].isin(list(top_hashes.index))]
        counts = most_shared_images.groupby(['hash', 'platform'])['platform'].count()
        df_temp = counts.unstack(fill_value=0)
        df_temp['row_sum'] = df_temp.sum(axis=1)
        df_temp = df_temp.sort_values(by='row_sum', ascending=False)
        df_temp = df_temp.drop(columns=['row_sum'])

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
                marker_color=platform_colors[platform],
            ))

        fig.update_layout(
            template='plotly_dark',
            barmode='stack',
            title='Most Shared Images across Platforms',
            xaxis_title="Image",
            yaxis_title="Times Shared",
            showlegend=False,
            xaxis=dict(showticklabels=False),
            plot_bgcolor=config['style']['foreground_color'],
            paper_bgcolor=config['style']['foreground_color'],
        )
        fig.update_xaxes(showticklabels=False)
        image_elements = []
        placeholder_image = './assets/placeholder.jpg'
        image_width = '4%'

        for hash in df_temp.index:
            image_path = f'./assets/{hash}.jpg'
            # Check if the image exists
            if not os.path.exists(f'./assets/{hash}.jpg'):
                image_path = placeholder_image
                
            image_elements.append(html.Img(src=image_path, style={'width': image_width, 'height': 'auto', 'object-fit': 'contain', 'display': 'block', 'margin': '0 auto'}))
            
        # Create the layout with the bar chart and images
        bar_chart = dcc.Graph(figure=fig, id='bar-chart')

        return most_shared_images.to_dict(), html.Div([
            bar_chart,
            html.Div(image_elements, 
                style={
                        'display': 'flex', 
                        'justify-content': 'space-between',
                        'padding-left': '80px',
                        'padding-right': '80px',
                        'padding-bottom': '80px',
                }
            )
        ])
    
    @callback(
        [Output('df-k-most-freq-hashes', 'data'),
         Output('bar-chart-wrapper', 'children')],
        [Input('config-store', 'data'),
         Input("switches", "value")],
    )
    def update_bar_chart(config_data, selected_values):
        if len(selected_values) < 2:
            return {}, html.P('Select at least two platforms', className='p-5')
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
        [Output('image-details-platform-page', 'is_open'),
         Output('image-timeline-platform-page', 'figure'),
         Output('image-details-text-platform-page', 'children'),
         Output('image-party-ratios-platform-page', 'figure'),
         Output('image-details-image-platform-page', 'src')],
         Input('bar-chart', 'clickData'),
        [State('image-details-platform-page', 'is_open'),
         State('df-k-most-freq-hashes', 'data'),
         State('config-store', 'data')]
    )
    def toggle_modal(clickData, is_open, df_dict, config):
        if clickData:
            image_hash_clicked = clickData['points'][0]['x']
            img_hash = image_hash_clicked
            df = pd.DataFrame(df_dict)
            fig_timeline, image_details_text, fig_party_ratios, img_data = create_image_details_items(df, config, img_hash)
            return True, fig_timeline, image_details_text, fig_party_ratios, img_data
        return is_open, dash.no_update, [], {}, 'assets/placeholder.jpg'
    