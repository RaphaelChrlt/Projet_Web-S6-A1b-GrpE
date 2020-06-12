    # -*- coding: utf-8 -*-
"""
Created on Fri June 12 10:39:59 2020

@author: Marin Siron
"""

## #%% Importations générales

import os

# os.chdir("CHEMIN A CHANGER SI BESOIN")



import sqlite3
import re
import json
from zipfile import ZipFile





## #%% CODE GENERAL



def get_info(country, continent):

    with ZipFile('{}.zip'.format(continent), 'r') as z:

        # liste des documents contenus dans le fichier zip

        # print(z.namelist())
        # print()

        # infobox de l'un des pays
        info = json.loads(z.read('{}.json'.format(country)))


        return info


#======================================
def get_names(wp_info):
    """ Récupération du/des nom(s) complet(s) d'un pays depuis l'infobox wikipédia. Renvoie une liste contenant le nom conventionnel du pays ainsi que son nom commun """

    pas_trouve = True       #Si aucun nom n'est trouvé

    # cas général
    if 'conventional_long_name' in wp_info:

        pas_trouve=False    #Au moins un nom a été trouvé

        name_cl = wp_info['conventional_long_name']

        # si le nom est composé de mots avec éventuellement des espaces,
        # des virgules et/ou des tirets, situés devant une double {{ ouvrante,
        # on conserve uniquement la partie devant les {{
        m = re.match("([\w, -]+?)\s*{{",name_cl)
        if m:
            name_cl = m.group(1)

        # si le nom est situé entre {{ }} avec un caractère séparateur |
        # on conserve la partie après le |
        m = re.match("{{.*\|([\w, -]+)}}",name_cl)
        if m:
            name_c = m.group(1)
        # return name
    else:
        name_cl = None

    if 'common_name' in wp_info:

        pas_trouve=False    #Au moins un nom a été trouvé

        name_c = wp_info['common_name']
        # print( 'using common name {}...'.format(name),end='')
        # return name
    else:
        name_c = None

    if pas_trouve:
        # Aveu d'échec, on ne doit jamais se retrouver ici
        print('Could not fetch country name {}'.format(wp_info))
        return None

    elif name_cl==None and name_c!=None:    #Cas où l'un des deux n'existe pas.
        return [name_c,name_c]

    elif name_c==None and name_cl!=None:    #Cas où l'un des deux n'existe pas.
        return [name_cl,name_cl]

    return [name_cl,name_c]                 #Cas où les deux noms existent.


#======================================

def get_capitale(wp_info):
    """ Retourne la capitale d'un pays """
    # cas général

    if 'capital' in wp_info:



        # parfois l'information récupérée comporte plusieurs lignes

        # on remplace les retours à la ligne par un espace

        capital = wp_info['capital'].replace('\n',' ')



        # le nom de la capitale peut comporter des lettres, des espaces,

        # ou l'un des caractères ',.()|- compris entre crochets [[...]]

        m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", capital)



        # on récupère le contenu des [[...]]

        capital = m.group(1)



        # si on tombe sur une valeur avec des séparateurs |

        # on prend le premier terme

        if '|' in capital:

            capital = capital.split('|').pop()



        # Cas particulier : Singapour, Monaco, Vatican

        if ( capital == 'city-state' ):

            capital = wp_info['common_name']



        # Cas particulier : Suisse

        if ( capital == 'de jure' and wp_info['common_name'] == 'Switzerland'):

            capital = 'Bern'


        return capital



    # FIX manuel (l'infobox ne contient pas l'information)

    if 'common_name' in wp_info and wp_info['common_name'] == 'Palestine':

        return 'Ramallah'



    # Aveu d'échec, on ne doit jamais se retrouver ici

    print(' Could not fetch country capital {}'.format(wp_info))

    return None

#======================================

def get_flag(wp_info):
    """ Retourne le nom du drapeau à récupérer pour l'afficher """
    #Récupération du nom commun. Pour se conformer au formatage, on utilise un underscore.
    nom_commun = get_names(wp_info)[1].replace(' ','_')

    with ZipFile('flags.zip', 'r') as z:
    # cas général
        liste_noms = z.namelist()
        for i, nom in enumerate(liste_noms):    #Itérateur utile par la suite.
            if nom_commun.lower() in nom :      #Les noms sont en minuscule.
                # return "{}.png".format(nom) #Cette ligne n'est pas nécessaire.
                return nom
        print("Le drapeau n'a pas été trouvé")
        return None


#======================================

def get_coords(wp_info):
    """ Récupération des coordonnées de la capitale depuis l'infobox d'un pays """
    # S'il existe des coordonnées dans l'infobox du pays (cas le plus courant)
    if 'coordinates' in wp_info:

        # (?i) - ignorecase - matche en majuscules ou en minuscules
        # ça commence par "{{coord" et se poursuit avec zéro ou plusieurs espaces suivis par une barre "|"
        # après ce motif, on mémorise la chaîne la plus longue possible ne contenant pas de },
        # jusqu'à la première occurence de "}}"
        m = re.match('(?i).*{{coord\s*\|([^}]*)}}', wp_info['coordinates'])

        # l'expression régulière ne colle pas, on affiche la chaîne analysée pour nous aider
        # mais c'est un aveu d'échec, on ne doit jamais se retrouver ici
        if m == None :
            print(' Could not parse coordinates info {}'.format(wp_info['coordinates']))
            return None

        # cf. https://en.wikipedia.org/wiki/Template:Coord#Examples
        # on a récupère une chaîne comme :
        # 57|18|22|N|4|27|32|W|display=title
        # 44.112|N|87.913|W|display=title
        # 44.112|-87.913|display=title
        str_coords = m.group(1)

        # on convertit en numérique et on renvoie
        if str_coords[0:1] in '0123456789':
            return cv_coords(str_coords)

    # FIX manuel (l'infobox ne contient pas d'information directement exploitable)
    if 'common_name' in wp_info and wp_info['common_name'] == 'the Philippines':
        return cv_coords('14|35|45|N|120|58|38|E')
    if 'common_name' in wp_info and wp_info['common_name'] == 'Tanzania':
        return cv_coords('6|10|23|S|35|44|31|E')


    # A FAIRE
    # # On n'a pas trouvé de coordonnées dans l'infobox du pays
    # # on essaie avec la page de la capitale
    # capitale = get_capitale(wp_info)
    # if capital:
    #     print(' Fetching capital coordinates...')
    #     return get_coords(get_info(capitale))

    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country coordinates')
    return {'lat' : 'None','lon' : 'None'}



#======================================

def cv_coords(str_coords):
    """ Conversion d'une chaîne de caractères décrivant une position géographique en coordonnées numériques latitude et longitude """
    # on découpe au niveau des "|"
    c = str_coords.split('|')

    # on extrait la latitude en tenant compte des divers formats
    lat = float(c.pop(0))
    if (c[0] == 'N'):
        c.pop(0)
    elif ( c[0] == 'S' ):
        lat = -lat
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'N' ):
        lat += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'S' ):
        lat += float(c.pop(0))/60
        lat = -lat
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'N' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'S' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        lat = -lat
        c.pop(0)

    # on fait de même avec la longitude
    lon = float(c.pop(0))
    if (c[0] == 'W'):
        lon = -lon
        c.pop(0)
    elif ( c[0] == 'E' ):
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'W' ):
        lon += float(c.pop(0))/60
        lon = -lon
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'E' ):
        lon += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'W' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        lon = -lon
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'E' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        c.pop(0)

    # on renvoie un dictionnaire avec les deux valeurs
    return {'lat':lat, 'lon':lon }



## #%% Méthodes de sauvegarde


def save_global(conn,country,continent):
    """ Cette fonction se charge de la sauvegarde des informations générales d'un pays dans la table concernée """
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO global VALUES (?, ?, ?, ?, ?, ?, ?, ?)'

    # vérification de la syntaxe pour les pays au nom composé :

    country = country.replace(' ','_')

    # récupération des données du pays :

    info = get_info(country,continent)

    # les infos à enregistrer
    nom_conventionnel = get_names(info)[0]
    nom_commun = get_names(info)[1]
    capitale = get_capitale(info)
    coords = get_coords(info)
    drapeau = get_flag(info)
    adresse_wiki = 'INCONNUE'

    print(nom_conventionnel)
    print(nom_commun)
    print(capitale)
    print(coords)
    print(drapeau)
    print(adresse_wiki)

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(nom_conventionnel, nom_commun, capitale, continent, drapeau, coords['lat'], coords['lon'], adresse_wiki))
    conn.commit()

def save_demographie(conn, country, info):
    """ Cette fonction se charge de la sauvegarde des informations sur la démographie d'un pays dans la table concernée """
    pass

def save_politique(conn, country, info):
    """ Cette fonction se charge de la sauvegarde des informations sur la politique d'un pays dans la table concernée """
    pass

def save_miscellaneous(conn, country, info):
    """ Cette fonction se charge de la sauvegarde des informations en vrac d'un pays dans la table concernée """
    pass

def save_economie(conn, country, info):
    """ Cette fonction se charge de la sauvegarde des informations sur l'économie d'un pays dans la table concernée """
    pass


## #%% Génération de la table "global" :


for continent in ['oceania', 'south_america']:

    with ZipFile('{}.zip'.format(continent), 'r') as z:

        for pays in z.namelist():
            pays = pays.replace('.json','')
            print("\n =============== {} ================".format(pays))
            wp = get_info(pays,continent)

            save_global(conn,pays,continent)


## #%% TESTS PARTIELS EN VRAC :

# TESTS D'ACCESSIONS AUX FICHIERS DE DONNEES BRUTES



for continent in ['oceania', 'south_america']:

    with ZipFile('{}.zip'.format(continent), 'r') as z:

        for pays in z.namelist():
            pays = pays.replace('.json','')
            print("\n =============== {} ================".format(pays))
            wp = get_info(pays,continent)
            noms = get_names(wp)
            capitales = get_capitale(wp)

            # Traitement ultérieur à faire pour chaque pays à ajouter à la base de données

            print(wp)



print("\n =============== \n")
print(get_names(get_info('Venezuela','south_america')))
print(get_flag(get_info('Venezuela','south_america')))

newz = get_info('New_Zealand','oceania')
print(get_names(newz))
print(get_capitale(newz))
print(get_coords(newz))
print(get_flag(newz))

print("\n =============== \n")

# TEST SUR LA NOUVELLE-ZELANDE

#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('pays.sqlite')

# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

# print(conn.cursor().execute("SELECT * FROM global"))
# print(conn.cursor().execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT,age INTERGER)"))


save_global(conn,'New Zealand','oceania')
