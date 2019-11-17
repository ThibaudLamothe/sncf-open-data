############################################################################################
########################################## IMPORTS #########################################
############################################################################################


# Import classic lib
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime as dt

# Import dash library and related ones
import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go

# Import logging
import logging
import logzero
from logzero import logger

# Importing personnal functions 
sys.path.append('/Users/thibaud/Documents/Python_scripts/02_Projects/SNCF/open_data/')
import sncf_utils as f


############################################################################################
#################################### APP INITIATION ########################################
############################################################################################

# Creating app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Creating server
server = app.server

# Initiating logger
logzero.loglevel(logging.DEBUG)
# logger.debug("Debug")
# logger.info("Info")
# logger.warning("Warning")
# logger.error("Error")
        
# Display app start
logger.error('*'*80)
logger.error('Initialisation de l\'Application')
logger.error('*'*80)

############################################################################################
########################################## LOADING #########################################
############################################################################################

# Loading map token
mapbox_access_token = f.get_token('../../dash.token')

# Loading main data
df = f.load_pickle('dash_first_try.p')
logger.info(df.head())

# Loading gare information
gare_position = f.load_pickle('gare_gps.p')
df_gare = pd.DataFrame(
    {
        'gare':[key for key in gare_position.keys()],
        'latitude':[value['latitude'] for value in gare_position.values()],
        'longitude':[value['longitude'] for value in gare_position.values()],
        'adresse':[value['location_adress'] for value in gare_position.values()]
    }
).set_index('gare')
    
# Computing gare liste
gares = df.pipe(f.get_gares)
logger.info(gares)

# Setting date for application purpose
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
####################################### COMPONENTS #########################################
############################################################################################


def NamedDropdown(name, **kwargs):
    return html.Div(
        style={"margin": "10px 0px"},
        children=[
            html.P(children=f"{name}", style={"margin-left": "3px"}),
            dcc.Dropdown(**kwargs),
        ],
    )

def OnOffButton(name, **kwargs):
    return html.Div(
        #style={"margin": "auto"},
        children=[
            daq.PowerButton(**kwargs)
        ],
    )

def simpleButton(name, **kwargs):
    return html.Div(
        #style={"margin": "auto"},
        children=[
            daq.StopButton(**kwargs)
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
                html.Div(
                    className='card',
                    id='img-card',
                    children=[
                        html.Img(
                            className="logo",
                            src="https://upload.wikimedia.org/wikipedia/fr/f/f7/Logo_SNCF_%282005%29.svg",
                            # src="./tgv_late/app/img/logo_SNCF.svg",
                            # src="./img/logo_SNCF.svg",
                            width=220,
                        ),
                    ]
                ),
                html.Div(
                    className='card',
                    id='upper-card',
                    children=[
                        html.H2("OPEN DATA"),
                        html.P(
                            """Analyse des retards des TGVs entre 2016 et 2019
                            """
                        ),
                        simpleButton(name='all-gare', id='reset-button', buttonText='RESET'),#, on=True),
                    ]
                ),            
                html.Div(
                    className='card',
                    id='analyse-card',
                    children=[
                        html.H3('Analyse complémentaire'),
                        NamedDropdown(
                            name="Gare de départ ",
                            id="gare-depart",
                            options=[
                                {"label": i, "value": i}
                                for i in gares
                            ],
                            placeholder="Gare de départ",
                            # value='PARIS MONTPARNASSE',
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
                            # value='BORDEAUX ST JEAN',
                            # clearable=False,
                            searchable=True,
                        ),
                        simpleButton(name='valider', id='valider-button', buttonText='Valider',),#, on=True),
                    ]
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
                            className='upperKPIFake',
                            children=[                        
                                dcc.Loading(
                                    className='KPIs',
                                    children=[                           
                                        html.Div(children=[dcc.Graph(id='kpi-1'),html.Span('Trains prévus')], className='rond_cercle'),
                                        html.Div(children=[dcc.Graph(id='kpi-2'),html.Span('Trains retardés')], className='rond_cercle'),
                                        html.Div(children=[dcc.Graph(id='kpi-3'),html.Span('Trains annulés')], className='rond_cercle'),
                                        html.Div(children=[dcc.Graph(id='kpi-4'),html.Span('Retard moyen (min)')], className='rond_cercle'),
                                        html.Div(children=[dcc.Graph(id='kpi-5'),html.Span('Retard cumulé (h)')], className='rond_cercle'),
                                    ],
                                    color='crimson',
                                    type="circle",
                                ),
                                html.Div(
                                    className='TimeSelector',
                                    style={'color':'crimson'},
                                    children=[
                                        dcc.RangeSlider(
                                            id='time-filter',
                                            min=min_date,
                                            max=max_date,
                                            step=1,
                                            marks=marks_data,
                                            value=min_max_date_value,
                                            # color='crimson',                                            
                                        ),
                                    ],
                                ),
                            ]
                        )
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
                                    className='leftUpper',
                                    children=[
                                        dcc.Graph(id="distribution-retard"),
                                        html.Div(
                                            className='radioGraph',
                                            children=[
                                                html.P('Axe des y'),
                                                dcc.RadioItems(
                                                    className='radioButton',
                                                    inputClassName='radio',
                                                    labelClassName='label',
                                                    labelStyle={'display': 'inline-block'},
                                                    id='choix-distribution-retard',
                                                    options=[
                                                        {'label': 'Nombre de trains', 'value': 'train'},
                                                        {'label': 'Nombre de minutes', 'value': 'minute'},
                                                    ],
                                                    value='train',
                                                ),
                                                html.P('Méthode de coloration'),
                                                dcc.RadioItems(
                                                    className='radioButton',
                                                    inputClassName='radio',
                                                    labelClassName='label',
                                                    labelStyle={'display': 'inline-block'},
                                                    id='couleur-distribution-retard',
                                                    options=[
                                                        {'label': 'Par année', 'value': 'an'},
                                                        {'label': 'Par gare d\'arrivée', 'value': 'gare'},
                                                    ],
                                                    value='an',
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className='leftDown',
                                    children=[
                                        dcc.Graph(id='cause-retard'),
                                        dcc.Graph(id='duree-retard'),
                                    ]
                                ),                
                            ],
                        ),
                        html.Article(
                            className='rightMap',
                            children=[
                                dcc.Loading(
                                    id="loading-3",
                                    children=[dcc.Graph(id='map-graph', config={ "scrollZoom": True}),],
                                    type="circle",
                                    color='crimson'
                                ),
                                html.Div(
                                    id="map-description",
                                    children=[
                                        "La liste des commentaires apparaitra ici", html.Br(),
                                        #dcc.Graph(id='individual_graph')
                                    ]
                                ),
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


def circle_number(value, max_value=100):
    values = [max_value-value,value]
    colors = ['rgba(0, 0, 0,0)', "crimson"]#"rgb(204, 255, 255)"]
    direction='clockwise'    
    rotation=0 if value>=max_value/2 else 360/max_value*value

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
        width=70,
        height=70,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            {
                "font": {"size": 15, "color":"crimson"},
                "showarrow": False,
                "text": value,
                "align": "center",
            },
        ],
    )
    return {"data": data, "layout": layout}


def filter_df(df, depart=None, arrivee=None, time_filter=None):
    logger.info('> FILTERING - taille du dataset {}'.format(df.shape))
    logger.info('- Depart : {} - Arrivée : {}'.format(depart, arrivee))
   
    # Initialisation & interprésttion des dates
    dff = df.copy()
    start, end = None, None     
    if time_filter:
        logger.debug('Time filter : {}'.format(time_filter))
        start = pd.to_datetime(str(time_filter[0]))
        end = pd.to_datetime(str(time_filter[1]))
    logger.info('Date selectionnées : Start : {} - End : {}'.format(start, end))
    
    # Filtres consécutifs
    if depart:
        dff = dff[dff['gare_depart']==depart]
        logger.debug('Taille post-depart : {}'.format(dff.shape))
    if arrivee:
        dff = dff[dff['gare_arrivee']==arrivee]
        logger.debug('Taille post-arrivee {}'.format(dff.shape))
    if start:
        dff = dff[dff['periode']>=start]
        logger.debug('Taille post-start {}'.format(dff.shape))
    if end:
        dff = dff[dff['periode']<=end]
        logger.debug('Taille post-end {}'.format(dff.shape))
    
    # Filtres effectués
    logger.debug('Taille finale {}'.format(dff.shape))
    return dff


############################################################################################
#################################### CALCULATIONS ##########################################
############################################################################################


##############################
# DISTRIBUTION DES RETARDS
##############################
def make_distribution_retard(dff, choix_radio, couleur):
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
    return x, y, colors


##############################
# CAUSE DES RETARDS
##############################
def make_cause_retard(df, depart, arrivee):
    logger.info('> GRAPHIQUE 2 : Distribution Retard')
    cause_retard = df.pipe(f.get_root_cause)

    causes = list(cause_retard.keys())
    values = list(cause_retard.values())

    colors = ['#1E1E1E',] * len(causes)
    max_index = values.index(max(values))
    colors[max_index] = 'crimson'

    data=[go.Bar(x=causes, y=values, marker_color=colors)]
    layout=go.Layout(
        margin={'l': 25,'b': 25,'t': 25,'r': 25},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title='Origine des retards',
        )
    return {"data": data, "layout": layout}


##############################
# DUREE DES RETARDS
##############################
def make_duree_retard(df, depart, arrivee):
    logger.info('> GRAPHIQUE 2 : Duree Retard')
    cause_retard = df.pipe(f.get_root_cause)

    causes = list(cause_retard.keys())
    values = list(cause_retard.values())

    colors = ['#1E1E1E',] * len(causes)
    max_index = values.index(max(values))
    colors[max_index] = 'crimson'

    data=[go.Bar(x=causes, y=values, marker_color=colors)]
    layout=go.Layout(
        margin={'l': 25,'b': 25,'t': 25,'r': 25},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title='Durée des retards',
        )
    return {"data": data, "layout": layout}


##############################
# CREATION DE LA CARTE
##############################
def make_map(depart, arrivee, df_gare=df_gare):
    logger.info('> Generating map')
    
    # Always the same
    lat_atelier = df_gare['latitude'].to_list()
    lon_atelier =  df_gare['longitude'].to_list()
    noms_ateliers = df_gare['adresse'].to_list()

    # Depend on gare de depart et d'arrivee
    colors = ['crimson' if gare in [depart, arrivee] else 'rgb(205, 205, 206)' for gare in gare_position.keys()]
    size = [30 if gare in [depart, arrivee] else 15 for gare in gare_position.keys()]
    
    trace_map = dict(
        type='scattermapbox',
        lon=lon_atelier,
        lat=lat_atelier,
        text=list(gare_position.keys()),#noms_ateliers,
        name = "Gares",
        marker=dict(size=size,color=colors,opacity=0.7),
         # customdata=customdata,
    )

    layout_map = dict(
        # autosize=True,
        # height=750,   
        font=dict(color='#1E1E1E'),
        titlefont=dict(color='#1E1E1E', size='22'),
        margin=dict(l=15,r=15,b=15,t=35),
        hovermode="closest",
        border=dict(color='#1E1E1E'),
        # plot_bgcolor="#191A1A",
        # paper_bgcolor="#020202",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        # showlegend=True,
        # legend=dict(font=dict(size=20), orientation='h'),
        title="Vue cartographique",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style="dark",
            center=dict(lon=2.33,lat=46.8),
            zoom=4.4,
        )
    )
    return dict(data=[trace_map], layout=layout_map)

############################################################################################
################################# GENERAL CALLBACKS ########################################
############################################################################################


##############################
# MISE A JOUR DES GARES D'ARRIVEE DISPONIBLES
##############################
@app.callback([
    Output('gare-arrivee', 'options'),
    Output('gare-arrivee', 'value')],
    [Input(component_id='gare-depart', component_property='value')])
def reselect_arrivee(depart, dff=df):
    logger.info('> SELECT arrivee - gare de départ {}'.format(depart))    
    if depart:
        gare_arrivee_list = df.pipe(f.get_gare_complement, depart)
        gare_displayed = gare_arrivee_list[0]
    else:
        gare_arrivee_list = df.pipe(f.get_gares)
        gare_displayed = None
    return [{"label": i, "value": i} for i in gare_arrivee_list], gare_displayed


##############################
# RESET DU CHOIX DES GARES
##############################
@app.callback([Output('gare-depart', 'value'), Output(component_id='time-filter', component_property='value')],
    [Input(component_id='reset-button', component_property='n_clicks')])
def reset_gare(n_click, dff=df):
    logger.info('> RESET : suppression des filtres')
    logger.info(n_click)
    return [None, [2014,2019]]


##############################
# FIGURE CALLBACKS
##############################
@app.callback(
    [
        Output('kpi-1', 'figure'),
        Output('kpi-2', 'figure'),
        Output('kpi-3', 'figure'),
        Output('kpi-4', 'figure'),
        Output('kpi-5', 'figure'),
        Output('cause-retard', 'figure'),
        Output('duree-retard', 'figure'),
        Output('map-graph', 'figure')
    ],
    [
        Input(component_id='valider-button', component_property='n_clicks'),
        Input(component_id='reset-button', component_property='n_clicks'),
        Input(component_id='time-filter', component_property='value')
    ],
    [
        State(component_id='gare-depart', component_property='value'),
        State(component_id='gare-arrivee', component_property='value'),
    ]
)
def update(n_click_val, n_click_reset, time_filter, depart, arrivee, dff=df):
    logger.info('> MULITPLE CREATION : KPIs + Carte')
    logger.debug(time_filter)
    
    # Filtering 
    dff = df.pipe(filter_df, depart, arrivee, time_filter)
    
    # Kpi preparation
    nombre_prevu = int(dff['nbr_circulations_prevues'].sum())
    nombre_retard = int(dff['nbr_trains_retard_arrivee'].sum())
    nombre_annule = int(dff['nbr_trains_annules'].sum())
    retard_moyen = np.round(dff['retard_moyen_trains_retard_arrivee__min'].mean(), 2)
    retard_cumule = int(retard_moyen * nombre_retard / 60)
    
    kpi1 = circle_number(nombre_prevu, max_value=nombre_prevu)
    kpi2 = circle_number(nombre_retard, max_value=nombre_prevu)
    kpi3 = circle_number(nombre_annule, max_value=nombre_prevu)
    kpi4 = circle_number(retard_moyen,retard_moyen)
    kpi5 = circle_number(retard_cumule, retard_cumule)

    # Graphique preparation
    cause_retard = make_cause_retard(dff, depart, arrivee)
    duree_retard = make_duree_retard(dff, depart, arrivee)

    # Map preparation
    carte = make_map(depart, arrivee)

    return kpi1, kpi2, kpi3, kpi4, kpi5, cause_retard, duree_retard,carte



##############################
# DISTRIBUTION RETARDS
##############################
@app.callback(
    Output('distribution-retard', 'figure'),
    [
        Input(component_id='valider-button', component_property='n_clicks'), 
        Input(component_id='reset-button', component_property='n_clicks'),
        Input(component_id='choix-distribution-retard', component_property='value'),
        Input(component_id='couleur-distribution-retard', component_property='value'),
        Input(component_id='time-filter', component_property='value')
    ],
    [
        State(component_id='gare-depart', component_property='value'),
        State(component_id='gare-arrivee', component_property='value'),
    ],
)
def distribution_retard(click_valider, click_reset, choix_radio, couleur, time_filter, depart, arrivee, dff=df):
    logger.info('> GRAPHIQUE 1 : Distribution Retard')
    
    # Prepare data
    dff = df.pipe(filter_df, depart, arrivee, time_filter)
    x, y, colors = make_distribution_retard(dff, choix_radio, couleur)    
    
    # Prepare graph
    data=[
        go.Scatter(
            x=x,
            y=y,
            mode='markers',
            marker=dict(color=colors,)#     size=[40, 60, 80, 100],
        )
    ]
    
    # Make it beautiful
    margin=40
    layout=go.Layout(
        margin={'l': 25,'b': 20,'t': 35,'r': 15},
        # margin={'l': margin,'b': margin,'t': margin,'r': margin},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title='Distribution des retards'
    )
    return {"data": data, "layout": layout}


############################################################################################
######################################### RUNNING ##########################################
############################################################################################

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)