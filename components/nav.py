import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Briann Booth Portfolio",
    brand_href="#",
    color="primary",
    dark=True,
)

        # if end_file == "pdf":
        #     contents= f"data:application/{end_file};base64,{jpg_as_text}"
        # elif end_file == 'svg':
        #     contents= f"data:image/svg+xml;base64,{jpg_as_text}"
        # elif end_file == 'png':
        #     contents= f"data:text/png;base64,{jpg_as_text}"
        # else:
        #     contents =f"data:image/{end_file.lower()};base64,{jpg_as_text}"