
def importation ():
    import sqlite3
    table=sqlite3.connect('pays.sqlite')
    datalist=[]
    
    #Ensemble des clefs de la base de données
    demographie_keys=['habitants','habitants_annee_N']
    economie_keys=['devise','PIB_nominal_courant','PIB_par_tete']
    global_keys=['nom_conventionnel','nom_commun','capitale','continent','drapeau','latitude','longitude','adresse_wiki']
    miscellaneous_keys=['Sens_circulation_voitures','code_appel','domaine_internet']
    politique_keys=['regime','type_chef_etat','nom_chef_etat']
    
    #Récupération d'un tuple des noms communs
    c=table.cursor()
    requete='SELECT nom_commun FROM global'
    c.execute(requete)
    r=c.fetchall()
    
    identification=1 #Chaque pays possède un id qui lui est propre
    for country in r:
        
        #Récupération des données dans chaque table
        demographie_donnees=read_pays_demographie(table,country)
        economie_donnees=read_pays_economie(table,country)
        global_donnees=read_pays_global(table,country)
        miscellaneous_donnees=read_pays_miscellaneous(table,country)
        politique_donnees=read_pays_politique(table,country)
                
        #Initialisation du dico
        datalist.append({'id':identification})
        identification+=1
        
        #On remplit le dictionnaire du pays concerné
        for i in range(len(global_keys)):
            datalist[-1][global_keys[i]]=global_donnees[i]
        for i in range(len(demographie_keys)):
            datalist[-1][demographie_keys[i]]=demographie_donnees[i]
        for i in range(len(economie_keys)):
            datalist[-1][economie_keys[i]]=economie_donnees[i]
        for i in range(len(miscellaneous_keys)):
            datalist[-1][miscellaneous_keys[i]]=miscellaneous_donnees[i]
        for i in range(len(politique_keys)):
            datalist[-1][politique_keys[i]]=politique_donnees[i]
        
    return datalist

#Fonctions permettant de lire les données d'un pays dans la table concernée
def read_pays_demographie(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM demographie WHERE nom_commun=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r

def read_pays_economie(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM economie WHERE nom_commun=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r

def read_pays_global(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM global WHERE nom_commun=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r

def read_pays_miscellaneous(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM miscellaneous WHERE nom_commun=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r

def read_pays_politique(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM politique WHERE nom_commun=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r


