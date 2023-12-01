# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 09:41:17 2023

@author: dsii
"""
!pip install osgeo
import os
import rasterio
import geopandas as gpd
from osgeo import gdal
#testcommentaire
otb_bin_path = os.environ['MYOTB']
##fonction

"""
        Traitement de la bd foret
"""
def traitement_bd_foret(bd_foret, emprise_etude, folder_traitement):
    
    foret = gpd.read_file(bd_foret)
    emprise = gpd.read_file(emprise_etude)
    # Identifier les valeurs à supprimer
    valeurs_a_supprimer = ['Lande', 'Formation herbacée'] #données a supprimer dans la bd foret
    foret_filtre = foret[~foret['TFV'].isin(valeurs_a_supprimer)] #supprime les valeurs de la bd foret non souhaité
    foret_filtre['raster'] = 1 #ajout d'un champs "raster" avec comme valeur 1 à la bd foret
    intersection = gpd.overlay(foret_filtre, emprise, how='intersection')
    intersection.to_file(folder_traitement, driver="ESRI Shapefile")


def rasterize_shapefile(in_vector, out_image, emprise_etude):
    '''
    Parameters
    ----------
    in_vector : TYPE shapefile
        DESCRIPTION. BD_foret avec les modifications apportées : suppress
        
    out_image : TYPE 
        DESCRIPTION. chemin de sortie de la rasterisation
        
    emprise_etude : TYPE shapefile
        DESCRIPTION. emprise d'étude pour découper la 

    '''
    spatial_resolution = 10
    field_name = 'raster'
    coordonnees_emprise = gpd.read_file(emprise_etude)
    xmin, ymin, xmax, ymax = coordonnees_emprise.total_bounds
    cmd_pattern = ("gdal_rasterize -a {field_name} "
               "-tr {spatial_resolution} {spatial_resolution} "
               "-te {xmin} {ymin} {xmax} {ymax} -ot Byte -of GTiff "
               "{in_vector} {out_image}")

    # fill the string with the parameter thanks to format function
    cmd = cmd_pattern.format(in_vector=in_vector, xmin=xmin, ymin=ymin, xmax=xmax,
                         ymax=ymax, out_image=out_image, field_name=field_name,
                         spatial_resolution=spatial_resolution)
    return cmd

"""
        Pre-traitement Images sentinels
"""


def cmd_ExtractROI(input_img,extraction_vector,output_raster):
    '''

    Parameters
    ----------
    list_image : STR
        DESCRIPTION.
    output_concat : STR
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    #découpage du raster selon le fichier emprise
    otbcli_ExtractROI = f'{otb_bin_path}/otbcli_ExtractROI.bat'
    cmd = (f'{otbcli_ExtractROI}  -mode fit -mode.fit.vect {extraction_vector}'
           f' -in {input_img} -out {output_raster} int16')
    os.system(cmd)


def cmd_Superimpose(inr,inm,output_raster):
    '''

    Parameters
    ----------
    list_image : STR
        DESCRIPTION.
    output_concat : STR
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    otbcli_Superimpose = f'{otb_bin_path}/otbcli_Superimpose.bat'
    cmd = (f'{otbcli_Superimpose} -inr {inr} -inm {inm} -interpolator nn'
           f' -out {output_raster} int16 ')
    os.system(cmd)
    

def cmd_ConcatenateImages(list_image, output_concat):
    '''

    Parameters
    ----------
    list_image : STR
        DESCRIPTION.
    output_concat : STR
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    list_image_str = ' '.join(list_image)
    #ou faire plutôt : list_image_str = ['{' + img_name + '}' for img_name in list_image] #pour avoir le format de ce qui est demandé par la fonction OTB
    #chemin {'chemin_img1'}{'chemin_img2'}etc...
    otbcli_ConcatenateImages = f'{otb_bin_path}/otbcli_ConcatenateImages.bat'
    cmd = (f'{otbcli_ConcatenateImages}  -il {list_image_str}'
           f' -out {output_concat} int16')
    os.system(cmd)

def get_date_f_b_path(str_band_path):
        '''

    Parameters
    ----------
    date : STR
        DESCRIPTION.

    Returns
    -------
    b_date : STR
        DESCRIPTION.

    '''
    b_ = os.path.basename(str_band_path)
    b_ = b_.replace('-','_').split('_')
    b = [x for x in split if len(x) == 8 and int(x)>20000000]
    b_date = b[0]
    return b_date



def rasterio_ndvi (file_path, red, pir):
    '''

    Parameters
    ----------
    file_path : STR
        DESCRIPTION.
    red : INT
        DESCRIPTION.
    pir : INT
        DESCRIPTION.

    Returns
    -------
    ndvi_path : STR
        DESCRIPTION.

    '''
    
    raster = rasterio.open(file_path)
    rdir = os.path.dirname(file_path)
    rname= os.path.basename(file_path)
    
    rouge = raster.read(red)
    nred = raster.read(pir)
    rouge = rouge.astype('float32')
    nred = nred.astype('float32')
    ndvi = (pir - rouge) / (pir + rouge)
    
    destination_meta = raster.profile
    # Changement du nombre de bande en sortie (1 seule pour le NDVI)
    destination_meta['count'] = 1
    # Changement de type de données stockées (de unint16 à float32)
    destination_meta['dtype'] = "float32"
    
    raster_sortie = rasterio.open(f'{rdir}/ndvi_{rname}','w', **destination_meta)
    raster_sortie.write(ndvi, 1)
    ndvi_path = f'{rdir}\ndvi_{rname}'
    
    return ndvi_path

    
    
    
    
    
    
    
