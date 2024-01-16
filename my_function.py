# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 09:41:17 2023

@author: dsii
"""

import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from osgeo import gdal
import matplotlib as plt
#testcommentaire
otb_bin_path = os.environ['MYOTB']
##fonction
RAM = os.environ['MYRAM']

"""
        Traitement de la bd foret
"""

def traitement_forest (bd_foret_path,out_dir):
    '''

    Parameters
    ----------
    bd_foret_path : STR
        DESCRIPTION.
    out_dir : STR
        DESCRIPTION.

    Returns
    -------
    foret_filtre : Geodataframe
        DESCRIPTION.
    foret_filtre_path : STR
        DESCRIPTION.

    '''
    #Open vector file
    foret = gpd.read_file(bd_foret_path)
    #Identifier les valeurs à supprimer
    valeurs_a_supprimer = ['Lande', 'Formation herbacée']
    #supprime les valeurs de la bd foret non souhaité
    foret_filtre = foret[~foret['TFV'].isin(valeurs_a_supprimer)]
    foret_filtre = foret_filtre[~foret_filtre['TFV'].str.startswith('Forêt ouverte')]
    #ajout d'un champs "raster" = 1 pour rasteriser      
    foret_filtre['raster'] = 1 
    foret_filtre.to_file(f'{out_dir}/bd_foret', driver="ESRI Shapefile")
    foret_filtre_path = 'bd_foret/bd_foret.shp'
    
    return foret_filtre, foret_filtre_path

def rasterize_shapefile(in_vector, out_image, emprise_etude, field_name, spatial_resolution):
    '''
    Parameters
    ----------
    in_vector : STR
        DESCRIPTION. BD_foret avec les modifications apportées : suppress
        
    out_image : STR
        DESCRIPTION. chemin de sortie de la rasterisation
        
    emprise_etude : STR 
        DESCRIPTION. shapefile emprise d'étude
    
    spatial_resolution : INT
        DESCRIPTION. integer of the target spatial resolution

    '''
    
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
    
    os.system(cmd)# execute the command in the terminal


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
           f' -in {input_img} -out {output_raster} int16 -ram {RAM}')
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
           f' -out {output_raster} int16 -ram {RAM}')
    os.system(cmd)
    

def cmd_ConcatenateImages(list_image, output_concat, type = None):
    '''

    Parameters
    ----------
    list_image : STR
        DESCRIPTION.
    output_concat : STR
        DESCRIPTION.
    type : STR OPTIONAL

    Returns
    -------
    None.

    '''
    if type == None: type = 'int16'
    list_image_str = ' '.join(list_image)
    #ou faire plutôt : list_image_str = ['{' + img_name + '}' for img_name in list_image] #pour avoir le format de ce qui est demandé par la fonction OTB
    #chemin {'chemin_img1'}{'chemin_img2'}etc...
    otbcli_ConcatenateImages = f'{otb_bin_path}/otbcli_ConcatenateImages.bat'
    cmd = (f'{otbcli_ConcatenateImages}  -il {list_image_str}'
           f' -out {output_concat} {type} -ram {RAM}')
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
    b = [x for x in b_ if len(x) == 8 and int(x)>20000000]
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
    ndvi = (nred - rouge) / (nred + rouge)
    
    destination_meta = raster.profile
    # Changement du nombre de bande en sortie (1 seule pour le NDVI)
    destination_meta['count'] = 1
    # Changement de type de données stockées (de unint16 à float32)
    destination_meta['dtype'] = "float32"
    
    raster_sortie = rasterio.open(f'{rdir}/ndvi_{rname}','w', **destination_meta)
    raster_sortie.write(ndvi, 1)
    ndvi_path = f'{rdir}/ndvi_{rname}'
    raster.close
    
    return ndvi_path

def apply_mask (fp_in_image,fp_out_image,gdf_mask):
    '''

    Parameters
    ----------
    fp_in_image : STR
        DESCRIPTION.
    fp_out_image : STR
        DESCRIPTION.
    gdf_mask : Geodataframe
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    gdf_mask = gdf_mask.dissolve()
    
    with rasterio.open(fp_in_image) as source:
        emprise = gdf_mask.to_crs(source.crs)
        out_image, out_transform = mask(source, emprise.geometry,crop=True)
        out_meta = source.meta.copy() 
        out_meta.update({"driver": "GTiff", 
                     "height": out_image.shape[1], 
                     "width": out_image.shape[2],
                     "transform": out_transform,
                     'nodata': '0'})
        source.close()
        
    with rasterio.open(fp_out_image, "w", **out_meta) as destination:
        destination.write(out_image)
        destination.close()


def reprojection (input_raster, epsg_cible ,output_raster, dtype=None):
    '''
    
    Parameters
    ----------
    input_raster : STR
        Path input raster to reproject.
    epsg_cible : STR
        EPSG code of the target CRS.
    output_raster : STR
        Path output reproject raster to save. 
    dtype : STR, optional
    Numpy data type
    
    Returns
    -------
    None.

    '''
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    
    #open source raster
    srcRst = rasterio.open(input_raster)
    dstCrs = {'init': f'EPSG:{epsg_cible}'}
    
    #calculate transform array and shape of reprojected raster
    transform, width, height = calculate_default_transform(
            srcRst.crs, dstCrs, srcRst.width, srcRst.height, *srcRst.bounds)
    
    if dtype==None : dtype=srcRst.read(1).dtype
    
    #Update the destination meta
    dstmeta = srcRst.meta.copy()
    dstmeta.update({
            'crs': dstCrs,
            'transform': transform,
            'width': width,
            'height': height,
            'dtype': dtype
        })
    #open destination raster
    dstRst = rasterio.open(output_raster, 'w', **dstmeta)
    #reproject and save raster band data
    
    for band in range(1, srcRst.count + 1):
        reproject(
            source=rasterio.band(srcRst, band),
            destination=rasterio.band(dstRst, band),
            src_transform=srcRst.transform,
            src_crs=srcRst.crs,
            dst_transform=transform,
            dst_crs=dstCrs,
            resampling=Resampling.nearest)
    #close destination raster
    srcRst.close()
    dstRst.close()
    
    
def warp( in_img,out_img,code_epsg):
    gdal.Warp (out_img, in_img, dstSRS=f'EPSG:{code_epsg}') 

#Création des digrammes du nombre de polygones par classe 
def create_polygons_bar_charts(shapefile_path, column_names, save_path_template):
    # Charger le shapefile
    gdf = gpd.read_file(shapefile_path)

    for column_name in column_names:
        # Extrait le numéro de la colonne (assumant que le format est "Code_lvlXX")
        column_number = ''.join(filter(str.isdigit, column_name))

        # Compter le nombre de polygones par valeur de la colonne spécifiée
        count_by_column = gdf[column_name].value_counts()

        # Créer le graphique
        plt.figure(figsize=(10, 6))
        ax = count_by_column.plot(kind='bar', color='darkgreen')
        plt.title(f'Nombre de Polygones par {column_name}')
        plt.xlabel(column_name)
        plt.ylabel('Nombre de Polygones')
        plt.xticks(rotation=45, ha='right')  # Rotation des étiquettes pour une meilleure lisibilité
        plt.tight_layout()

        # Ajouter une légende
        plt.legend(['Nombre de Polygones'], loc='upper right')

        # Ajouter une grille à l'arrière
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Annoter chaque barre avec sa valeur
        for i, v in enumerate(count_by_column):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=8)

        # Sauvegarder le graphique avec un nom de fichier basé sur le format spécifié
        save_path = save_path_template.format(column_number=column_number)
        plt.savefig(save_path)

        # Afficher le graphique si nécessaire
        plt.show()

