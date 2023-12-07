# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 15:29:41 2023

@author: joffrion
"""
#!pip install --update rastererio
#!pip install osgeo
import os
os.environ['MYOTB'] = 'C:/OTB-8.1.2-Win64/bin' #path to the OTB bin folder
os.environ['MYRAM'] = '2000'
import my_function as f
import glob
import pandas as pd 
import geopandas as gpd
import rasterio
from osgeo import gdal, osr
import time

#Initiate compteur
# get the start time
st = time.time()

    ##Espace de travail et donnée en entrée

#folder containing 6 subdirectory for the 6 SENTI II S2A img
data_path ='C:/Temp/bd_foret_teledec_python-main/data_set'
#directory to register the local intermediate and final data
working_directory = 'C:/Temp/bd_foret_teledec_python-main/traitement'
#path to bd_foret
bd_foret='C:/Temp/bd_foret_teledec_python-main/data_set/FORMATION_VEGETALE.shp'
#path emprise
roi = 'C:/Temp/bd_foret_teledec_python-main/data_set/emprise_etude.shp'

os.chdir(working_directory)

    ##Create subworking-dir

#create subdirectory to store intermediate result
os.mkdir(f'{working_directory}/intermediate_result')
#store short name
iwdir = f'{working_directory}/intermediate_result'

#create subdirectory to store finale date result
os.mkdir(f'{working_directory}/date_result')
#store short name
ifwdir = f'{working_directory}/date_result'

    ##Découper la bd foret & Rasterisation
    
#Nettoyage de la donnée, création champ raster
gdf_mask , foret_filtre_path = f.traitement_forest(bd_foret,iwdir)
#in_vector = f.traitement_bd_foret(bd_foret,roi, working_directory) 

out_image = 'masque_foret.tif'
field = 'raster'#field to rasterize
f.rasterize_shapefile(foret_filtre_path, out_image, roi,field, 10)
#f.rasterize_shapefile(in_vector, out_image, roi, field_name ,10)


    ##Check SCR
#ouverture de l'image et de l'emprise
#boucle sur le nombre de subdirectory du data_path en entree
files = [os.path.join(data_path,f) for f in os.listdir(data_path)
         if os.path.isdir(os.path.join(data_path,f))]
result_1 = glob.glob(F"{files[0]}/*FRE_B2.tif")
img_path=result_1[0]

img = rasterio.open(img_path)
emprise = gpd.read_file(roi)

#reprojectionimg_crs de l'emprise par rapport aux img S2
img_crs = img.crs
emprise_32631 = emprise.to_crs(img_crs)

#sauvegarder la nouvelle projection de l'emprise
emprise_32631.to_file(f'{iwdir}/emprise_32631', driver = 'ESRI Shapefile')

new_emprise = f'{iwdir}/emprise_32631'

    ##Start Pre_traitement

#init empty list of futur date_x path
list_date_path = []
#init empty list of futur ndvi date_x path
list_ndvi_path = []

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
        output_raster = f'{iwdir}/cut{band_name}'
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
        output_raster = f'{iwdir}/_10m_{band_name}'
        #appel de la fonction
        f.cmd_Superimpose(inr, inm, output_raster)
        list_bande_finale.append(output_raster)
    
    list_bande_finale = list_band_10m + list_bande_finale

            
            ##Concaténation 
    #recup la date première band et store it in var
    date =  f.get_date_f_b_path(list_bande_finale[0])
    output_concat = f'{ifwdir}/output_{date}_date.tif'
    #appel de la fonction
    f.cmd_ConcatenateImages(list_bande_finale, output_concat)
    list_date_path.append(output_concat)
    
    #produce ndvi
    ndvi_path = f.rasterio_ndvi(output_concat,3,4)#return ndvi path  ?
    list_ndvi_path.append(ndvi_path)

#concat finale des 6 dates        
output_concat = 'Serie_temp_S2_allbands.tif'
f.cmd_ConcatenateImages(list_date_path, f'{iwdir}/{output_concat}')
f.warp(f'{iwdir}/{output_concat}', f'{ifwdir}/{output_concat}', '2154')
f.apply_mask( f'{ifwdir}/{output_concat}', output_concat, gdf_mask)



#concat finale des 6 dates NDVI 
output_concat = 'Serie_temp_S2_ndvi.tif'
f.cmd_ConcatenateImages(list_ndvi_path, f'{iwdir}/{output_concat}')
f.warp(f'{iwdir}\{output_concat}', f'{ifwdir}\{output_concat}', '2154')
f.apply_mask( f'{ifwdir}/{output_concat}', output_concat, gdf_mask)

#compteur 
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')

##Delete intermediate result folder
import shutil
shutil.rmtree(iwdir)


# Création des diagrammes

column_name = ['Code_lvl1','Code_lvl2','Code_lvl3']
shapefile_path = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/Sample_BD_foret_T31TCJ.shp'
save_path_template = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_poly_lvl{column_number}.png'

f.create_polygons_bar_charts(shapefile_path, column_name, save_path_template)
