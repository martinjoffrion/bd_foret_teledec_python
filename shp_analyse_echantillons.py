# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 17:19:39 2023

@author: clair
"""

import pandas as pd
import geopandas as gpd
#conda install openpyxl
import os
os.environ['MYOTB'] = 'D:/OTB-8.1.2-Win64/bin' #path to the OTB bin folder
working_directory = 'D:/projet_teledetection_python'



nomenclature = pd.read_excel('D:/projet_teledetection_python/nomenclature.xlsx')
emprise_etude = 'D:/projet_teledetection_python/emprise_etude.shp'
bd_foret='D:/projet_teledetection_python/BDFORET_2-0__SHP_LAMB93_D031_2019-01-09/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D031/FORMATION_VEGETALE.shp'

folder_traitement = 'D:/projet_teledetection_python/bd_foret'
foret = gpd.read_file(bd_foret)
emprise = gpd.read_file(emprise_etude)
    # Identifier les valeurs à supprimer
valeurs_a_supprimer = ['Lande', 'Formation herbacée'] #données a supprimer dans la bd foret
foret_filtre = foret[~foret['TFV'].isin(valeurs_a_supprimer)] #supprime les valeurs de la bd foret non souhaité
intersection = gpd.overlay(foret_filtre, emprise, how='intersection')
intersection.to_file(folder_traitement, driver="ESRI Shapefile")




##lire le shp
bd_foret = gpd.read_file('D:/projet_teledetection_python/bd_foret.shp')
bd_foret_nomenclature = pd.merge(bd_foret, nomenclature, on='CODE_TFV', how='inner')
supp_col = ['raster', 'MINX', 'MINY', 'MAXX', 'MAXY', 'CNTX', 'CNTY', 'AREA', 'PERIM', 'HEIGHT', 'WIDTH', 'MINX_2', 'MINY_2', 'MAXX_2', 'MAXY_2', 'CNTX_2', 'CNTY_2', 'AREA_2', 'PERIM_2', 'HEIGHT_2', 'WIDTH_2','TFV_y']
bd_foret_nomenclature = bd_foret_nomenclature.drop(supp_col, axis=1)
bd_foret_nomenclature = bd_foret_nomenclature.rename(columns={'TFV_x' : 'TFV'})


bd_foret_nomenclature.to_file(f'{working_directory}/bd_foret_nomenclature.shp', driver="ESRI Shapefile")
print(bd_foret_nomenclature.TFV_x == 'Forêt fermée de feuillus purs en îlots')

###condition 
seuil_min_polygones = 15
comptage_polygones = bd_foret_nomenclature.groupby('CODE_TFV')['Code_lvl3'].count()
classes_a_supprimer = comptage_polygones[comptage_polygones <= seuil_min_polygones].index
df_filtre = bd_foret_nomenclature[~bd_foret_nomenclature['Code_lvl3'].isin(classes_a_supprimer)]
print(df_filtre)
