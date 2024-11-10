import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State

def Navbar():
    navbar = dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("Election Dashboard", href="#"),

                dbc.Nav(
                    [
                        # Page links
                        dbc.NavItem(dbc.NavLink("Cross-Party Partisans", href="/")),
                        dbc.NavItem(dbc.NavLink("Platform Dissemination", href="/cross-platform")),
                        dbc.NavItem(dbc.NavLink("network_v2", href="/network_v2")),

                        # Dropdown for "About"
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem("Author", href="https://www.linkedin.com/in/tobias-raidl/", target="_blank"),
                                dbc.DropdownMenuItem("PolarVis", href="https://polarvis.github.io/", target="_blank"),
                            ],
                            nav=True,
                            in_navbar=True,
                            label="About",
                        ),
                    ],
                    className="ml-auto",  # Aligns the nav items to the right
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-4"
    )
    
    @callback(Output("page-content", "children"), [Input("url", "pathname")])
    def display_page(pathname):
        if pathname == "/cross-party-partisans":
            return html.H3("Cross-Party Partisans Page Content")
        elif pathname == "/platform-dissemination":
            return html.H3("Platform Dissemination Page Content")
        else:
            return html.H3("Welcome to the Homepage")
        
    return navbar