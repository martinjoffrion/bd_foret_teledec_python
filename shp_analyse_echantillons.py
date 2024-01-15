# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 17:19:39 2023

@author: clair
"""

import pandas as pd
import geopandas as gpd
#conda install openpyxl
working_directory = 'D:/projet_teledetection_python'

nomenclature = pd.read_excel('D:/projet_teledetection_python/nomenclature.xlsx')#20 lignes et 8 colonnes
emprise_etude = 'D:/projet_teledetection_python/data_set/emprise_etude.shp'
bd_foret='D:/projet_teledetection_python/data_set/FORMATION_VEGETALE.shp'

#Lecture des fichiers
foret = gpd.read_file(bd_foret)
emprise = gpd.read_file(emprise_etude)
# Identifier les valeurs à supprimer
valeurs_a_supprimer = ['Lande', 'Formation herbacée',
                       'Forêt ouverte de feuillus purs',
                       'Forêt ouverte de conifères purs',
                       'Forêt ouverte sans couvert arboré',
                       'Forêt ouverte à mélange de feuillus et conifères'] #données a supprimer dans la bd foret
foret_filtre = foret[~foret['TFV'].isin(valeurs_a_supprimer)] #supprime les valeurs de la bd foret non souhaité

#emprise des images S2 que vous allez utiliser
bd_foret_ok = gpd.clip(foret_filtre, emprise)


bd_foret_nomenclature = pd.merge(bd_foret_ok, nomenclature, on='CODE_TFV', how='inner')
#nettoyage
bd_foret_nomenclature = bd_foret_nomenclature.drop(columns=['TFV_y'])
bd_foret_nomenclature = bd_foret_nomenclature.rename(columns={'TFV_x' : 'TFV'})

#si une classe TFV contient moins de 15 polygones dans la classe 3, alors ne la prenez pas en compte.
seuil_min_polygones = 15
comptage_polygones = bd_foret_nomenclature.groupby('Code_lvl3')['Code_lvl3'].count()

classes_a_supprimer = comptage_polygones[comptage_polygones <= seuil_min_polygones].index
df_filtre = bd_foret_nomenclature[~bd_foret_nomenclature['Code_lvl3'].isin(classes_a_supprimer)]
print(df_filtre)

#test
folder_traitement = 'D:/projet_teledetection_python/Sample_BD_foret_T31TCJ'
df_filtre.to_file(folder_traitement, driver="ESRI Shapefile")
