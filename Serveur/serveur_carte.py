# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:53:46 2020

@author: letog
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:49:04 2020

@author: letog
"""

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json
import import_database as dt


# définition du handler
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  # on surcharge la méthode qui traite les requêtes GET
  def do_GET(self):
    self.init_params()
    data_import=dt.importation()
    
    # requete location - retourne la liste de lieux et leurs coordonnées géographiques
    if self.path_info[0] == "location":
      data = data_import
      self.send_json(data)

    # requete description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
    elif self.path_info[0] == "description":
      data= data_import
      for c in data:
        if c['id'] == int(self.path_info[1]):
          self.send_json(c)
          break
    
    #requête du formulaire de distance
    elif self.path_info[0] == "distance":
        print(self.path_info[1],self.path_info[2])
        distance=self.calcul_distance(data_import,self.path_info[1],self.path_info[2])
        print(distance)
        if distance==0:
            self.send('Vous êtes dans le même pays')
        elif distance==-1:
            self.send('Multiples erreurs de frappe')
        elif distance==-2:
            self.send('Erreur de frappe Pays/Capital A')
        elif distance==-3:
            self.send('Erreur de frappe Pays/Capital B')
        else :
            self.send('La distance Capitale/Capitale est de {} km'.format(int(distance)))
    
    else:
      self.send_static()


  # méthode pour traiter les requêtes HEAD
  def do_HEAD(self):
      self.send_static()


  # méthode pour traiter les requêtes POST - non utilisée dans l'exemple
  def do_POST(self):
    self.init_params()
    send_error(405)


  # on envoie le document statique demandé
  def send_static(self):

    # on modifie le chemin d'accès en insérant le répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)


  # on envoie un document html dynamique
  def send_html(self,content):
     headers = [('Content-Type','text/html;charset=utf-8')]
     html = '<!DOCTYPE html><title>{}</title><meta charset="utf-8">{}' \
         .format(self.path_info[0],content)
     self.send(html,headers)

  # on envoie un contenu encodé en json
  def send_json(self,data,headers=[]):
    body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body) 

  # on envoie la réponse
  def send(self,body,headers=[]):
     encoded = bytes(body, 'UTF-8')

     self.send_response(200)

     [self.send_header(*t) for t in headers]
     self.send_header('Content-Length',int(len(encoded)))
     self.end_headers()

     self.wfile.write(encoded)


  # on analyse la requête pour initialiser nos paramètres
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # traces
    print('info_path =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)

  def calcul_distance(self,data,psa,psb):
      lata=0
      latb=0
      lona=0
      lonb=0
      testa=0
      testb=0 #tests de bon orthographe
      import numpy as np
      for d in data:
          if d['nom_commun']==psa or d['nom_conventionnel']==psa or d['capitale']==psa:
              lata=d['latitude']*np.pi/180
              lona=d['longitude']*np.pi/180
              testa+=1
          if d['nom_commun']==psb or d['nom_conventionnel']==psb or d['capitale']==psb:
              latb=d['latitude']*np.pi/180
              lonb=d['longitude']*np.pi/180
              testb+=1
      M=60*1.852*180/np.pi*np.arccos(np.sin(lata)*np.sin(latb)+np.cos(lata)*np.cos(latb)*np.cos(lonb-lona))
      if testa==0 and testb==0:
          return -1 #'''S'il y a une erreur de frappe pour les 2 pays/capitales'''
      elif lata==latb and lona==lonb:
          return 0 #'''Si on est dans le même pays ex : A=Lima B=Peru'''
      elif testa==0:
          return -2 #'''Erreur de frappe uniquement A'''
      elif testb==0 :
          return -3 #'''Erreur de frappe uniquement A'''
      #'''Si tout est bon on return la distance'''
      return M   

# instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()
