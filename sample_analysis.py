# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 12:15:01 2023

@author: leond
"""

import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
import numpy as np
from my_function import create_polygons_bar_charts
from my_function import create_pixel_count_bar_charts

# Charger le shapefile avec GeoPandas
shapefile_path = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/Sample_BD_foret_T31TCJ.shp'
gdf = gpd.read_file(shapefile_path)

# Afficher les premières lignes du GeoDataFrame pour comprendre la structure des données




column_name = ['Code_lvl1','Code_lvl2','Code_lvl3']

save_path_template = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_poly_lvl{column_number}.png'
save_path_template2 = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_pix_lvl{column_number}.png'



create_polygons_bar_charts(shapefile_path, column_name, save_path_template)
    

raster_path = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/mask_bd_foret.tif'


create_pixel_count_bar_charts(shapefile_path, raster_path, column_name, save_path_template2)



