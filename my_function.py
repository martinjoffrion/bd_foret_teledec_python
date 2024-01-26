# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 09:41:17 2023

@author: ducrocq, joffrion et arondel
"""

import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
from osgeo import gdal
import matplotlib as plt
#testcommentaire
otb_bin_path = os.environ['MYOTB']
##fonction
RAM = os.environ['MYRAM']
import plotly.graph_objects as go
from rasterstats import zonal_stats

def traitement_forest (bd_foret_path, out_dir):
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
    foret = gpd.read_file(bd_foret_path)
    valeurs_a_supprimer = ['Lande', 'Formation herbacée']
    foret_filtre = foret[~foret['TFV'].isin(valeurs_a_supprimer)]
    foret_filtre = foret_filtre[~foret_filtre['TFV'].str.startswith('Forêt ouverte')]
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
    cmd = cmd_pattern.format(in_vector=in_vector, xmin=xmin, ymin=ymin, xmax=xmax,
                         ymax=ymax, out_image=out_image, field_name=field_name,
                         spatial_resolution=spatial_resolution)
    os.system(cmd)


"""
        Pre-traitement Images sentinels
"""


def cmd_ExtractROI(input_img, extraction_vector, output_raster):
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
    otbcli_ExtractROI = f'{otb_bin_path}/otbcli_ExtractROI.bat'
    cmd = (f'{otbcli_ExtractROI}  -mode fit -mode.fit.vect {extraction_vector}'
           f' -in {input_img} -out {output_raster} int16 -ram {RAM}')
    os.system(cmd)

def cmd_Superimpose(inr, inm, output_raster):
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

def cmd_ConcatenateImages(list_image, output_concat, type=None):
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
    rname = os.path.basename(file_path)
    
    rouge = raster.read(red)
    nred = raster.read(pir)
    rouge = rouge.astype('float32')
    nred = nred.astype('float32')
    ndvi = (nred - rouge) / (nred + rouge)
    
    destination_meta = raster.profile
    destination_meta['count'] = 1
    destination_meta['dtype'] = "float32"
    
    raster_sortie = rasterio.open(f'{rdir}/ndvi_{rname}', 'w', **destination_meta)
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


def reprojection (input_raster, epsg_cible, output_raster, dtype=None):
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
    
    srcRst = rasterio.open(input_raster)
    dstCrs = {'init': f'EPSG:{epsg_cible}'}
    
    transform, width, height = calculate_default_transform(
            srcRst.crs, dstCrs, srcRst.width, srcRst.height, *srcRst.bounds)
    
    if dtype==None: dtype=srcRst.read(1).dtype
    
    dstmeta = srcRst.meta.copy()
    dstmeta.update({
            'crs': dstCrs,
            'transform': transform,
            'width': width,
            'height': height,
            'dtype': dtype
        })
    dstRst = rasterio.open(output_raster, 'w', **dstmeta)
    
    for band in range(1, srcRst.count + 1):
        reproject(
            source=rasterio.band(srcRst, band),
            destination=rasterio.band(dstRst, band),
            src_transform=srcRst.transform,
            src_crs=srcRst.crs,
            dst_transform=transform,
            dst_crs=dstCrs,
            resampling=Resampling.nearest)
    srcRst.close()
    dstRst.close()
    
    
def warp( in_img,out_img,code_epsg):
    gdal.Warp (out_img, in_img, dstSRS=f'EPSG:{code_epsg}') 


def cmd_Rasterization(sample_bdforet_filename, out_sample_filename, image_filename, field_name):

    otbcli_Rasterization = f'{otb_bin_path}/otbcli_Rasterization.bat'
    cmd = (f'{otbcli_Rasterization} -in {sample_bdforet_filename} '
           f' -out {out_sample_filename} -im {image_filename} -mode attribute ' 
           f' -mode.attribute.field {field_name}')
    os.system(cmd)


### ----- Fonctions du cours
def get_samples_from_roi(raster_name, roi_name, value_to_extract=None,
                         bands=None, output_fmt='full_matrix'):
    '''
    The function get the set of pixel of an image according to an roi file
    (raster). In case of raster format, both map should be of same
    size.

    Parameters
    ----------
    raster_name : string
        The name of the raster file, could be any file GDAL can open
    roi_name : string
        The path of the roi image.
    value_to_extract : float, optional, defaults to None
        If specified, the pixels extracted will be only those which are equal
        this value. By, defaults all the pixels different from zero are
        extracted.
    bands : list of integer, optional, defaults to None
        The bands of the raster_name file whose value should be extracted.
        Indexation starts at 0. By defaults, all the bands will be extracted.
    output_fmt : {`full_matrix`, `by_label` }, (optional)
        By default, the function returns a matrix with all pixels present in the
        ``roi_name`` dataset. With option `by_label`, a dictionnary
        containing as many array as labels present in the ``roi_name`` data
        set, i.e. the pixels are grouped in matrices corresponding to one label,
        the keys of the dictionnary corresponding to the labels. The coordinates
        ``t`` will also be in dictionnary format.

    Returns
    -------
    X : ndarray or dict of ndarra
        The sample matrix. A nXd matrix, where n is the number of referenced
        pixels and d is the number of variables. Each line of the matrix is a
        pixel.
    Y : ndarray
        the label of the pixel
    t : tuple or dict of tuple
        tuple of the coordinates in the original image of the pixels
        extracted. Allow to rebuild the image from `X` or `Y`
    '''

    # Get size of output array
    raster = gdal.Open(raster_name, gdal.GA_ReadOnly)
    nb_col, nb_row, nb_band = raster.RasterXSize, raster.RasterYSize, raster.RasterCount
    # Get data type
    band = raster.GetRasterBand(1)
    gdal_data_type = gdal.GetDataTypeName(band.DataType)
    
    if gdal_data_type == 'Byte':
        numpy_data_type = 'uint8'
    else:
        numpy_data_type = gdal_data_type.lower()

    # Check if is roi is raster or vector dataset
    roi = gdal.Open(roi_name, gdal.GA_ReadOnly)

    if (raster.RasterXSize != roi.RasterXSize) or \
            (raster.RasterYSize != roi.RasterYSize):
        print('Images should be of the same size')
        print('Raster : {}'.format(raster_name))
        print('Roi : {}'.format(roi_name))
        exit()

    if not bands:
        bands = list(range(nb_band))
    else:
        nb_band = len(bands)

    #  Initialize the output
    ROI = roi.GetRasterBand(1).ReadAsArray()
    if value_to_extract:
        t = np.where(ROI == value_to_extract)
    else:
        t = np.nonzero(ROI)  # coord of where the samples are different than 0

    Y = ROI[t].reshape((t[0].shape[0], 1)).astype('int32')

    del ROI
    roi = None  # Close the roi file

    try:
        X = np.empty((t[0].shape[0], nb_band), dtype=numpy_data_type)
    except MemoryError:
        print('Impossible to allocate memory: roi too large')
        exit()

    # Load the data
    for i in bands:
        temp = raster.GetRasterBand(i + 1).ReadAsArray()
        X[:, i] = temp[t]
    del temp
    raster = None  # Close the raster file

    # Store data in a dictionnaries if indicated
    if output_fmt == 'by_label':
        labels = np.unique(Y)
        dict_X = {}
        dict_t = {}
        for lab in labels:
            coord = np.where(Y == lab)[0]
            dict_X[lab] = X[coord]
            dict_t[lab] = (t[0][coord], t[1][coord])

        return dict_X, Y, dict_t
    else:
        return X, Y, t,
    
    




def report_from_dict_to_df(dict_report):
    # convert report into dataframe
    report_df = pd.DataFrame.from_dict(dict_report)

    # drop unnecessary rows and columns
    try :
        report_df = report_df.drop(['accuracy', 'macro avg', 'weighted avg'], axis=1)
    except KeyError:
        print(dict_report)
        report_df = report_df.drop(['micro avg', 'macro avg', 'weighted avg'], axis=1)

    
    report_df = report_df.drop(['support'], axis=0)
    
    return report_df




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




def generate_pixel_count_diagrams(shapefile_path, column_names, raster_path, save_path_template2):
    # Charger le GeoDataFrame à partir du shapefile
    gdf = gpd.read_file(shapefile_path)

    for class_column in column_names:
        # Extrait le numéro de la colonne (assumant que le format est "Code_lvlXX")
        column_number = ''.join(filter(str.isdigit, class_column))
        # Calculer les statistiques zonales pour chaque polygone
        stats = zonal_stats(gdf.geometry, raster_path, stats='count', all_touched=True)

        # Extraire le nombre de pixels de chaque statistique et l'ajouter à une nouvelle colonne
        pixel_counts = [stat['count'] for stat in stats]
        gdf['nb_pixels'] = pixel_counts

        # Grouper le GeoDataFrame par la classe et calculer la somme des pixels
        pixel_sum_per_class = gdf.groupby(class_column)['nb_pixels'].sum()

        # Créer le graphique à barres
        plt.figure(figsize=(10, 6))
        ax = pixel_sum_per_class.plot(kind='bar', color='blue')  # Ajout de la bordure noire
        plt.title(f'Somme du Nombre de Pixels par {class_column}')
        plt.xlabel(class_column)
        plt.xticks(rotation=45, ha='right')  # Rotation des étiquettes pour une meilleure lisibilité
        plt.ylabel('Somme du Nombre de Pixels')

        # Ajouter une grille à l'arrière
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Ajouter les valeurs de chaque colonne au-dessus des colonnes avec une marge réduite
        for p in ax.patches:
            height = p.get_height()
            width = p.get_width()
            if height > 0:
                ax.annotate(str(int(height)),
                            (p.get_x() + width / 2., height),
                            ha='center', va='bottom')

        # Sauvegarder le graphique avec un nom de fichier basé sur le format spécifié
        save_path = save_path_template2.format(column_number=column_number)
        plt.savefig(save_path)

        # Afficher le graphique
        plt.tight_layout()
        plt.show()
        
   
     
  def generate_temporal_signature_plot(my_folder, image_filename, sample_filename, output_folder, sample_name, band_names):
    # Get samples from ROI
    dict_X, dict_Y, dict_t = get_samples_from_roi(image_filename, sample_filename, output_fmt="by_label")

    # Plotting
    fig = go.Figure()

    for label, X in dict_X.items():
        # Calculate mean and standard deviation along the time axis
        mean_ndvi = np.mean(X, axis=0)
        std_ndvi = np.std(X, axis=0)

        # Plotting mean NDVI with shaded standard deviation
        fig.add_trace(go.Scatter(x=band_names,
                                 y=mean_ndvi,
                                 mode='lines',
                                 line=dict(color=f'rgb({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)})'),
                                 name=f'Class {label}'))

        fig.add_trace(go.Scatter(x=band_names + band_names[::-1],
                                 y=list(mean_ndvi - std_ndvi) + list((mean_ndvi + std_ndvi)[::-1]),
                                 fill='toself',
                                 fillcolor=f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.3)',
                                 line=dict(color='rgba(255,255,255,0)'),
                                 showlegend=False))

    # Update layout for a single-column legend
    fig.update_layout(title=f'Signature temporelle de la moyenne et écart type du ndvi pour le niveau {sample_name}',
                      xaxis_title='Bands',
                      yaxis_title='NDVI',
                      legend=dict(orientation="v", x=1.05, y=1.0),
                      showlegend=True)

    # Save the plot with the sample name in the filename
    output_filename = os.path.join(output_folder, f'temp_mean_ndvi_lvl{sample_name}.html')
    fig.write_html(output_filename)
    # Afficher le graphique
    plt.tight_layout()
    plt.show()
