# -*- coding: utf-8 -*-
"""
Created on Fri June 12 10:39:59 2020

@author: Marin Siron
"""

## #%% Importations générales

import os

# os.chdir("CHEMIN A CHANGER SI BESOIN")

# os.chdir("C:\\Users\\Marin\\Desktop\\Travail\\Centrale\\S6\\Informatique\\Projet d'application Web\\Projet\\INF tc3 - Projet (sujet)\\client")

"""os.chdir("C:\\Users\\Marin\\Desktop\\Travail\\Centrale\\S6\\Informatique\\Projet d'application Web\\Projet\\Projet_Web-S6-A1b-GrpE\\Serveur")"""

import sqlite3
import re
import json
from zipfile import ZipFile




#=================================== GLOBAL ====================================

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
def get_capitale(pays, wp_info):
    """ Retourne (chaîne) la capitale d'un pays """

    information = 'capitale'
    clef = 'capital'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # On prend les infos se trouvant entre [[ ]]
    p = re.compile("""
                        \[\[        # On supprime [[
                        ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                        \]\]        # On supprime ]]
                       """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "%s: information invalide" % pays
    chaine = m.group(1)

    # Si on tombe sur un nom avec des séparateurs |, on rend le dernier terme
    chaine = chaine.split('|').pop()

    return chaine

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
    lat = '{:.3f}'.format(lat)

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
    lon = '{:.3f}'.format(lon)

    # on renvoie un dictionnaire avec les deux valeurs
    return {'lat':lat, 'lon':lon }

#======================================
def get_adresse_wiki(pays, wp_info):
    
    get_capital = get_capitale(pays, wp_info)
    adresse_wiki = str('https://en.wikipedia.org/wiki/{}'.format(get_capital).replace(' ','_'))
    return adresse_wiki

#=================================== ECONOMIE =================================

#======================================
def get_devise(pays, wp_info):
    """ Retourne (chaine de caractères) la devise d'un pays """

    information = 'devise'
    clef = 'currency'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # Cas où chaine est de la forme
    # ... [[ nom ]] ... [[ nom ]]
    # On prend le 2ème nom, sauf pour l'Argentine où on prend le 1er nom
    p = re.compile("""
                    [^\]]*      # On supprime les caractères jusqu'au ] (non compris)
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                    [^\[]*      # On supprime les caractères jusqu'à [ (non compris)
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 2
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)

    if pays == 'Argentina':
        nom = m.group(1) # 1er nom
    elif m is not None:
        nom = m.group(2) # 2ème nom
    else:
        # Cas où chaine est de la forme
        # ... [[ nom ]]
        # On prend nom
        p = re.compile("""
                        [^\]]*      # On supprime les caractères jusqu'au ] (non compris)
                        \[\[        # On supprime [[
                        ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                        \]\]        # On supprime ]]
                       """, flags=re.VERBOSE)
        m = p.match(chaine)
        if m is None:
            assert False, "{}: {} invalide".format(pays, information)
        nom = m.group(1) # nom

    # Si on tombe sur un nom avec des séparateurs |, on rend le dernier terme
    nom = nom.split('|').pop()
    return nom

#======================================
def get_pib_nominal(pays, wp_info):
    """ Retourne (flottant) le PIB nominal courant d'un pays en dollar"""

    information = 'PIB nominal'
    clef = 'GDP_nominal'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    p = re.compile("""
                    [^0-9]*     # On supprime les caractères alphabétiques
                    ([0-9.]+)   # On garde les chiffres et le . => pib (groupe 1)
                    [^0-9]*     # On supprime les caractères alphabétiques
                    (million|billion|trillion)  # on garde ces mots => unit (groupe 2)
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    pib = float(m.group(1))
    unit = m.group(2)
    if unit == 'million':
        pib *= 10e-3
    elif unit == 'billion':
        pib *= 1
    elif unit == 'trillion':
        pib *= 10e3
    else:
        assert False, "{}: {} invalide".format(pays, information)

    return pib

#======================================
def get_pib_par_tete(pays, wp_info):
    """ Retourne (flottant) le PIB par tête d'un pays en dollar"""

    information = 'PIB par tête'
    clef = 'GDP_nominal_per_capita'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    p = re.compile("""
                    [^\$]*     # On supprime les caractères alphabétiques jusqu'au $
                    \$         # On supprime le $
                    ([0-9.]+)  # On garde les chiffres et le . => pib (groupe 1)
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    pib = float(m.group(1))
    return float(pib)

#=================================== MISCELLANEOUS =================================

#======================================
def get_sens_circulation(pays, wp_info):
    """ Retourne (chaine) le sens de circulation"""

    information = 'sens de circulation'
    clef = 'drives_on'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # S'il y des infos entre [[ ]], on prend celles ci
    p = re.compile("""
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is not None:
        chaine = m.group(1)

    # S'il y des infos entre {{ }}, on les supprime et on garde ce qui précède
    p = re.compile("""
                    ([^{]+)  # On garde tout ce qui précède une accolade => groupe 1
                    {{*      # On supprime tout ce qui suit deux accolades (accolades comprises)
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is not None:
        chaine = m.group(1)

    # S'il y des infos qui suivent <, on les supprime et on garde ce qui précède
    p = re.compile("""
                    ([^<]+)  # On garde tout ce qui précède un < => groupe 1
                    <*       # On supprime tout ce qui suit < (< compris)
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is not None:
        chaine = m.group(1)

    # S'il y a un |, on garde ce qui suit
    p = re.compile("""
                    [^\|]+   # On supprime tout ce qui précède un |
                    \|       # On supprime le |
                    (.+)     # On garde ce qui suit => groupe 1
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is not None:
        chaine = m.group(1)

    return chaine

#======================================
def get_code_appel(pays, wp_info):
    """ Retourne (chaine) le code d'appel"""

    information = "code d'appel"
    clef = 'calling_code'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # chaine est de la forme
    # [[ nom ]]
    # On prend nom
    p = re.compile("""
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    chaine = m.group(1)

    # S'il y a un |, on garde ce qui suit
    p = re.compile("""
                    [^\|]+   # On supprime tout ce qui précède un |
                    \|       # On supprime le |
                    (.+)     # On garde ce qui suit => groupe 1
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is not None:
        chaine = m.group(1)

    return chaine

#======================================
def get_domaine_internet(pays, wp_info):
    """ Retourne (chaine) le domaine internet"""

    information = "domaine internet"
    clef = 'cctld'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # chaine est de la forme
    # [[ nom ]]
    # On prend nom
    p = re.compile("""
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    chaine = m.group(1)

    return chaine

#=================================== POLITIQUE =================================

#======================================
def get_nom_chef_etat(pays, wp_info):
    """ Retourne (chaine) le nom du chef d'etat"""

    information = "nom du chef d'état"
    clef = 'leader_name1'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # Chaine est de la forme
    # ... [[ nom ]] ...
    # On prend nom
    p = re.compile("""
                    [^\]]*      # On supprime les caractères jusqu'au ] (non compris)
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    else:
        chaine = m.group(1)
        # Si on tombe sur un nom avec des séparateurs |, on rend le dernier terme
        chaine = chaine.split('|').pop()

    return chaine

#======================================
def get_type_chef_etat(pays, wp_info):
    """ Retourne (chaine) le type de chef d'etat"""

    information = "type de chef d'état"
    clef = 'leader_title1'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # Chaine est de la forme
    # [[ nom ]]
    # On prend nom
    p = re.compile("""
                    \[\[        # On supprime [[
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    chaine = m.group(1)
    # Si on tombe sur un nom avec des séparateurs |, on rend le dernier terme
    chaine = chaine.split('|').pop()

    return chaine

#======================================
def get_regime(pays, wp_info):
    """ Retourne (chaine) le régime"""

    information = "régime"
    clef = 'government_type'
    if clef not in wp_info:
        assert False, "{}: {} non trouvé".format(pays, information)
    chaine = wp_info[clef]

    # Chaine est de la forme
    # (... [[ nom ]])*
    # On cherche le dernier [
    chaine = chaine.split('[').pop()
    p = re.compile("""
                    ([^\]]*)    # On garde les caractères jusqu'au ] (non compris) => groupe 1
                    \]\]        # On supprime ]]
                   """, flags=re.VERBOSE)
    m = p.match(chaine)
    if m is None:
        assert False, "{}: {} invalide".format(pays, information)
    chaine = m.group(1)

    # Si on tombe sur un nom avec des séparateurs |, on rend le dernier terme
    chaine = chaine.split('|').pop()

    return chaine

#=================================== DEMOGRAPHIE =================================

#======================================
def get_habitants(pays, wp_info):
    """ Retourne (chaîne) le nombre d'habitants recensés ou estimés ("inconnu' si non renseigné)"""

    information = "nombre d'habitants"
    clef = 'population_census'
    if clef not in wp_info:
        clef = 'population_estimation'
        if clef not in wp_info:
            return "inconnu"
        else:
            chaine = wp_info[clef]
    else:
        chaine = wp_info[clef]
    return chaine

#======================================
def get_habitants_annee(pays, wp_info):
    """ Retourne (chaîne) l'année pour laquelle le nombre d'habitants recensés ou estimés est donné ('inconnu' si non renseigné)"""

    information = "année du nombre d'habitants"

    # Recherche de l'année de recensement
    clef = 'population_census_year'
    res = None
    if clef in wp_info:
        chaine = wp_info[clef]

        # On extrait de chaine le nombre entier
        p = re.compile("""
                        [^0-9]*     # On supprime les caractères jusqu'au premier chiffre
                        ([0-9]+)   # On garde les chiffres consécutifs => groupe 1
                       """, flags=re.VERBOSE)
        m = p.match(chaine)
        if m is not None:
            res = m.group(1)

    # Pas d'année de recensement => recherche de l'année d'estimation
    if res == None:
        clef = 'population_estimation_year'
        if clef in wp_info:
            chaine = wp_info[clef]

            # On extrait de chaine le nombre entier
            p = re.compile("""
                            [^0-9]*     # On supprime les caractères jusqu'au premier chiffre
                            ([0-9]+)   # On garde les chiffres consécutifs => groupe 1
                           """, flags=re.VERBOSE)
            m = p.match(chaine)
            if m is not None:
                res = m.group(1)

    if res == None:
        res = 'inconnu'
    return res

#=================================== SAUVEGARDE =================================

#======================================
def print_all_info():
    for continent in ['oceania', 'south_america']:
        with ZipFile('{}.zip'.format(continent), 'r') as z:
            for pays_json_file_name in z.namelist():
                wp = json.loads(z.read(pays_json_file_name))
                pays = pays_json_file_name.replace('.json', '')

                # Demographie
                #val = get_habitants(pays, wp)
                val = get_habitants_annee(pays, wp)

                # global
                #val = get_names(wp)
                #val = get_capitale(pays, wp)
                #val = get_flag(wp)

                # Economie
                #val = get_devise(pays, wp)
                #val = get_pib_nominal(pays, wp)
                #val = get_pib_par_tete(pays, wp)

                # Miscellaneous
                #val = get_sens_circulation(pays, wp)
                #val = get_code_appel(pays, wp)
                #val = get_domaine_internet(pays, wp)

                # Politique
                #val = get_regime(pays, wp)
                #val = get_nom_chef_etat(pays, wp)
                #val = get_type_chef_etat(pays, wp)

                print(u"{:<15}: {:<30}: {}".format(continent, pays, val))

#======================================
def save_global(conn, pays, continent, wp):
    """ Cette fonction se charge de la sauvegarde des informations générales d'un pays dans la table concernée """

    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO global VALUES (?, ?, ?, ?, ?, ?, ?, ?)'

    # Récupération des données du pays
    nom_conventionnel = get_names(wp)[0]
    nom_commun = get_names(wp)[1]
    capitale = get_capitale(pays, wp)
    coords = get_coords(wp)
    drapeau = get_flag(wp)
    adresse_wiki = get_adresse_wiki(pays,wp)

    # Soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql, (nom_conventionnel, nom_commun, capitale, continent, drapeau, coords['lat'], coords['lon'], adresse_wiki))

#======================================
def save_demographie(conn, pays, wp):
    """ Cette fonction se charge de la sauvegarde des informations sur la démographie d'un pays dans la table concernée """

    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO demographie VALUES (?, ?, ?)'

    # Récupération des données du pays
    habitants = get_habitants(pays, wp)
    habitants_annee = get_habitants_annee(pays, wp)

    # Soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql, (habitants, habitants_annee, pays.replace('_',' ')))

#======================================
def save_economie(conn, pays, wp):
    """ Cette fonction se charge de la sauvegarde des informations sur l'économie d'un pays dans la table concernée """

    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO economie VALUES (?, ?, ?, ?)'

    # Récupération des données du pays
    devise = get_devise(pays, wp)
    pib_nominal = get_pib_nominal(pays, wp)
    pib_par_tete = get_pib_par_tete(pays, wp)

    # Soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql, (devise, pib_nominal, pib_par_tete, pays.replace('_',' ')))

#======================================
def save_miscellaneous(conn, pays, wp):
    """ Cette fonction se charge de la sauvegarde des informations en vrac d'un pays dans la table concernée """

    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO miscellaneous VALUES (?, ?, ?, ?)'

    # Récupération des données du pays
    sens_circulation = get_sens_circulation(pays, wp)
    code_appel = get_code_appel(pays, wp)
    domaine_internet = get_domaine_internet(pays, wp)

    # Soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql, (sens_circulation, code_appel, domaine_internet, pays.replace('_',' ')))

#======================================
def save_politique(conn, pays, wp):
    """ Cette fonction se charge de la sauvegarde des informations sur la politique d'un pays dans la table concernée """

    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO politique VALUES (?, ?, ?, ?)'

    # Récupération des données du pays
    regime = get_regime(pays, wp)
    type_chef = get_type_chef_etat(pays, wp)
    nom_chef = get_nom_chef_etat(pays, wp)

    # Soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql, (regime, type_chef, nom_chef, pays.replace('_',' ')))

#======================================
def save_all_info(conn):
    for continent in ['oceania', 'south_america']:
        with ZipFile('{}.zip'.format(continent), 'r') as z:
            for pays_json_file_name in z.namelist():
                wp = json.loads(z.read(pays_json_file_name))
                pays = pays_json_file_name.replace('.json', '')

                save_global(conn, pays, continent, wp)
                save_demographie(conn, pays, wp)
                save_economie(conn, pays, wp)
                save_miscellaneous(conn, pays, wp)
                save_politique(conn, pays, wp)

#======================================
def delete_global(conn):
    """ Cette fonction supprime toutes les données de la table globale """

    c = conn.cursor()
    c.execute('DELETE FROM global')

#======================================
def delete_demographie(conn):
    """ Cette fonction supprime toutes les données de la table demographie """

    c = conn.cursor()
    c.execute('DELETE FROM demographie')

#======================================
def delete_economie(conn):
    """ Cette fonction supprime toutes les données de la table economie """

    c = conn.cursor()
    c.execute('DELETE FROM economie')

#======================================
def delete_miscellaneous(conn):
    """ Cette fonction supprime toutes les données de la table miscellaneous """

    c = conn.cursor()
    c.execute('DELETE FROM miscellaneous')

#======================================
def delete_politique(conn):
    """ Cette fonction supprime toutes les données de la table politique """

    c = conn.cursor()
    c.execute('DELETE FROM politique')

#======================================
def delete_all_info(conn):
    """ Cette fonction supprime toutes les données de toutes les tables """

    delete_global(conn)
    delete_demographie(conn)
    delete_economie(conn)
    delete_miscellaneous(conn)
    delete_politique(conn)

#=================================== Le programme ==============================


# Création de la base de données

#print_all_info()
conn = sqlite3.connect('pays.sqlite')
delete_all_info(conn)
save_all_info(conn)
conn.commit()
conn.close()

# Modifications manuelles de la table de données

def modifications_manuelles():
    import sqlite3
    table=sqlite3.connect('pays.sqlite')
    print(table)
    
    #Ajout et modifications des capitales
    
    #Listes des données manquantes
    tab_pays = ['Vanuatu','Bolivia', 'Ecuador', 'New Zealand', 'Solomon Islands', 'Kiribati', 'Majuro', 'Federated States of Micronesia', 'Republic of Palau']
    tab_lat = [-17.745,-19.043,-0.238,-41.299,-9.432,1.362,7.090,6.919,7.501]
    tab_long = [168.316,-65.259,-78.517,174.781,159.956,173.145,171.381,158.161,134.624]
    
    c=table.cursor()
    
    for i in range(len(tab_lat)-2):
        requete='UPDATE global SET latitude={},longitude={} WHERE nom_commun=?'.format(tab_lat[i],tab_long[i])
        c.execute(requete,(tab_pays[i],))
        table.commit()

    for i in range(len(tab_lat)-2,len(tab_lat)):
        
        c=table.cursor()
        requete='UPDATE global SET latitude={},longitude={} WHERE nom_conventionnel=?'.format(tab_lat[i],tab_long[i])
        c.execute(requete,(tab_pays[i],))
        table.commit()
#    
    
    #Ajout des populations
    
    tab_pays = ['Federated States of Micronesia','Solomon Islands', 'Bolivia', 'Brazil', 'Colombia', 'Ecuador', 'Venezuela', 'Paraguay']
    tab_habit = ['102,624', '647,581', '11,639,909', '211,715,973', '49,084,841', '16,904,867', '31,689,176', '7,191,685']
    tab_annees = [2010, 2017, 2020, 2020, 2020, 2020, 2018, 2020]
    

    for i in range(len(tab_pays)):
        c=table.cursor()  
        requete='UPDATE demographie SET habitants=?,habitants_annee_N={} WHERE nom_commun=?'.format(tab_annees[i])
        c.execute(requete,(tab_habit[i],tab_pays[i],))
        table.commit()


    #Modification noms pour bonne extraction 
    
    c=table.cursor()
    requete='UPDATE global SET nom_commun=? WHERE nom_conventionnel=?'
    c.execute(requete,('Palau','Republic of Palau',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET nom_commun=? WHERE nom_conventionnel=?'
    c.execute(requete,('Federated States of Micronesia','Federated States of Micronesia',))
    table.commit()
    
    #Ajout drapeaux manquants
    
    c=table.cursor()
    requete='UPDATE global SET drapeau=? WHERE nom_commun=?'
    c.execute(requete,('flags/palau-160x100.png','Palau',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET drapeau=? WHERE nom_commun=?'
    c.execute(requete,('flags/federated_states_of_micronesia-190x100.png','Federated States of Micronesia',))
    table.commit()
    
    table.close()

modifications_manuelles()
