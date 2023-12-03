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

#### Warning variable emprise_etude ####

#folder containing 6 subdirectory for the 6 SENTI II S2A img
data_path ='C:/Users/dsii/Documents/Teledec_python'
#directory to register the local intermediate and final data
working_directory = 'C:/Users/dsii/Documents/Teledec_python'

#create subdirectory to store intermediate result
os.mkdir(f'{working_directory}\intermediate_result')
#store short name
iwdir = f'{working_directory}\intermediate_result'

#create subdirectory to store finale date result
os.mkdir(f'{working_directory}\date_result')
#store short name
ifwdir = f'{working_directory}\date_result'


#init empty list of futur date_x path
list_date_path = []
#init empty list of futur ndvi date_x path
list_ndvi_path = []

#boucle sur le nombre de subdirectory du data_path en entree
files = [f for f in os.listdir(data_path) if os.path.isdir(f)]#pas encore indenté
for subfil in range(len(files)):

    ##Get the band with 'glob'
    
    #list des bandes recherchées
    list_band=['B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12']
    #init empty list of band path
    list_band_name =[]
    for i in range (len(list_band)):
        result = glob.glob(F"{files[subfil]}/*FRE_{list_band[i]}.tif")
        if result == [] : result.append( ' ')
        band = result[0]
        list_band_name.append(band)
    
    
    # to convert lists to dictionary
    dict_band = {list_band[i]: list_band_name[i] for i in range(len(list_band))}   

            
    ##Découpage du raster selon le fichier emprise
    
    #init empty list of new band path
    list_bande_cut = []
    
    for i in range (len(list_band_name)):
        input_img = list_band_name[i]
        band_name = os.path.basename(input_img)
        output_raster = f'{iwdir}\cut{band_name}'
        #appel de la fonction
        f.cmd_ExtractROI(input_img,emprise_etude,output_raster)
        list_bande_cut.append(output_raster)
        
    #update_dict
    # to convert lists to dictionary
    dict_band = {list_band[i]: list_bande_cut[i] for i in range(len(list_band))}   
    
    #create list band 20m resolution
    list_bande_20m_plus = [dict_band.get(x) for x in ['B5','B6','B7','B8A','B11','B12']]
    
    #create list band 10m resolution
    list_band_10m = [dict_band.get(x) for x in ['B2','B3','B4','B8']]
    
    #init empty list of new path superimpose
    list_bande_finale = []
    
    ##Rééchantillonage
    
    for i in range(len(list_bande_20m_plus)):
        inr = list_band_10m[0] #premiere element de la liste bande ref 10m
        inm = list_bande_20m_plus[i]
        band_name = os.path.basename(inm)
        output_raster = f'{iwdir}\_10m_{band_name}'
        #appel de la fonction
        f.cmd_Superimpose(inr, inm, output_raster)
        list_bande_finale.append(output_raster)
    
    list_bande_finale = list_band_10m + list_bande_finale

            
            ##Concaténation 
    #recup la date première band et store it in var
    date =  f.get_date_f_b_path(list_bande_finale[0])
    output_concat = f'{ifwdir}\output_{date}_x.tif'
    list_date_path.append(output_concat)
    #appel de la fonction
    f.cmd_ConcatenateImages(list_bande_finale, output_concat)
    
    #produce ndvi
    ndvi_path = f.rasterio_ndvi(output_concat,3,4)#return ndvi path  ?
    list_ndvi_path.append(ndvi_path)

#concat finale des 6 dates        
output_concat = 'Serie_temp_S2_allbands.tif'
f.cmd_ConcatenateImages(list_date_path, output_concat)

#concat finale des 6 dates NDVI 
output_concat = 'Serie_temp_S2_ndvi.tif'
f.cmd_ConcatenateImages(list_ndvi_path, output_concat)

##Delete intermediate result folder
import shutil
shutil.rmtree(iwdir)


