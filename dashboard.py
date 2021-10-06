import plotly.express as px
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np
import json
import os
from urllib.request import urlopen


# Initialize app

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}
    ]
)
app.title = 'US Food Insecurity'
server = app.server

# Load Data

with open('data/gz_2010_us_040_00_500k.json') as geojson:
    states = json.load(geojson)

with open('data/db.csv') as df_file:
    df = pd.read_csv(df_file, parse_dates=['start_date', 'end_date'])

# Figures & Components

map_fig = px.choropleth_mapbox(df, geojson=states, locations='state', featureidkey='properties.NAME', color='overall_after',
                               color_continuous_scale=px.colors.sequential.Plasma,
                               mapbox_style='carto-positron',
                               zoom=4, center={'lat': 38, 'lon': -95.7129},
                               opacity=1,
                               )
map_fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

chart_fig = px.bar(
    df[df.state.eq('Alabama')],
    x='study_site',
    y=['overall_before', 'overall_after', 'overall_diff'],
    facet_col='variable',
    color='study_site',
    title='{} Food Insecurity'.format('Alabama')
)

start_date = df['start_date'].min()
end_date = df['end_date'].max()
n_months = (end_date.to_period('M')-start_date.to_period('M')).n + 1
month_keys = [i for i in range(0, n_months)]
month_labels = pd.date_range(start_date, periods=n_months, freq='M').strftime('%B,\n%Y').tolist()
dates = dict(zip(month_keys, month_labels))

date_slider = dcc.RangeSlider(
    id='date-slider',
    disabled=True,
    min=-1,
    max=n_months,
    step=None,
    marks=dates,
    value=[]
)


# App layout

header = dbc.Row(
    id='header',
    justify='between',
    align='start',
    children=[
        dbc.Col(
            width=8,
            children=[
                html.H1(children='United States Food Insecurity'),
                html.P(
                    id='description',
                    className='text-muted',
                    children=[
                        'Support for this project was provided in part by Cooperative Agreement Number (U48DP006374) funded by the Centers for Disease Control and Prevention’s Division of Nutrition, Physical Activity, and Obesity (DNPAO) and Prevention Research Centers Program, which includes the Nutrition and Obesity Policy Research and Evaluation Network (NOPREN). The findings and conclusions in this product are those of the author(s) and do not necessarily represent the official position of the CDC or DHHS.'
                    ]
                ),
            ]
        ),
        dbc.Col(
            width='auto',
            children=[
                html.A(
                    html.Img(id='logo', src=app.get_asset_url('segs_logo.png')),
                    href='https://segs.w3.uvm.edu/',
                ),
            ]
        )
    ],
)

main_map = html.Div(
    id='map-container',
    children=[
        dbc.Row(
            dbc.Col(
                width=12,
                children=[
                    dcc.Graph(
                        id='map-figure',
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

study_site_info = html.Div(
    id='study-site-info',
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H2(
                            id="study-site-state",
                            children=[
                                "Hello World"
                            ]
                        )
                    ]
                ),
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='study-site-dropdown',
                            options=[],
                            value=''
                        ),
                    ],
                    width=3
                ),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    date_slider
                ),
            ]
        )
    ]
)

app.layout = dbc.Container(
    id='root',
    fluid=False,
    className='p-5',
    children=[
        header,
        main_map,
        study_site_info,
    ],
)

@app.callback(
    Output('study-site-dropdown', 'options'),
    Output('study-site-dropdown', 'value'),
    Output('study-site-state', 'children'),
    Input('map-figure', 'clickData')
)
def display_click_data(clickData):
    try:
        state_name = clickData['points'][0]['location']
        study_sites = df[(df['state'] == state_name)]['study_site'].tolist()
        options = [{'label': site, 'value': site} for site in study_sites]
        return (options, study_sites[0], state_name)
    except TypeError as e:
        print(e)
        return ([], '', '')

@app.callback(
    Output('date-slider', 'value'),
    Input('study-site-dropdown', 'value'),
)
def display_site_data(study_site):
    try:
        study_site = df[(df['study_site'] == study_site)].iloc[0]
        study_site_start_date = study_site['start_date']
        study_site_end_date = study_site['end_date']
        start_month_value = ((study_site_start_date.to_period('M')-start_date.to_period('M')).n)
        end_month_value = ((study_site_end_date.to_period('M')-start_date.to_period('M')).n)
        date_values = [start_month_value, end_month_value]
        return (date_values)
    except IndexError as e:
        print(e)
        return []


if __name__ == '__main__':
    app.run_server(debug=True)
