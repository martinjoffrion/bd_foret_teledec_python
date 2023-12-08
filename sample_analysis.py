# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 12:15:01 2023

@author: leond
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from my_function import create_polygons_bar_charts

# Charger le shapefile avec GeoPandas
shapefile_path = 'D:/Cours_M2/Teledetecion_python/traitements/traitement_bd_foret/Sample_BD_foret_T31TCJ.shp'
column_name = ['Code_lvl1','Code_lvl2','Code_lvl3']
save_path_template = 'D:/Cours_M2/Teledetecion_python/traitements/Diagrammes/diag_baton_nb_poly_lvl{column_number}.png'

create_polygons_bar_charts(shapefile_path, column_name, save_path_template)


