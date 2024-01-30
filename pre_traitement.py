# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 15:29:41 2023

@author: arondel, ducrocq et joffrion
"""
###############################################################################
##--------------------- CHEMINS D'ACCES A RENSEIGNER ------------------------##
###############################################################################

import glob
import geopandas as gpd
import rasterio
import os

# --- Mettre le chemin d'accès du dossier OTB-8.1.2/bin :
os.environ['MYOTB'] = 'le/chemin/vers/OTB-8.1.2-Win64/bin'

os.environ['MYRAM'] = '8000'
import my_function as f
import shutil

# --- Chemin d'accès du dossier qui comprendra les résultats intermédiaires et les images concaténées par date :
working_directory = 'le/chemin/vers/projet_teledection_sigmaM2_group4/traitement'

# --- Chemin d'accès du dossier comprenant les données d'entrée :
data_path = 'le/chemin/vers/projet_teledection_sigmaM2_group4/data_set'

# --- Chemin d'accès du fichier shapefile de la base de données BD_FORET :
bd_foret = 'le/chemin/vers/projet_teledection_sigmaM2_group4/data_set/FORMATION_VEGETALE.shp'

# --- Chemin d'accès du fichier shapefile de l'emprise d'étude :
roi = 'le/chemin/vers/projet_teledection_sigmaM2_group4/data_set/emprise_etude.shp'


###############################################################################
##----------------------------- PRE-TRAITEMENT ------------------------------##
###############################################################################

# --- Répertoire de travail actuel 
os.chdir(working_directory)

# --- Création d'un nouveau sous-dossier pour y stocker les résultats intermédiaires
os.mkdir(os.path.join(working_directory, 'intermediate_result_pre_traitement'))
# enregistre le chemin complet sous une variable
iwdir = os.path.join(working_directory, 'intermediate_result_pre_traitement')

# --- Création d'un sous-dossier pour y stocker les images concaténées par date
os.mkdir(os.path.join(working_directory, 'date_result_pre_traitement'))
# enregistre le chemin complet sous une variable
ifwdir = os.path.join(working_directory, 'date_result_pre_traitement')

########### --- Découpage et Rasterisation de la BD_FORET

# nettoyage de la donnée et création d'une variable pour le champ raster
gdf_mask, foret_filtre_path = f.traitement_forest(bd_foret, iwdir)
foret_filtre_path = os.path.join(iwdir, foret_filtre_path)
out_image = 'masque_foret.tif'
field = 'raster' # champ necessaire à la rasterisation
# appel de la fonction rasterize_shapefile
f.rasterize_shapefile(foret_filtre_path, out_image, roi, field, 10)

########### --- Vérification du système de projection

# boucle sur le nombre de sous-dossiers dans le dossier data_set (data_path)
files = [os.path.join(data_path, f) for f in os.listdir(data_path)
         if os.path.isdir(os.path.join(data_path, f))]
result_1 = os.path.join(files[0], "*FRE_B2.tif")
img_path = glob.glob(result_1)[0]

img = rasterio.open(img_path)
emprise = gpd.read_file(roi)

# reprojection de l'emprise vectorielle par rapport au SCR des images S2
img_crs = img.crs
emprise_32631 = emprise.to_crs(img_crs)

# sauvegarde de la nouvelle projection de l'emprise
emprise_32631.to_file(os.path.join(iwdir, 'emprise_32631'), driver='ESRI Shapefile')
new_emprise = os.path.join(iwdir, 'emprise_32631')

########### --- Début de la phase de pré-traitement

# créer une liste vide pour les futurs fichiers pré-traités par date
list_date_path = []
# créer une liste vide pour les futurs fichiers NDVI par date
list_ndvi_path = []

for subfil in range(len(files)):
         
    # liste des bandes recherchées
    list_band = ['B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B11', 'B12']
    # créer une liste vide pour le nom de futurs fichiers par bande
    list_band_name = []
    for i in range (len(list_band)):
        result = os.path.join(files[subfil], f"*FRE_{list_band[i]}.tif")
        result = glob.glob(result)
        if result == [] : result.append(' ')
        band = result[0]
        list_band_name.append(band)
    
    # convertir les "lists" en "dictionary"
    dict_band = {list_band[i]: list_band_name[i] for i in range(len(list_band))}   
            
########### --- Découpage du raster selon le shapefile de l'emprise
    
    # créer une liste vide pour le nom de futurs fichiers par bande coupée
    list_bande_cut = []
    
    for i in range (len(list_band_name)):
        input_img = list_band_name[i]
        band_name = os.path.basename(input_img)
        name = 'cut{band_name}'
        output_raster = os.path.join(iwdir, name.format(band_name=band_name))
        # appel de la fonction cmd_ExtractROI
        f.cmd_ExtractROI(input_img, new_emprise, output_raster)
        list_bande_cut.append(output_raster)
        
    # convertir les "lists" en "dictionary"
    dict_band = {list_band[i]: list_bande_cut[i] for i in range(len(list_band))}   
    
    # créer la liste des bandes à 20m de résolution
    list_bande_20m_plus = [dict_band.get(x) for x in ['B5', 'B6', 'B7', 'B11', 'B12']]
    
    # créer la liste des bandes à 10m de résolution
    list_band_10m = [dict_band.get(x) for x in ['B3', 'B4', 'B8']]
    
    # créer une liste vide pour le chemin d'accès des futurs fichiers générés après le rééchantillonnage
    list_bande_finale = []
    
########### --- Rééchantillonage des images
    
    for i in range(len(list_bande_20m_plus)):
        inr = list_band_10m[0]
        inm = list_bande_20m_plus[i]
        band_name = os.path.basename(inm)
        name = '_10m_{band_name}'
        output_raster = os.path.join(iwdir, name.format(band_name=band_name))
        # appel de la fonction cmd_Superimpose
        f.cmd_Superimpose(inr, inm, output_raster)
        list_bande_finale.append(output_raster)
    
    list_bande_finale = list_band_10m + list_bande_finale

########### --- Concaténation 

    # appel de la fonction get_date_f_b_path
    date =  f.get_date_f_b_path(list_bande_finale[0]) # recupération la date de la première bande
    name = 'output_{date}_date.tif'
    output_concat = os.path.join(iwdir, name.format(date=date))
    # appel de la fonction cmd_ConcatenateImages
    f.cmd_ConcatenateImages(list_bande_finale, output_concat)
    list_date_path.append(output_concat)
    
########### --- NDVI

    # appel de la fonction rasterio_ndvi (la B2 correspond à la B4 (rouge) et la B3 à la B5 (infrarouge)) 
    ndvi_path = f.rasterio_ndvi(output_concat, 2, 3)
    list_ndvi_path.append(ndvi_path)

########### --- Concaténation finale des 6 dates

output_concat = 'Serie_temp_S2_allbands.tif'
f.cmd_ConcatenateImages(list_date_path, os.path.join(iwdir, output_concat), 'uint16')
f.warp(os.path.join(iwdir, output_concat), os.path.join(ifwdir, output_concat), '2154')
f.apply_mask(os.path.join(ifwdir, output_concat), output_concat, gdf_mask)

########### --- Concaténation finale des NDVI

output_concat = 'Serie_temp_S2_ndvi.tif'
f.cmd_ConcatenateImages(list_ndvi_path, os.path.join(iwdir, output_concat), 'float')
f.warp(os.path.join(iwdir, output_concat), os.path.join(ifwdir, output_concat), '2154')
f.apply_mask(os.path.join(ifwdir, output_concat), output_concat, gdf_mask)

########### --- Suppression des résultats intermédiaires

shutil.rmtree(iwdir)

