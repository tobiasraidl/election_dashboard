import dash_bootstrap_components as dbc

def Navbar():
    
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Accounts Network", href="/accounts-network")),
            dbc.NavItem(dbc.NavLink("Cross Platform", href="/cross-platform")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("About", header=True),
                    dbc.DropdownMenuItem("Author", href="https://www.linkedin.com/in/tobias-raidl/", target="_blank"),
                    dbc.DropdownMenuItem("PolarVis", href="https://polarvis.github.io/", target="_blank"),
                ],
                nav=True,
                in_navbar=True,
                label="About",
            ),
        ],
    )