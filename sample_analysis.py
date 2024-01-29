# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 12:15:01 2023

@author: ducrocq, joffrion et arondel
"""
###############################################################################
##--------------------- CHEMINS D'ACCES A RENSEIGNER ------------------------##
###############################################################################

working_directory = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4'
import os
os.chdir(working_directory)

# --- Mettre le chemin d'accès du dossier OTB-8.1.2/bin :
#os.environ['MYOTB'] = 'le/chemin/vers/OTB-8.1.2-Win64/bin'
os.environ['MYOTB'] = 'C:/Users/clair/Documents/OTB-8.1.2-Win64/bin'
os.environ['MYRAM'] = '8000'

import my_function as f

# --- Chemin d'accès du dossier qui comprendra les diagrammes :
#working_directory = 'le/chemin/vers/projet_teledection_sigmaM2_group4/traitement'
working_directory = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4/traitement'

# --- Chemin d'accès du dossier comprenant les données d'entrée :
#data_path = 'le/chemin/vers/projet_teledection_sigmaM2_group4/data_set'
data_path = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4/data_set'

# --- Répertoire de travail actuel 
os.chdir(working_directory)

# --- Création d'un nouveau sous-dossier pour y stocker les résultats intermédiaires
os.mkdir(os.path.join(working_directory,'intermediate_result'))
# enregistre le chemin complet sous une variable
iwdir = os.path.join(working_directory, 'intermediate_result')


###############################################################################
##----------------------------- SAMPLE ANALYSIS -----------------------------##
###############################################################################

########### --- Création de 3 diagrammes en bâton du nombre de polygones par classe

shapefile_path = os.path.join (data_path, 'Sample_BD_foret_T31TCJ.shp')
column_name = ['Nom_lvl1', 'Nom_lvl2', 'Nom_lvl3']
save_path_template = os.path.join(working_directory, 'diag_baton_nb_poly_lvl{column_number}.png')

# appel à la fonction
f.create_polygons_bar_charts(shapefile_path, column_name, save_path_template)

########### --- Création de diagrammes sur le nombre de pixels par classe

# rasterisation du fichier Sample_BD_foret_T31TCJ.shp par classe dans le dossier intermédiaire
image_filename = os.path.join(data_path, 'Serie_temp_S2_ndvi.tif')

for niv in range(1, 4):
    sample_filename_niv = os.path.join(iwdir, 'sample_bdforet_codelvl{}.tif'.format(niv))
    # le champ nécessaire à la rasterisation (correspond au niveau 1, 2 puis 3)
    field_name = 'Code_lvl{}'.format(niv)  
    # appel à la fonction
    f.cmd_Rasterization(sample_bdforet_filename=shapefile_path, 
                        out_sample_filename=sample_filename_niv, 
                        image_filename=image_filename, field_name=field_name)

raster_path = image_filename
save_path_template2 = os.path.join(working_directory, 'diag_baton_nb_pix_lvl{column_number}.png')
f.generate_pixel_count_diagrams(shapefile_path, column_name, raster_path, save_path_template2)

########### --- Création de graphiques représentant la signature temporelle de la moyenne
########### --- et l'écart type du ndvi par classe

### Léon

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

generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl1, output_folder, code_lvl[0], bande_names)
generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl2, output_folder,code_lvl[1], bande_names)
generate_temporal_signature_plot(my_folder, image_filename, sample_code_lvl3, output_folder, code_lvl[2], bande_names)



