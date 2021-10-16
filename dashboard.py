import plotly.express as px
import plotly.io as pio
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

map_fig = px.choropleth_mapbox(
    df,
    geojson=states, 
    locations=df['state'].unique(),
    featureidkey='properties.NAME',
    color = df.groupby(['state']).size(),
    labels={
        'locations': 'State',
        'color': 'Number of Study Sites',
    },
    color_continuous_scale=px.colors.sequential.Sunsetdark,
    mapbox_style='carto-positron',
    zoom=4, center={'lat': 38, 'lon': -95.7129},
    opacity=1,
)
map_fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0}, coloraxis_showscale=False)

start_date = df['start_date'].min()
end_date = df['end_date'].max()
n_months = (end_date.to_period('M')-start_date.to_period('M')).n + 1
month_keys = [i for i in range(0, n_months)]
month_labels = pd.date_range(start_date, periods=n_months, freq='M').strftime('%b, %Y').tolist()
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


states = df['state'].unique().tolist()
states.insert(0, states.pop(states.index('National')))
states_dropdown_options = [{'label': state, 'value': state} for state in states]
study_site_state_dropdown = dcc.Dropdown(
    id='study-site-state-dropdown',
    options=states_dropdown_options,
    value='National'
)

study_site_dropdown = dcc.Dropdown(
    id='study-site-dropdown',
    options=[{'label': 'National', 'value': 'National'}],
    value='National'
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

study_site_table = dbc.Table(
    children=[
        html.Thead([
            html.Th('Study Site Information', colSpan=2)
        ]),
        html.Tbody([
            html.Tr([html.Td('Target Population'), html.Td('', id='target-population')]),
            html.Tr([html.Td('Representative of State Population'), html.Td('', id='rep-state')]),
            html.Tr([html.Td('Survey Sample Type'), html.Td('', id='sample-type')]),
            html.Tr([html.Td('Survey Weighting'), html.Td('', id='weighting')]),
            html.Tr([html.Td('Sampling and Recruitment'), html.Td('', id='sample-recruitment')]),
        ])
    ],
    bordered=True,
    size='lg'
)

study_site_info = html.Div(
    id='study-site-info',
    children=[
        dbc.Row(
            dbc.Col(
                html.Br()
            )
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H2(
                            id='study-site-state',
                            children=[
                                'Study Site State'
                            ]
                        ),
                        html.H4(
                            id='study-site-name',
                            children=[
                                'Study Site Name'
                            ]
                        )
                    ]
                ),
                dbc.Col(
                    children=[
                        html.H6(
                            'Select State:'
                        ),
                        study_site_state_dropdown,
                    ],
                    width=3
                ),
                dbc.Col(
                    children=[
                        html.H6(
                            'Select Study Site:'
                        ),
                        study_site_dropdown,
                    ],
                    width=3
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                html.Br()
            )
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H4(
                            'Survey Timeline'
                        ),
                        date_slider
                    ]
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                children=[
                    html.Br(),
                ]
            )
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        study_site_table,
                        dcc.Graph(id='population-fig', figure=px.bar()),
                        dcc.Graph(id='food-insecurity-fig', figure=px.bar()),
                        dcc.Graph(id='job-disruption-fig', figure=px.bar()),
                    ]
                )
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
    Output('study-site-state-dropdown', 'value'),
    Input('map-figure', 'clickData')
)
def handle_map_click(clickData):
    try:
        state_name = clickData['points'][0]['location']
        return state_name
    except TypeError as e:
        print(e)
        return 'National'

@app.callback(
    Output('study-site-dropdown', 'options'),
    Output('study-site-dropdown', 'value'),
    Output('study-site-state', 'children'),
    Input('study-site-state-dropdown', 'value')
)
def handle_state_updated(state_name):
    try:
        study_sites = df[(df['state'] == state_name)]['study_site'].tolist()
        options = [{'label': site, 'value': site} for site in study_sites]
        study_site = study_sites[0]
        return (options, study_site, state_name)
    except (TypeError, IndexError) as e:
        print(e)
        return ([{'label': 'National', 'value': 'National'}], 'National', 'National')

@app.callback(
    Output('study-site-name', 'children'),
    Input('study-site-dropdown', 'value'),
)
def display_site_name(study_site_name):
    return study_site_name

@app.callback(
    
    Output('date-slider', 'value'),
    Input('study-site-dropdown', 'value'),
)
def display_site_date_range(study_site_name):
    try:
        study_site = df[(df['study_site'] == study_site_name)].iloc[0]
        study_site_start_date = study_site['start_date']
        study_site_end_date = study_site['end_date']
        start_month_value = ((study_site_start_date.to_period('M')-start_date.to_period('M')).n)
        end_month_value = ((study_site_end_date.to_period('M')-start_date.to_period('M')).n)
        date_values = [start_month_value, end_month_value]
        return (date_values)
    except IndexError as e:
        print(e)
        return ([])

@app.callback(
    Output('target-population', 'children'),
    Output('rep-state', 'children'),
    Output('sample-type', 'children'),
    Output('weighting', 'children'),
    Output('sample-recruitment', 'children'),
    Input('study-site-dropdown', 'value'),
)
def display_site_info(study_site_name):
    try:
        study_site = df[(df['study_site'] == study_site_name)].iloc[0]
        return(
            study_site['target_population'],
            study_site['rep_state'],
            study_site['sample_type'],
            study_site['weighting'],
            study_site['sample_recruitment'],
        )
    except IndexError as e:
        print(e)
        return ('', '', '', '', '')

@app.callback(
    Output('population-fig', 'figure'),
    Output('food-insecurity-fig', 'figure'),
    Output('job-disruption-fig', 'figure'),
    Input('study-site-dropdown', 'value'),
)
def display_site_graphs(study_site_name):
    study_site = df[(df['study_site'] == study_site_name)].iloc[0]
    site_df = study_site.to_frame()
    site_df.index.name = 'vars'
    site_df.reset_index(inplace=True)
    site_df.columns.values[1] = 'data'

    pop_chart_vars = ['total', 'hh_children', 'work_disruption', 'bipoc', 'nhw', 'nhb', 'hispanic', 'other']
    pop_chart_labels = ['Total', 'Housholds w/Children', 'Work Disruption', 'BIPOC', 'Non-Hispanic White', 'Non-Hispanic Black', 'Hispanic', 'Other']
    pop_chart_df = site_df.loc[site_df['vars'].isin(pop_chart_vars)]
    pop_chart_df = pop_chart_df.replace(to_replace=pop_chart_vars, value=pop_chart_labels)
    pop_chart_fig = px.bar(
        pop_chart_df,
        x='vars',
        y='data',
        text='data',
        color='vars',
        labels={
            'data': 'Number of Respondents',
            'vars': 'Sub-Populations',
        },
        title='Total number of respondents and sub-population characteristics',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    
    food_insec_overall_vars = ['overall_before', 'overall_after', 'overall_diff']
    food_insec_bipoc_vars = ['bipoc_before', 'bipoc_after', 'bipoc_diff']
    food_insec_nhw_vars = ['nhw_before', 'nhw_after', 'nhw_diff']
    food_insec_nhb_vars = ['nhb_before', 'nhb_after', 'nhb_diff']
    food_insec_h_vars = ['h_before', 'h_after', 'h_diff']
    food_insec_hhc_vars = ['hhc_before', 'hhc_after', 'hhc_diff']

    food_insec_vars = (
        food_insec_overall_vars +
        food_insec_bipoc_vars +
        food_insec_nhw_vars +
        food_insec_nhb_vars +
        food_insec_h_vars +
        food_insec_hhc_vars
    )

    food_insec_df = site_df.loc[site_df['vars'].isin(food_insec_vars)]
    food_insec_df['group'] = [var.split('_')[0] for var in food_insec_vars]
    food_insec_df['timeline'] = [var.split('_')[1] for var in food_insec_vars]
    group_vars = ['overall', 'bipoc', 'nhw', 'nhb', 'h', 'hhc']
    group_labels = ['All Respondents', 'BIPOC', 'Non-Hispanic White', 'Non-Hispanic Black', 'Hispanic', 'Housholds w/Children']
    timeline_vars = ['before', 'after', 'diff']
    timeline_labels = ['Before COVID-19', 'Since COVID-19', 'Difference']
    food_insec_df = food_insec_df.replace(to_replace=group_vars + timeline_vars, value=group_labels + timeline_labels)
    food_insec_fig = px.bar(
        food_insec_df,
        x='group',
        y='data',
        text=food_insec_df['data'].apply(lambda x: '{0:1.1f}%'.format(x*100)),
        color='timeline',
        labels={
            'data': 'Food-Insecure Respondents',
            'group': 'Sub-Population Group',
            'timeline': 'Timeline'
        },
        barmode='group',
        title='Food insecurity among all respondent groups',
        template='plotly_white',
        color_discrete_sequence=['#00CC96', '#636EFA', '#EF553B'],
        height=1000
    )

    job_disruption_vars = ['job_disruption', 'job_loss', 'furlough', 'reduced_hours']
    job_disruption_labels = ['Job Disruption', 'Job Loss', 'Furlough', 'Reduced Hours']
    job_disruption_df = site_df.loc[site_df['vars'].isin(job_disruption_vars)]
    job_disruption_df = job_disruption_df.replace(to_replace=job_disruption_vars, value=job_disruption_labels)
    job_disruption_fig = px.bar(
        job_disruption_df,
        x='vars',
        y='data',
        text=job_disruption_df['data'].apply(lambda x: '{0:1.1f}%'.format(x*100)),
        color='vars',
        labels={
            'data': 'Food-Insecure Respondents',
            'vars': 'Type of Work Disruption',
        },
        title='Food insecurity since COVID-19 among respondents with any type of work disruption',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    pop_chart_fig.update_layout(showlegend=False)
    job_disruption_fig.update_layout(showlegend=False, yaxis_tickformat = '0%')
    food_insec_fig.update_layout(yaxis_tickformat = '0%', )

    return(
        pop_chart_fig,
        food_insec_fig,
        job_disruption_fig
    )


if __name__ == '__main__':
    app.run_server(debug=True)
