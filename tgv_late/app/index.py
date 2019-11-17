import dash
import dash_daq as daq
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

mapbox_access_token = f.get_token('../../dash.token')


        

############################################################################################
######################################### DATA PREP ########################################
############################################################################################

# Loading necessary data
df = f.load_pickle('dash_first_try.p')
gares = df.pipe(f.get_gares)
print(df.head())

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


def NamedDropdown(name, **kwargs):
    return html.Div(
        style={"margin": "10px 0px"},
        children=[
            html.P(children=f"{name}:", style={"margin-left": "3px"}),
            dcc.Dropdown(**kwargs),
        ],
    )

def simpleButton(name, **kwargs):
    return html.Div(
        style={"margin": "10px 0px"},
        children=[
            daq.PowerButton(**kwargs)
        ],
    )


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
                    # src="./tgv_late/app/img/logo_SNCF.svg",
                    # src="./img/logo_SNCF.svg",
                    width=200,
                ),
                html.H2("OPEN DATA"),
                html.P(
                    """Analyse des retards des TGVs entre 2016 et 2019.
                    """
                ),
                simpleButton(name='all-gare', id='my-daq-powerbutton', on=True),
                html.Br(),
                NamedDropdown(
                    name="Gare de départ ",
                    id="gare-depart",
                    options=[
                        {"label": i, "value": i}
                        for i in gares
                    ],
                    placeholder="Gare de départ",
                    value='PARIS MONTPARNASSE',
                    # clearable=False,
                    # searchable=False,
                ),
                NamedDropdown(
                    name="Gare d'arrivée ",
                    id="gare-arrivee",
                    options=[
                        {"label": i, "value": i}
                        for i in gares
                    ],
                    placeholder="Gare d'arrivée",
                    value='BORDEAUX ST JEAN',
                    # clearable=False,
                    # searchable=False,
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
                                
                                html.Div(children=[dcc.Graph(id='kpi-1'),html.Span('Trains prévus')]),
                                html.Div(children=[dcc.Graph(id='kpi-2'),html.Span('Trains retardés')]),
                                html.Div(children=[dcc.Graph(id='kpi-3'),html.Span('Trains annulés')]),
                                html.Div(children=[dcc.Graph(id='kpi-4'),html.Span('Retard moyen')]),
                                html.Div(children=[dcc.Graph(id='kpi-5'),html.Span('Retard cumulé')]),
                                # dcc.Graph(id='kpi-2'),
                                # dcc.Graph(id='kpi-3'),
                                # dcc.Graph(id='kpi-4'),
                                # dcc.Graph(id='kpi-5')
                            ]
                        ),
                        # html.Div(
                        #     className='KPItitle',
                        #     children=[
                        #         html.P('kpi1'),
                        #         html.P('kpiiiiiiiiiiii2'),
                        #         html.P('kpi3'),
                        #         html.P('kpi4'),
                        #         html.P('kpi5'),
                        #     ]
                        # ),
                        html.Div(
                            className='TimeSelector',
                            children=[
                                # html.P('Time Selector'),
                                dcc.RangeSlider(
                                    id='time-filter',
                                    min=min_date,
                                    max=max_date,
                                    step=1,
                                    marks=marks_data,
                                    value=min_max_date_value
                                ),
                                # html.P('')
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
                                dcc.RadioItems(
                                    id='choix-distribution-retard',
                                    options=[
                                        {'label': 'Nombre de trains', 'value': 'train'},
                                        {'label': 'Nombre de minutes', 'value': 'minute'},
                                    ],
                                    value='train',
                                ),
                                dcc.RadioItems(
                                    id='couleur-distribution-retard',
                                    options=[
                                        {'label': 'Par année', 'value': 'an'},
                                        {'label': 'Par gare d\'arrivée', 'value': 'gare'},
                                    ],
                                    value='an',
                                ),
                                dcc.Graph(id="distribution-retard"),
                                html.P("Select any of the bars on the histogram to section data by time."),
                                dcc.Graph(id='cause-retard'),
                                
                            ],
                        ),
                        html.Article(
                            className='rightMap',
                            children=[
                                dcc.Graph(id='map-graph', config={ "scrollZoom": True}),
                                # html.Div(
                                #     id="map-description",
                                #     children=[
                                #         "La liste des commentaires apparaitra ici", html.Br(),
                                #         "Select any of the bars on the histogram to section data by time.",
                                #         dcc.Graph(id='individual_graph')

                                #     ]
                                # )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

############################################################################################
#########################################  FONCTIONS #######################################
############################################################################################


def filter_df(df, depart=None, arrivee=None, time_filter=None):
    dff = df.copy()
    start, end = None, None
   
    print('> FILTERING', dff.shape)
    print('-', depart, arrivee, start, end)
    if time_filter:
        print(time_filter)
        start = pd.to_datetime(str(time_filter[0]))
        end = pd.to_datetime(str(time_filter[1]))

    print(start, end)
    if depart:
        dff = dff[dff['gare_depart']==depart]
        print('depart', dff.shape)
    if arrivee:
        dff = dff[dff['gare_arrivee']==arrivee]
        print('arrivee', dff.shape)
    if start:
        print('start', dff.shape)
        dff = dff[dff['periode']>=start]
    if end:
        print('end', dff.shape)
        dff = dff[dff['periode']<=end]
    print('final', dff.shape)
    return dff

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


############################################################################################
######################################### CALLBACKS ########################################
############################################################################################

input_list =[
    Input(component_id='gare-depart', component_property='value'),
    Input(component_id='gare-arrivee', component_property='value'),
    Input(component_id='time-filter', component_property='value')
]


@app.callback([Output('gare-arrivee', 'options'),Output('gare-arrivee', 'value')],
    [Input(component_id='gare-depart', component_property='value')])
def reselect_arrivee(depart, dff=df):
    print('> Arrival selection (from {})'.format(depart))
    gare_arrivee = df.pipe(f.get_gare_complement, depart)
    return [{"label": i, "value": i} for i in gare_arrivee], gare_arrivee[0]


##############################
# GRAPHIQUES
##############################
@app.callback(Output('distribution-retard', 'figure'),
    input_list + [
        Input(component_id='choix-distribution-retard', component_property='value'),
        Input(component_id='couleur-distribution-retard', component_property='value')])
def distribution_retard(depart, arrivee, time_filter, choix_radio, couleur, dff=df):
    print('> Graphique 1 : Distribution Retard')
    dff = df.pipe(filter_df, depart, arrivee, time_filter)
    
    # Select axes
    x = dff['nbr_trains_retard_depart'].tolist()
    if choix_radio=='train':
        y = dff['nbr_trains_retard_arrivee'].tolist()
    else: # choix==minute
        y = dff['retard_moyen_trains_retard_arrivee__min'].tolist()
    
    # Select color_scheme
    if couleur=='an':
        colors = dff.pipe(f.transform_category_to_color, 'annee').tolist()
    else: # couleur==gare
        colors = dff.pipe(f.transform_category_to_color, 'gare_arrivee').tolist()

    data=[
        go.Scatter(
            x=x,
            y=y,
            mode='markers',
            marker=dict(color=colors,)#     size=[40, 60, 80, 100],
        )
    ]
    
    margin=40
    layout=go.Layout(
        margin={'l': margin,'b': margin,'t': margin,'r': margin}
    )
    return {"data": data, "layout": layout}


@app.callback(Output('cause-retard', 'figure'),input_list)
def cause_retard(depart, arrivee, time_filter, dff=df):
    print('> Graphique 2 : Cause Retard')
    cause_retard = (df
        .pipe(filter_df, depart, arrivee, time_filter)
        .pipe(f.get_root_cause)
    )
    
    causes = list(cause_retard.keys())
    values = list(cause_retard.values())

    colors = ['lightslategray',] * len(causes)
    max_index = values.index(max(values))
    colors[max_index] = 'crimson'

    data=[go.Bar(
        x= causes,
        y= values,
        marker_color=colors 
    )]

    margin=20
    layout=go.Layout(
        margin={'l': margin,'b': margin,'t': margin,'r': margin}
    )
    return {"data": data, "layout": layout}



##############################
# KPIS
##############################



@app.callback(Output('kpi-1', 'figure'),[Input(component_id='time-filter', component_property='value')])
def kpi_1(input_, dff=df):
    print('> KPI 1')   
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-2', 'figure'),[Input(component_id='gare-depart', component_property='value')])
def kpi_2(input_, dff=df):
    print('> KPI 2')
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-3', 'figure'), input_list)
def kpi_3(depart, arrivee,time_filter, dff=df):
    print('> KPI 3')
    print(time_filter)
    dff = df.pipe(filter_df, depart, arrivee, time_filter)
    nombre_retard = dff['nbr_trains_retard_arrivee'].sum()
    circle = circle_number(nombre_retard)
    return circle

@app.callback(Output('kpi-4', 'figure'),[Input(component_id='gare-depart', component_property='value')])
def kpi_4(input_, dff=df):
    return circle_number(random.randint(1,99))

@app.callback(Output('kpi-5', 'figure'),[Input(component_id='gare-arrivee', component_property='value')])
def kpi_5(input_, dff=df):
    return circle_number(random.randint(1,99))


##############################
# MAP
##############################



layout_map = dict(
    # autosize=True,
    # height=750,
    font=dict(color='#7FDBFF'),
    titlefont=dict(color='#7FDBFF', size='22'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    showlegend=True,
    legend=dict(font=dict(size=20), orientation='h'),
    title="Vue cartographique",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="dark",
        center=dict(
            lon=2.333333,
            lat=48.866667
        ),
        zoom=6,
    )
)


@app.callback(Output('map-graph', 'figure'),
                input_list
            #   [Input("affichage", "values"),
            #    Input("origine_dropdown", "value")],
            #   [State('main_graph', 'relayoutData')]
              )
# def make_main_figure(affichage,origine, main_graph_layout, df_car=rep_new['vehicules_actifs'], df_ateliers=rep_new['ateliers']):
def make_main_figure(debut, fin, time_, dff=df):
    gare_position = f.load_pickle('gare_gps.p')
    df_gare = pd.DataFrame(
        {
            'gare':[key for key in gare_position.keys()],
            'latitude':[value['latitude'] for value in gare_position.values()],
            'longitude':[value['longitude'] for value in gare_position.values()],
            'adresse':[value['location_adress'] for value in gare_position.values()]
        }
    ).set_index('gare')
    print(df_gare.head())

    lat_atelier = df_gare['latitude'].to_list()
    lon_atelier =  df_gare['longitude'].to_list()
    noms_ateliers = df_gare['adresse'].to_list()

    trace = dict(
        type='scattermapbox',
        lon=lon_atelier,
        lat=lat_atelier,
        text=noms_ateliers,
        name = "Gares",
        # customdata=customdata,
        marker=dict(
            size=15,
            color='#BFD3E6',
            opacity=0.7
        )
    )

    figure = dict(data=[trace], layout=layout_map)
    return figure


############################################################################################
######################################### RUNNING ##########################################
############################################################################################


if __name__ == '__main__':
    app.run_server(debug=True)