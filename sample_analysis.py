# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 12:15:01 2023

@author: leond
"""
import geopandas as gpd
from my_function import create_polygons_bar_charts
from my_function import generate_pixel_count_diagrams
from my_function import generate_temporal_signature_plot
import os


# Charger le shapefile avec GeoPandas
shapefile_path = 'D:/Cours_M2/Teledetecion_python/traitements/data/bd_foret2.shp'
gdf = gpd.read_file(shapefile_path)
column_name = ['Code_lvl1','Code_lvl2','Code_lvl3']
save_path_template = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_poly_lvl{column_number}.png'

#Création des 3 premiers diagrammes : compter le nombre de polygone par classe
create_polygons_bar_charts(shapefile_path, column_name, save_path_template)



save_path_template2 = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_pix_lvl{column_number}.png'
raster_path = 'D:/Cours_M2/Teledetecion_python/traitements/masque_bd_foret/masque_foret.tif'

#Création des 3 diagrammes intermédiaires : compter le pixel par classe
generate_pixel_count_diagrams(shapefile_path, column_name, raster_path, save_path_template2)



#Définition des 
my_folder = ("D:/Cours_M2/Teledetecion_python/traitements/traitement/date_result")

image_filename = os.path.join(my_folder, 'Serie_temp_S2_ndvi.tif')
sample_code_lvl1 = os.path.join(my_folder,'sample_bdforet_codelvl1.tif')
sample_code_lvl2 = os.path.join(my_folder,'sample_bdforet_codelvl2.tif')
sample_code_lvl3 = os.path.join(my_folder,'sample_bdforet_codelvl3.tif')
output_folder = ('D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/')
bande_names = ['31/03/21','15/04/21','19/07/21','17/10/21','16/12/21','25/01/22']
code_lvl = ['1','2','3']

#Création des 3 graphiques représentant la signature temporelle de la moyenne et l'écart type du ndvi par classe

generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl1, output_folder, code_lvl[0], bande_names)
generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl2, output_folder,code_lvl[1], bande_names)
generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl3, output_folder, code_lvl[2], bande_names)



