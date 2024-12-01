import pandas as pd
import plotly.express as px
from dash import html
from utils.image_loader import load_image
import dash_bootstrap_components as dbc

def create_image_details_items(df, config, img_hash):
    df_one_hash = df[df['hash'] == img_hash]
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
        template='plotly_dark',
        yaxis_title='Platform',
        yaxis=dict(tickvals=list(range(len(platform_order))), ticktext=platform_order),  # Dynamically set y-ticks
        xaxis_title='Time',
        legend_title='Platform',
        hovermode='closest',
        paper_bgcolor=config['style']['foreground_color'],
        plot_bgcolor=config['style']['foreground_color'],
    )
    
    ### PARTY RATIO BAR CHART
    party_ratios = df_one_hash['party'].value_counts()
    
    df_party_ratios = party_ratios.reset_index()
    df_party_ratios.columns = ['party', 'count']

    fig_party_ratios = px.bar(df_party_ratios, x='party', y='count',
        labels={'party': 'Party', 'count': 'Frequency'},
        title='Platform Frequency',
        color='party',
        color_discrete_map=config['party_color_map'])
    
    fig_party_ratios.update_layout(
        template='plotly_dark',
        paper_bgcolor=config['style']['foreground_color'],
        plot_bgcolor=config['style']['foreground_color'],
    )
    
    image_details_text = [
        html.P(f"Image Hash: {img_hash}"),
        html.P(f"Times Shared: {df_one_hash.shape[0]}"),
        dbc.FormText(
            "These statistics and plots refer to the entire dataset (The network view only includes ones where the party is known)",
            style={"fontSize": "0.9rem", "color": "#A0A0A0"}
        ),
    ]
    
    img_data = load_image(img_hash)
    
    return fig_timeline, image_details_text, fig_party_ratios, img_data