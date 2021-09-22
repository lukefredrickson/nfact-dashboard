import plotly.express as px
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import json
import os
from urllib.request import urlopen


# Initialize app

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
app.title = "US Opioid Epidemic"
server = app.server


with urlopen('https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json') as response:
    states = json.load(response)

df = pd.read_csv(
    "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv")


# Load data


YEARS = [2003, 2004, 2005, 2006, 2007, 2008,
         2009, 2010, 2011, 2012, 2013, 2014, 2015]


# Figures

map_fig = px.choropleth_mapbox(df, geojson=states, locations='state', featureidkey="properties.NAME", color='cases',
                               color_continuous_scale=px.colors.sequential.Plasma,
                               mapbox_style="carto-positron",
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=1,
                               )
map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

chart_fig = px.bar(df[df.state.eq('Alabama')], x="date", y="cases")


# App layout

header = dbc.Row(
    id="header",
    justify="between",
    align="start",
    children=[
        dbc.Col(
            width=8,
            children=[
                html.H1(children="United States Food Insecurity"),
                html.P(
                    id="description",
                    className="text-muted",
                    children=[
                        "Support for this project was provided in part by Cooperative Agreement Number (U48DP006374) funded by the Centers for Disease Control and Prevention’s Division of Nutrition, Physical Activity, and Obesity (DNPAO) and Prevention Research Centers Program, which includes the Nutrition and Obesity Policy Research and Evaluation Network (NOPREN). The findings and conclusions in this product are those of the author(s) and do not necessarily represent the official position of the CDC or DHHS."
                    ]
                ),
            ]
        ),
        dbc.Col(
            width="auto",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("segs_logo.png")),
                    href="https://segs.w3.uvm.edu/",
                ),
            ]
        )
    ],
)

main_map = html.Div(
    id="map-container",
    children=[
        dbc.Row(
            dbc.Col(
                width=12,
                children=[
                    html.H2(
                        "Map Title",
                        id="map-title",
                    ),
                ]
            )
        ),
        dbc.Row(
            dbc.Col(
                width=12,
                children=[
                    dcc.Graph(
                        id="map-figure",
                        figure=map_fig
                    ),
                ]
            )
        )
    ]
)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

graphs = html.Div(
    id="graph-container",
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Graph(
                            id="selected-data",
                            figure=chart_fig
                        ),
                    ]
                ),
                dbc.Col(
                    html.Div(
                        children=[
                            dcc.Markdown("""
                                            **Click Data**

                                            Click on states on the map.
                                        """),
                            html.Pre(id='click-data', style=styles['pre']),
                        ],
                        className='three columns'),
                ),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(

                ),
                dbc.Col(

                ),
            ]
        )
    ]
)

app.layout = dbc.Container(
    id="root",
    fluid=True,
    className="p-5",
    children=[
        header,
        main_map,
        graphs,
    ],
)


@app.callback(
    Output('click-data', 'children'),
    Input('map-figure', 'clickData')
)
def display_click_data(clickData):
    return clickData["points"][0]["location"]

@app.callback(
    Output("selected-data", "figure"),
    Input('map-figure', 'clickData')
)
def display_click_data(clickData):
    chart_dropdown = clickData["points"][0]["location"]
    chart_fig = px.bar(
        df[df.state.eq(chart_dropdown)],
        x="date",
        y="cases",
        title="{} Cumulative COVID-19 Cases".format(chart_dropdown)
    )
    return chart_fig


if __name__ == "__main__":
    app.run_server(debug=True)
