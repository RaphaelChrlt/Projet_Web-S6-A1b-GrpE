# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 11:17:32 2020

@author: rapha
"""

def modifications_manuelles():
    import sqlite3
    table=sqlite3.connect('pays.sqlite')
    print(table)
    
    #Ajout et modifications des capitales
    c=table.cursor()
    requete='UPDATE global SET latitude=-17.7450363,longitude=168.315741 WHERE nom_commun=?'
    c.execute(requete,('Vanuatu',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=-19.0427778,longitude=-65.25916667 WHERE nom_commun=?'
    c.execute(requete,('Bolivia',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=-0.238333,longitude=-78.5172222 WHERE nom_commun=?'
    c.execute(requete,('Ecuador',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=-41.2986111,longitude=174.78111111 WHERE nom_commun=?'
    c.execute(requete,('New Zealand',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=-9.4319444,longitude=159.95555555555555 WHERE nom_commun=?'
    c.execute(requete,('Solomon Islands',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=1.3617602583883812,longitude=173.14547027034357 WHERE nom_commun=?'
    c.execute(requete,('Kiribati',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=7.0897222,longitude=171.38055555555556 WHERE nom_commun=?'
    c.execute(requete,('Majuro',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE global SET latitude=6.918685081405425,longitude=158.16068345373725 WHERE nom_conventionnel=?'
    c.execute(requete,('Federated States of Micronesia',))
    table.commit()
#    
    c=table.cursor()
    requete='UPDATE global SET latitude=7.5005556,longitude=134.62416666666667 WHERE nom_conventionnel=?'
    c.execute(requete,('Republic of Palau',))
    table.commit()
    
    #Ajout des populations
    c=table.cursor()
    requete='UPDATE demographie SET habitants=102624,habitants_annee_N=2010 WHERE nom_commun=?'
    c.execute(requete,('Federated States of Micronesia',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=647581,habitants_annee_N=2017 WHERE nom_commun=?'
    c.execute(requete,('Solomon Islands',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=11639909,habitants_annee_N=2020 WHERE nom_commun=?'
    c.execute(requete,('Bolivia',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=211715973,habitants_annee_N=2020 WHERE nom_commun=?'
    c.execute(requete,('Brazil',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=49084841,habitants_annee_N=2020 WHERE nom_commun=?'
    c.execute(requete,('Colombia',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=16904867,habitants_annee_N=2020 WHERE nom_commun=?'
    c.execute(requete,('Ecuador',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=31689176,habitants_annee_N=2018 WHERE nom_commun=?'
    c.execute(requete,('Venezuela',))
    table.commit()
    
    c=table.cursor()
    requete='UPDATE demographie SET habitants=7191685,habitants_annee_N=2020 WHERE nom_commun=?'
    c.execute(requete,('Paraguay',))
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
    
    #Ajout drapeau manquant
    
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








