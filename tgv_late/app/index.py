import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import random

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from datetime import datetime as dt

# Importing personnal functions 
import sys
sys.path.append('/Users/thibaud/Documents/Python_scripts/02_Projects/SNCF/open_data/')
import sncf_utils as f

# Creating app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Creating server
server = app.server

############################################################################################
######################################### DATA PREP ########################################
############################################################################################

# Loading necessary data
df = f.load_pickle('dash_first_try.p')
print(df.head())

gares = df.pipe(f.get_gares)

min_date = 2014 #df['periode'].min()
max_date = 2019 #df['periode'].max()
min_max_date_value=[min_date, max_date]
marks_data = f.slicer(min_date, max_date)

def min_max_date(df):
    min_date = df['Year'].min()
    max_date = df['Year'].max()
    if min_date > max_date:
        tmp = min_date
        min_date = max_date
        max_date = tmp
    return min_date, max_date



############################################################################################
######################################### MAIN APP #########################################
############################################################################################


app.layout = html.Div(
    className="content",
    children=[

        ##############################
        # MENU CONTEXTUEL
        ##############################
        html.Nav(
            children=[
                html.Img(
                    className="logo",
                    src="https://upload.wikimedia.org/wikipedia/fr/f/f7/Logo_SNCF_%282005%29.svg",
                    width=200,
                ),
                html.H2("OPEN DATA"),
                html.P(
                    """Analyse des retards des TGVs entre 2016 et 2019.
                    """
                ),
                html.Div(
                    children=[
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown-1",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in gares #list_of_locations
                                    ],
                                    placeholder="Gare de départ",
                                )
                            ],
                        ),
                    ],
                ),

                html.Div(
                    children=[
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown-2",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in gares 
                                    ],
                                    placeholder="Gare d'arrivée'",
                                )
                            ],
                        ),
                    ],
                ),

                dcc.Markdown(
                    children=[
                        "Source: [Open Data SNCF](https://data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/information/?sort=periode)"
                    ]
                ),
                
                ]
        ),

        ##############################
        # ENSEMBLE DES INDICATEURS
        ###############################
        html.Section(
            children=[
                ###### KPIS ######
                html.Article(
                    className='upperKPI',
                    children=[
                        html.Div(
                            className='KPIs',
                            children=[
                                dcc.Graph(id='kpi-1'),
                                dcc.Graph(id='kpi-2'),
                                dcc.Graph(id='kpi-3'),
                                dcc.Graph(id='kpi-4'),
                                dcc.Graph(id='kpi-5'),
                                # dcc.Graph(id='kpi-1'),
                            ]
                        ),
                        html.Div(
                            className='TimeSelector',
                            children=[
                                html.P('Time Selector'),
                                dcc.RangeSlider(
                                    id='id-year',
                                    min=min_date,
                                    max=max_date,
                                    step=1,
                                    marks=marks_data,
                                    value=min_max_date_value
                                ),
                                html.P('')
                            ],
                        ),
                    ]
                ),
                ###### GRAPHIQUES ######
                html.Article(
                    className='graphiques',
                    children=[
                        html.Article(
                            className='leftGraph',
                            children=[
                                html.Div(
                                    className="text-padding",
                                    children=[
                                        "Place for KPIS."
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(id='distribution-retard')
                                    ],
                                    style={'margin-top': '10'},
                                ),                               
                                html.Div(
                                    className="text-padding",
                                    children=[
                                        "Select any of the bars on the histogram to section data by time."
                                    ],
                                ),
                                dcc.Graph(id="cause-retard"),
                            ],
                        ),
                        html.Article(
                            className='rightMap',
                            children=[
                                html.Div("Ci-dessous la map"),
                                dcc.Graph(id="map-graph"),
                                html.Div(
                                    id="map-description",
                                    children=[
                                        "La liste des commentaires apparaitra ici", html.Br(),
                                        "Select any of the bars on the histogram to section data by time."
                                    ]
                                ),
                            ],
                        )
                    ]
                )
            ]
        )
    ]
)

############################################################################################
######################################### CALLBACKS ########################################
############################################################################################


@app.callback(
    Output('distribution-retard', 'figure'),
    [Input(component_id='location-dropdown-1', component_property='value')]
    )
def distribution_retard(input_, dff=df):
    data=[
        go.Scatter(
            x=[1, 2, 3, 4],
            y=[10, 11, 12, 13],
            mode='markers',
            marker=dict(
                size=[40, 60, 80, 100],
                color=[0, 1, 2, 3]
            )
        )
    ]
    return {"data": data} #, "layout": layout}




@app.callback(
    Output('cause-retard', 'figure'),
    [Input(component_id='location-dropdown-1', component_property='value')]
    )
def casue_retard(input_, dff=df):
    
    colors = ['lightslategray',] * 5
    colors[1] = 'crimson'

    data=[go.Bar(
        x=['Feature A', 'Feature B', 'Feature C',
        'Feature D', 'Feature E'],
        y=[20, 14, 23, 25, 22],
        marker_color=colors # marker color can be a single color value or an iterable
    )]
    
    return {"data": data} #, "layout": layout}


def circle_number(value):
    values = [100-value,value]
    colors = ['rgba(0, 0, 0,0)', "rgb(204, 255, 255)"]
    direction='clockwise'    
    rotation=0 if value>=50 else 360/100*value

    data = [go.Pie(
        values=values,
        hole=.9,
        showlegend=False,
        marker={'colors':colors},
        textinfo="none",
        direction=direction,
        rotation=rotation,
        )]

    layout = go.Layout(
        margin={'l':0, 'r':0, 't':0, 'b':0},
        width=80,
        height=80,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            {
                "font": {"size": 20, "color":"rgb(204, 255, 255)"},
                "showarrow": False,
                "text": value,
                "align": "center",
            },
        ],
    )
    return {"data": data, "layout": layout}


@app.callback(Output('map-graph', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def map_graph(input_, dff=df):

    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-1', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def kpi_1(input_, dff=df):
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-2', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def kpi_2(input_, dff=df):
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-3', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def kpi_3(input_, dff=df):
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-4', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def kpi_4(input_, dff=df):
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-5', 'figure'),[Input(component_id='location-dropdown-1', component_property='value')])
def kpi_5(input_, dff=df):
    return circle_number(random.randint(1,99))

# # GRAPH 2 : DISPO A DATE
# @app.callback(
#     Output('dispo_a_date', 'figure'),
#     [Input('picker_single', 'date')] + values.input_)
# def dispo_date_(date, model, origin, finition, geography, df_m=rep['df_maintenance_small'], df_car=rep['df_caracteristique_total']):
    # result = {}
    # for mod in model:
    #     dff = filter_and_compute.filterVehicle(df_car, [mod], origin, finition, dept=geography)
    #     mr = filter_and_compute.getPctDispoADate(df_m, dff, d=str(date))
    #     result[mod] = mr['pct_dispo']
    
    # data = [go.Bar(y=[mod for mod in result.values()],
    #                x=[mod for mod in result.keys()],
    #                text=[mod for mod in result.values()],
    #                textposition = 'auto')]

    # layout = go.Layout(
    #     barmode="stack",
    #     margin=dict(l=35, r=25, b=30, t=30, pad=10),
    #     paper_bgcolor="white",
    #     plot_bgcolor="white",
    #     title="Taux de disponibilité à date"
    # )

    # return {"data": data, "layout": layout}



############################################################################################
######################################### RUNNING ##########################################
############################################################################################


if __name__ == '__main__':
    app.run_server(debug=True)