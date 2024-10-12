import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app.layout = html.Div(
#     [
#         html.Div("Python Multipage App with Dash", style={'fontSize': 50, 'textAlign': 'center'}),
#         html.Div([
#             
#         ]),
#         html.Hr(),
        
#         # Content of each page
#         dash.page_container
#     ]
# )

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Cluster View", href="/cluster-view")),
                dbc.NavItem(dbc.NavLink("Platform View", href="/platform-view")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("More", header=True),
                        dbc.DropdownMenuItem("Author", href="https://www.linkedin.com/in/tobias-raidl/"),
                        dbc.DropdownMenuItem("PolarVis", href="https://polarvis.github.io/"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="More",
                ),
            ],
        ),
        # Content of each page
        dash.page_container
    ]
)

if __name__ == "__main__":
    app.run(debug=True)