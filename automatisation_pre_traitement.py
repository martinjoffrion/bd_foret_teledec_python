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
from osgeo import gdal, osr

    ##Espace de travail et donnée en entrée

#folder containing 6 subdirectory for the 6 SENTI II S2A img
data_path ='C:/Users/dsii/Documents/Teledec_python'
#directory to register the local intermediate and final data
working_directory = 'C:/Users/dsii/Documents/Teledec_python'
#path to bd_foret
bd_foret="bd_foret/FORMATION_VEGETALE.shp"
#path emprise
roi = 'D:/Cours_M2/Teledetecion_python/traitements/data/emprise_etude.shp'


    ##Découper la bd foret & Rasterisation
    
#réalise un intersect entre la bd foret et l'emprise d'étude
in_vector = f.traitement_bd_foret(bd_foret,roi, working_directory) 

out_image = f'{working_directory}/masque_foret.tif'
field_name = 'raster'#field to rasterize
f.rasterize_shapefile(in_vector, out_image, roi, field_name ,10)


    ##Create subworking-dir

#create subdirectory to store intermediate result
os.mkdir(f'{working_directory}\intermediate_result')
#store short name
iwdir = f'{working_directory}\intermediate_result'

#create subdirectory to store finale date result
os.mkdir(f'{working_directory}\date_result')
#store short name
ifwdir = f'{working_directory}\date_result'


    ##Check SCR
#ouverture de l'image et de l'emprise

files = [f for f in os.listdir(data_path) if os.path.isdir(f)]
result = glob.glob(F"{files[0]}/*FRE_B2.tif")
img_path=result[0]

img = rasterio.open(img_path)
emprise = gpd.read_file(roi)

#reprojectionimg_crs de l'emprise par rapport aux img S2
img_crs = img.crs
emprise_32631 = emprise.to_crs(img_crs)

#sauvegarder la nouvelle projection de l'emprise
emprise_32631.to_file(f'{iwdir}\emprise_32631', driver = 'ESRI Shapefile')

new_emprise = f'{iwdir}\emprise_32631'

    ##Start Pre_traitement

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
        f.cmd_ExtractROI(input_img,new_emprise,output_raster)
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


