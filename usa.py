import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import pathlib
from dash.dependencies import Input, Output, State


# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "US Opioid Epidemic"
server = app.server


with urlopen('https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json') as response:
    states = json.load(response)

df = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv",
                 dtype={"fips": str})


# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())


YEARS = [2003, 2004, 2005, 2006, 2007, 2008,
         2009, 2010, 2011, 2012, 2013, 2014, 2015]


# Map figure

map_fig = px.choropleth_mapbox(df, geojson=states, locations='state', featureidkey="properties.NAME", color='cases',
                               color_continuous_scale=px.colors.sequential.Plasma,
                               mapbox_style="carto-positron",
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=1,
                               )
map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

chart_fig = px.bar(df[df.state.eq('Alabama')], x="date", y="cases")


# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("segs_logo.png")),
                    href="https://segs.w3.uvm.edu/",
                ),
                html.H4(children="COVID-19 Cases by State"),
                html.P(
                    id="description",
                    children=[
                        "† Data for COVID-19 Deaths sourced from NYTimes: ",
                        html.A(
                            "https://github.com/nytimes/covid-19-data/",
                            href="https://github.com/nytimes/covid-19-data/"
                        )
                    ]
                ),

            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap Title",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=map_fig
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Alabama",
                                    "value": "Alabama",
                                },
                                {
                                    "label": "Alaska",
                                    "value": "Alaska",
                                },
                                {
                                    "label": "Arizona",
                                    "value": "Arizona",
                                },
                                {
                                    "label": "Arkansas",
                                    "value": "Arkansas",
                                },
                                {
                                    "label": "California",
                                    "value": "California",
                                },
                                {
                                    "label": "Colorado",
                                    "value": "Colorado",
                                },
                                {
                                    "label": "Connecticut",
                                    "value": "Connecticut",
                                },
                                {
                                    "label": "Delaware",
                                    "value": "Delaware",
                                },
                                {
                                    "label": "Florida",
                                    "value": "Florida",
                                },
                                {
                                    "label": "Georgia",
                                    "value": "Georgia",
                                },
                                {
                                    "label": "Hawaii",
                                    "value": "Hawaii",
                                },
                                {
                                    "label": "Idaho",
                                    "value": "Idaho",
                                },
                                {
                                    "label": "Illinois",
                                    "value": "Illinois",
                                },
                                {
                                    "label": "Indiana",
                                    "value": "Indiana",
                                },
                                {
                                    "label": "Iowa",
                                    "value": "Iowa",
                                },
                                {
                                    "label": "Kansas",
                                    "value": "Kansas",
                                },
                                {
                                    "label": "Kentucky",
                                    "value": "Kentucky",
                                },
                                {
                                    "label": "Louisiana",
                                    "value": "Louisiana",
                                },
                                {
                                    "label": "Maine",
                                    "value": "Maine",
                                },
                                {
                                    "label": "Maryland",
                                    "value": "Maryland",
                                },
                                {
                                    "label": "Massachusetts",
                                    "value": "Massachusetts",
                                },
                                {
                                    "label": "Michigan",
                                    "value": "Michigan",
                                },
                                {
                                    "label": "Minnesota",
                                    "value": "Minnesota",
                                },
                                {
                                    "label": "Mississippi",
                                    "value": "Mississippi",
                                },
                                {
                                    "label": "Missouri",
                                    "value": "Missouri",
                                },
                                {
                                    "label": "Montana",
                                    "value": "Montana",
                                },
                                {
                                    "label": "Nebraska",
                                    "value": "Nebraska",
                                },
                                {
                                    "label": "Nevada",
                                    "value": "Nevada",
                                },
                                {
                                    "label": "New Hampshire",
                                    "value": "New Hampshire",
                                },
                                {
                                    "label": "New Jersey",
                                    "value": "New Jersey",
                                },
                                {
                                    "label": "New Mexico",
                                    "value": "New Mexico",
                                },
                                {
                                    "label": "New York",
                                    "value": "New York",
                                },
                                {
                                    "label": "North Carolina",
                                    "value": "North Carolina",
                                },
                                {
                                    "label": "North Dakota",
                                    "value": "North Dakota",
                                },
                                {
                                    "label": "Ohio",
                                    "value": "Ohio",
                                },
                                {
                                    "label": "Oklahoma",
                                    "value": "Oklahoma",
                                },
                                {
                                    "label": "Oregon",
                                    "value": "Oregon",
                                },
                                {
                                    "label": "Pennsylvania",
                                    "value": "Pennsylvania",
                                },
                                {
                                    "label": "Puerto Rico",
                                    "value": "Puerto Rico",
                                },
                                {
                                    "label": "Rhode Island",
                                    "value": "Rhode Island",
                                },
                                {
                                    "label": "South Carolina",
                                    "value": "South Carolina",
                                },
                                {
                                    "label": "South Dakota",
                                    "value": "South Dakota",
                                },
                                {
                                    "label": "Tennessee",
                                    "value": "Tennessee",
                                },
                                {
                                    "label": "Texas",
                                    "value": "Texas",
                                },
                                {
                                    "label": "Utah",
                                    "value": "Utah",
                                },
                                {
                                    "label": "Vermont",
                                    "value": "Vermont",
                                },
                                {
                                    "label": "Virginia",
                                    "value": "Virginia",
                                },
                                {
                                    "label": "Washington",
                                    "value": "Washington",
                                },
                                {
                                    "label": "West Virginia",
                                    "value": "West Virginia",
                                },
                                {
                                    "label": "Wisconsin",
                                    "value": "Wisconsin",
                                },
                                {
                                    "label": "Wyoming",
                                    "value": "Wyoming",
                                },
                            ],
                            value="Alabama",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=chart_fig
                        ),
                    ],
                ),
            ],
        ),
    ],
)

@app.callback(
    Output("selected-data", "figure"),
    [
        Input("chart-dropdown", "value"),
    ],
)
def display_selected_data(chart_dropdown):
    chart_fig = px.bar(
        df[df.state.eq(chart_dropdown)],
        x="date",
        y="cases",
        title="{} Cumulative COVID-19 Cases".format(chart_dropdown)
    )
    chart_fig.update_traces(
        marker_color="#1f2630",
    )
    return chart_fig


if __name__ == "__main__":
    app.run_server(debug=True)