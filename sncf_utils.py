import string as __string
import os as __os
import pickle as __pickle
import numpy as __np
import pandas as __pd
from sklearn.preprocessing import LabelEncoder

DATA_PATH = '/Users/thibaud/Documents/Data/SNCF/'
PICKLE_PATH = DATA_PATH + 'pickle/'


def load_pickle(file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'rb') as pfile:
        my_pickle = __pickle.load(pfile)
    return my_pickle

def save_pickle(object_, file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'wb') as pfile:
        __pickle.dump(object_, pfile, protocol=__pickle.HIGHEST_PROTOCOL)

def list_pickle():
    file_list = __os.listdir(PICKLE_PATH)
    pickle_list = [i for i in file_list if '.p' in i]
    print(pickle_list)

# Version améliorée par rapport à general
def encode_serie(serie):
    lbl = LabelEncoder()
    lbl.fit(serie.apply(str).values)
    serie =lbl.transform(list(serie.apply(str).values)) # Ajout du str (sinon fonctionne pas sur nombre)
    return serie, lbl

def slicer(min_date, max_date):
    step = 1
    if 5 < max_date - min_date <= 10:
        step = 2
    elif 10 < max_date - min_date <= 50:
        step = 5
    elif max_date - min_date > 50:
        step = 10
    marks_data = {}
    for i in range(int(min_date), int(max_date) + 1, step):
        if i > int(max_date):
            marks_data[i] = str(int(max_date))
        else:
            marks_data[i] = str(i)

    if i < int(max_date):
        marks_data[int(max_date)] = str(max_date)

    return marks_data
    

def get_token(path):
    with open(path, 'r') as file:
        api_key= file.read()
    return api_key

def transform_category_to_color(df, col_name, colors=None):
    if colors == None:
        colors = ['red', 'blue', 'green', 'yellow', 'orange'] * 50
    ser = df[col_name]
    ser, _ = encode_serie(ser)
    ser = __pd.Series(ser).apply(lambda x : colors[int(x)])
    return ser

def get_gare(df, nb=1, print_gare=False):
    gares = df['gare_depart'].unique()
    gares.sort()
    gare = gares[nb]
    if print_gare : print(gare)
    return gare

def get_gares(df):
    return df['gare_depart'].unique()

def get_gare_complement(df, gare):
    tmp = df[['gare_depart', 'gare_arrivee']].drop_duplicates()
    tmp = tmp[tmp['gare_depart']==gare]
    gares_cplmt = tmp['gare_arrivee'].unique()
    return gares_cplmt

# A retravailler par unité (la moyenne n'est pas pondérée dans ce calcul)
def get_root_cause(df):
    extern = __np.round(df['retard_causes_externes'].mean())
    infra = __np.round(df['retard_infrastructure_ferroviaire'].mean())
    trafic = __np.round(df['retard_gestion_trafic'].mean())
    matos = __np.round(df['retard_materiel_roulant'].mean())
    gare = __np.round(df['retard_gestion_en_gare_et_reutilisation_de_materiel'].mean())
    voyageurs = __np.round(df['retard_prise_en_compte_voyageurs'].mean())

    # Tests
    # root_cause = df_liaison.pipe(get_root_cause)
    # np.sum(list(root_cause.values()))
    return {'extern':extern, 'infra':infra, 'trafic':trafic, 'matos':matos, 'gare':gare, 'voyageurs':voyageurs}




def transfoCol(ancien, ponctuation=None, accent=None, replacer='_'):
    """Description : simplifie une chaine de caractère en supprimant les majuscules, la ponctuation, les accents et les espaces
    inputs :
        - ancien as string : chaine à modifier
        - ponctuation as list : liste des caractères à retirer
        - accent as dict : dictionnaire des caractères à modifier par un autre
    outputs:
        - string : chaine de caractère modifiée (simplifiée)
    """  
    
    if not ponctuation:
        caracters_to_remove = list(__string.punctuation) + [' ','°']
        ponctuation = {initial:replacer for initial in caracters_to_remove}

    if not accent:
        avec_accent = ['é', 'è', 'ê', 'à', 'ù', 'ç', 'ô', 'î', 'â']
        sans_accent = ['e', 'e', 'e', 'a', 'u', 'c', 'o', 'i', 'a']
        accent = {sans:avec for sans, avec in zip(avec_accent, sans_accent)}
    
    ancien = ancien.lower()
    ancien = ancien.translate(str.maketrans(ponctuation))
    ancien = ancien.translate(str.maketrans(accent))
    double_replacer = replacer + replacer
    while double_replacer in ancien:
        ancien = ancien.replace(double_replacer, replacer)
    
    if ancien[0] ==replacer:
        ancien = ancien[1:]
        
    if ancien[-1] == replacer:
        ancien = ancien[:-1]
    
    return ancien
