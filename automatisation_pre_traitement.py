# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 15:29:41 2023

@author: joffrion
"""
!pip install --update rastererio
!pip install osgeo
import os
os.environ['MYOTB'] = 'C:/OTB-8.1.2-Win64/bin' #path to the OTB bin folder
import my_function as f
import glob
import pandas as pd 
import geopandas as gpd
from my_function import traitement_bd_foret
from my_function import rasterize_shapefile
from osgeo import gdal, osr

"""
            Découper la bd foret selon l'emprise de l'étude
"""


bd_foret="bd_foret/FORMATION_VEGETALE.shp"
emprise_etude = 'D:/Cours_M2/Teledetecion_python/traitements/data/emprise_etude.shp'
folder_traitement = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/bd_foret.shp'

traitement_bd_foret(bd_foret,emprise_etude, folder_traitement) #réalise un intersect entre la bd foret et l'emprise d'étude


"""
            Rasterisation
"""
in_vector = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/bd_foret.shp'
out_image = 'traitement_bd_foret/mask_bd_foret.tif'


cmd = rasterize_shapefile(in_vector, out_image, emprise_etude)
os.system(cmd)# execute the command in the terminal






#folder containing 6 subdirectory for the 6 SENTI II S2A img
data_path ='C:/Users/dsii/Documents/Teledec_python'
#directory to register the local intermediate and final data
working_directory = 'C:/Users/dsii/Documents/Teledec_python'



#init empty list of futur date_x path
list_date_path = []


#boucle sur le nombre de subdirectory du data_path en entree
files = [f for f in os.listdir(data_path) if os.path.isdir(f)]#pas encore indenté

###Get the band with 'glob'

#list des bandes recherchées
list_band=['B2','B3','B4','B5','B6','B7','B8','B9','B11','B12']
#init empty list of band path
list_band_name =[]
for i in range (len(list_band)):
    result = glob.glob(F"{data_path}/*FRE_{list_band[i]}.tif")
    if result == [] : result.append( ' ')
    band = result[0]
    list_band_name.append(band)
    #version plusieurs results(plusieurs dates dans un dossier) 
    #list_band_names.append(result)


# to convert lists to dictionary
dict_band = {list_band[i]: list_band_name[i] for i in range(len(list_band))}   
print(dict_band.get('B7'))

#create subdirectory to store intermediate result
os.mkdir(f'{working_directory}\intermediate_result')
#store short name
iwdir = f'{working_directory}\intermediate_result'

##découpage du raster selon le fichier emprise

#init empty list of new band path
list_bande_cut = []

for i in range (len(list_band_name)):
    input_img = list_band_name[i]
    band_name = os.path.basename(input_img)
    output_raster = f'{iwdir}\cut{band_name}'
    #appel de la fonction
    f.cmd_ExtractROI(input_img, emprise_etude, output_raster)
    list_bande_cut.append(output_raster)
    
#update_dict
# to convert lists to dictionary
dict_band = {list_band[i]: list_bande_cut[i] for i in range(len(list_band))}   

#
list_bande_20m_plus = [dict_band.get(x) for x in ['B5','B6','B7','B9','B11','B12']]

#
list_band_10m = [dict_band.get(x) for x in ['B2','B3','B4','B8']]

#init empty list of new path superimpose
list_bande_finale = []

##Rééchantillonage

for i in range(len(list_bande_20m_plus)):
    inr = list_band_10m[0] #premiere element de la liste bande ref 10m
    inm = list_bande_20m_plus[i]
    band_name = os.path.basename(inm)
    output_raster = f'{iwdir}\10m_{band_name}'
    #appel de la fonction
    f.cmd_Superimpose(inr, inm, output_raster)
    list_bande_finale.append(output_raster)

list_bande_finale = list_band_10m + list_bande_finale
    
#find a way to recup la date et store it in the name
output_concat = f'{iwdir}\output_date_x.tif'
#appel de la fonction
f.cmd_ConcatenateImages(list_bande_finale, output_concat)

list_date_path.append(output_concat)

#produce ndvi
f.rasterio_ndvi(output_concat,3,4)


