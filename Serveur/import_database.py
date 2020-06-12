
#import sqlite3
#
#table=sqlite3.connect('pays.sqlite')

def importation ():
    import sqlite3
    table=sqlite3.connect('pays.sqlite')
    datalist=[]
    #Liste à mettre à jour en fonction de l'avancée dans le projet
    keys=['nom_conventionnel','nom_commum','capitale','continent','drapeau','latitude','longitude','adresse_wiki']
    
    #Récupération d'un tuple des noms conventionnels
    c=table.cursor()
    requete='SELECT nom_conventionnel FROM global'
    c.execute(requete)
    r=c.fetchall()
    print(r)
    identification=1
    for country in r:
        donnees=read_pays(table,country)
        #Initialisation du dico
        datalist.append({'id':identification})
        identification+=1
        
        for i in range(len(keys)):
            datalist[-1][keys[i]]=donnees[i]
    
    return datalist
    
        

def read_pays(conn,pays):
    c=conn.cursor()
    requete='SELECT * FROM global WHERE nom_conventionnel=?'
    c.execute(requete,pays)
    r=c.fetchone()
    return r


