# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 09:41:17 2023

@author: arondel, ducrocq et joffrion
"""

import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
from osgeo import gdal
import matplotlib as plt
import plotly.graph_objects as go
from rasterstats import zonal_stats
import sys
otb_bin_path = os.environ['MYOTB']
RAM = os.environ['MYRAM']


###############################################################################
##--------------------------- Fonctions créées -----------------------------##
###############################################################################

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
    foret_filtre.to_file(f'{out_dir}/bd_foret', driver = "ESRI Shapefile")
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
    cmd = (f'{otbcli_ConcatenateImages} -il {list_image_str}'
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
    b_ = b_.replace('-', '_').split('_')
    b = [x for x in b_ if len(x) == 8 and int(x) > 20000000]
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


def apply_mask (fp_in_image, fp_out_image, gdf_mask):
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
    
    if dtype == None: dtype=srcRst.read(1).dtype
    
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
            source = rasterio.band(srcRst, band),
            destination = rasterio.band(dstRst, band),
            src_transform = srcRst.transform,
            src_crs = srcRst.crs,
            dst_transform = transform,
            dst_crs = dstCrs,
            resampling = Resampling.nearest)
    srcRst.close()
    dstRst.close()
    
    
def warp( in_img, out_img, code_epsg):
    gdal.Warp (out_img, in_img, dstSRS=f'EPSG: {code_epsg}') 

# Création des diagrammes baton du nombre de polygones par classe 

def create_polygons_bar_charts(shapefile_path, column_names, save_path_template):
    '''
    
    La fonction permet de compter le nombre de polygone pour chaque classe de la colonne spécifiée et de 
    générer des diagrammes en baton des résultats
    
    Parameters
    ----------
    shapefile_path : shapefile (BD_foret)
    column_names : Colonnes sur lesquelles la fonction va générer les diagrammes batons
    save_path_template :  Emplacement et nom en sortie des diagrammes batons
    
    '''
    
    # Charger le shapefile
    gdf = gpd.read_file(shapefile_path)

    for column_name in column_names:
        # Extrait le numéro de la colonne (assumant que le format est "Code_lvlXX")
        column_number = ''.join(filter(str.isdigit, column_name))

        # Compter le nombre de polygones par valeur de la colonne spécifiée
        count_by_column = gdf[column_name].value_counts()

        # Créer le graphique
        plt.figure(figsize=(10, 6))
        ax = count_by_column.plot(kind='bar', color='mediumseagreen')
        plt.title('Répartition des essences de la BD Forêt', weight='bold', fontsize=18)
        plt.xlabel(f'Nomenclature utilisée : {column_name}', weight='bold')
        plt.ylabel('Nombre de polygones', weight='bold')
        plt.xticks(rotation=25, ha='right')  # Rotation des étiquettes pour une meilleure lisibilité
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
    '''
    
    La fonction permet de compter le nombre de pixel contenu dans les polygones de chaque classe de la colonne spécifiée 
    en entrée et de générer des diagrammes en baton des résultats
    
    Parameters
    ----------
    shapefile_path : shapefile (BD_foret)
    column_names : Colonnes sur lesquelles la fonction va générer les diagrammes batons
    raster_path : Image en entrée sur laquelle est comptée le nombre de pixel pour chaque polygone de la BD_foret
    save_path_template2 :  Emplacement et nom en sortie des diagrammes batons

    '''
    
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
        pixel_sum_per_class = gdf.groupby(class_column)['nb_pixels'].sum().sort_values(ascending=False)

        # Créer le graphique à barres
        plt.figure(figsize=(10, 6))
        ax = pixel_sum_per_class.plot(kind='bar', color='forestgreen')  # Ajout de la bordure noire
        plt.title('Nombre de pixels contenus dans les polygones par classe', weight='bold', fontsize=18)
        plt.xlabel(f'Nomenclature utilisée : {class_column}', weight='bold')
        plt.xticks(rotation=25, ha='right')  # Rotation des étiquettes pour une meilleure lisibilité
        plt.ylabel('Somme du nombre de pixels', weight='bold')

        # Ajouter une grille à l'arrière
        plt.grid(axis = 'y', linestyle='--', alpha = 0.7)

        # Ajouter les valeurs de chaque colonne au-dessus des colonnes avec une marge réduite
        for p in ax.patches:
            height = p.get_height()
            width = p.get_width()
            if height > 0:
                ax.annotate(str(int(height)),
                            (p.get_x() + width / 2., height),
                            ha='center', va='bottom')

        # Ajuster les marges pour agrandir le cadre
        plt.subplots_adjust(bottom=0.3)

        # Sauvegarder le graphique avec un nom de fichier basé sur le format spécifié
        save_path = save_path_template2.format(column_number=column_number)
        plt.savefig(save_path)

        # Afficher le graphique
        plt.tight_layout()
        plt.show()


def generate_temporal_signature_plot(my_folder, image_filename, sample_filename, code_lvl, band_names):
    '''
    
    Cette fonction permet de générer un graphique de la signature spectrale moyenne et de l'écart type pour chaque bande
    d'un NDVI par classe.

    Parameters
    ----------
    my_folder : Environnement ou vont être enregistré tous les graphiques générés par la fonction
    
    image_filename : Chemin d'accès pour le NDVI en entrée
    
    sample_filename : Chemin d'accès pour les différents sample rasterisés en entrée
        
    code_lvl : est une liste contenant 3 valeurs de 1 à 3 permettant d'afficher le bon niveau de nomenclature
    dans le nom en sortie
    
    band_names : Une liste qui est utilisée dans la fonction afficher les dates en abscisse

    '''
    
    # Get samples from ROI
    dict_X, dict_Y, dict_t = get_samples_from_roi(image_filename, sample_filename, output_fmt="by_label")

    # Plotting
    fig = go.Figure()

    for label, X in dict_X.items():
        # Calculate mean and standard deviation along the time axis
        mean_ndvi = np.mean(X, axis=0)
        std_ndvi = np.std(X, axis=0)
        rgb = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
        rgb = ','.join(map(str, rgb))
        # Plotting mean NDVI with shaded standard deviation
        fig.add_trace(go.Scatter(x=band_names,
                                 y=mean_ndvi,
                                 mode='lines',
                                 line=dict(color=f'rgb({rgb})'),
                                 name=f'Class {label}'))

        fig.add_trace(go.Scatter(x = band_names + band_names[::-1],
                                 y = list(mean_ndvi - std_ndvi) + list((mean_ndvi + std_ndvi)[::-1]),
                                 fill = 'toself',
                                 fillcolor = f'rgba({rgb}, 0.3)',
                                 line=dict(color = 'rgba(255,255,255,0)'),
                                 name = f'Std {label}',
                                 showlegend = True))
        
    # Update layout for a single-column legend
    fig.update_layout(title=f'Signature temporelle de la moyenne et écart type du NDVI pour le niveau {code_lvl}',
                      xaxis_title='Dates des images',
                      yaxis_title='Valeurs NDVI', 
                      legend=dict(orientation="v", x=1.05, y=1.0),
                      showlegend=True)
    
    # Save the plot with the sample name in the filename
    output_filename = os.path.join(my_folder, f'temp_mean_ndvi{code_lvl}.html')
    fig.write_html(output_filename)

    print(f"Plot for {code_lvl} saved successfully.")
  

def cmd_Rasterization(sample_bdforet_filename, out_sample_filename, image_filename, field_name):
    '''

    Parameters
    ----------
    sample_bdforet_filename : STR
        DESCRIPTION.
    out_sample_filename : STR
        DESCRIPTION.
    image_filename : STR
        DESCRIPTION.
    field_name : STR
        DESCRIPTION. Field to rasterize

    Returns
    -------
    None.

    '''

    otbcli_Rasterization = f'{otb_bin_path}/otbcli_Rasterization.bat'
    cmd = (f'{otbcli_Rasterization} -in {sample_bdforet_filename} '
           f' -out {out_sample_filename} -im {image_filename} -mode attribute ' 
           f' -mode.attribute.field {field_name}')
    os.system(cmd)


def agg_metrics (list_cm ,list_accuracy, list_report) :
    '''

    Parameters
    ----------
    list_cm : TYPE
        DESCRIPTION.
    list_accuracy : TYPE
        DESCRIPTION.
    list_report : TYPE
        DESCRIPTION.

    Returns
    -------
    mean_cm : ARRAY
        DESCRIPTION.
    mean_accuracy : FLOAT
        DESCRIPTION.
    std_accuracy : FLOAT
        DESCRIPTION.
    mean_df_report : DATAFRAME
        DESCRIPTION.
    std_df_report : DATAFRAME
        DESCRIPTION.

    '''
    
    # compute mean of cm
    array_cm = np.array(list_cm)
    mean_cm = array_cm.mean(axis=0)
    # compute mean and std of overall accuracy
    array_accuracy = np.array(list_accuracy)
    mean_accuracy = array_accuracy.mean()
    std_accuracy = array_accuracy.std()
    # compute mean and std of classification report
    array_report = np.array(list_report)
    mean_report = array_report.mean(axis=0)
    std_report = array_report.std(axis=0)
    a_report = list_report[0]
    mean_df_report = pd.DataFrame(mean_report, index=a_report.index,
                                  columns=a_report.columns)
    std_df_report = pd.DataFrame(std_report, index=a_report.index,
                                 columns=a_report.columns)
    
    return mean_cm, mean_accuracy, std_accuracy, mean_df_report, std_df_report


def plot_class_metrics (mean_oa, std_oa, mean_report, std_report, out_qualite):
    '''

    Parameters
    ----------
    mean_oa : TYPE
        DESCRIPTION.
    std_oa : TYPE
        DESCRIPTION.
    mean_report : TYPE
        DESCRIPTION.
    std_report : TYPE
        DESCRIPTION.
    out_qualite : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    # Display class metrics
    fig, ax = plt.subplots(figsize=(10, 7))
    ax = mean_report.T.plot.bar(ax=ax, yerr=std_report.T, zorder=2)
    ax.set_ylim(0, 1)
    _ = ax.text(1.5, 0.95, 'OA : {:.2f} +- {:.2f}'.format(mean_oa,
                                                          std_oa),
                fontsize=14)
    ax.set_title('Class quality estimation')

    # custom : cuteness
    # background color
    ax.set_facecolor('ivory')
    # labels
    x_label = ax.get_xlabel()
    ax.set_xlabel(x_label, fontdict={'fontname': 'Sawasdee'}, fontsize=14)
    y_label = ax.get_ylabel()
    ax.set_ylabel(y_label, fontdict={'fontname': 'Sawasdee'}, fontsize=14)
    # borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis='x', colors='darkslategrey', labelsize=14)
    ax.tick_params(axis='y', colors='darkslategrey', labelsize=14)
    # grid
    ax.minorticks_on()
    ax.yaxis.grid(which='major', color='darkgoldenrod', linestyle='--',
                  linewidth=0.5, zorder=1)
    ax.yaxis.grid(which='minor', color='darkgoldenrod', linestyle='-.',
                  linewidth=0.3, zorder=1)
    plt.savefig(out_qualite, bbox_inches='tight')

def display_metrics (list_metrics, out_matrix, out_qualite):

    # Display confusion matrix
    plot_cm(list_metrics[0], list_metrics[3].columns.values, out_matrix)
    #plt.savefig(out_matrix, bbox_inches='tight')
    
    plot_class_metrics(list_metrics[1],list_metrics[2],
                       list_metrics[3],list_metrics[4],
                       out_qualite)


###############################################################################
##--------------------------- Fonctions du cours ----------------------------##
###############################################################################

########### --- Ces fonctions proviennent du script read_and_write.py

"""
Created on Wed Mar  1 10:35:21 2017

@author: marc lang
"""

def open_image(filename, verbose=False):
  """
  Open an image file with gdal

  Paremeters
  ----------
  filename : str
      Image path to open

  Return
  ------
  osgeo.gdal.Dataset
  """
  data_set = gdal.Open(filename, gdal.GA_ReadOnly)

  if data_set is None:
      print('Impossible to open {}'.format(filename))
  elif data_set is not None and verbose:
      print('{} is open'.format(filename))

  return data_set


def get_image_dimension(data_set, verbose=False):
    """
    get image dimensions

    Parameters
    ----------
    data_set : osgeo.gdal.Dataset

    Returns
    -------
    nb_lignes : int
    nb_col : int
    nb_band : int
    """

    nb_col = data_set.RasterXSize
    nb_lignes = data_set.RasterYSize
    nb_band = data_set.RasterCount
    if verbose:
        print('Number of columns :', nb_col)
        print('Number of lines :', nb_lignes)
        print('Number of bands :', nb_band)

    return nb_lignes, nb_col, nb_band


def get_origin_coordinates(data_set, verbose=False):
    """
    get origin coordinates

    Parameters
    ----------
    data_set : osgeo.gdal.Dataset

    Returns
    -------
    origin_x : float
    origin_y : float
    """
    geotransform = data_set.GetGeoTransform()
    origin_x, origin_y = geotransform[0], geotransform[3]
    if verbose:
        print('Origin = ({}, {})'.format(origin_x, origin_y))

    return origin_x, origin_y


def get_pixel_size(data_set, verbose=False):
    """
    get pixel size

    Parameters
    ----------
    data_set : osgeo.gdal.Dataset

    Returns
    -------
    psize_x : float
    psize_y : float
    """
    geotransform = data_set.GetGeoTransform()
    psize_x, psize_y = geotransform[1],geotransform[5]
    if verbose:
        print('Pixel Size = ({}, {})'.format(psize_x, psize_y))

    return psize_x, psize_y


def convert_data_type_from_gdal_to_numpy(gdal_data_type):
    """
    convert data type from gdal to numpy style

    Parameters
    ----------
    gdal_data_type : str
        Data type with gdal syntax
    Returns
    -------
    numpy_data_type : str
        Data type with numpy syntax
    """
    if gdal_data_type == 'Byte':
        numpy_data_type = 'uint8'
    else:
        numpy_data_type = gdal_data_type.lower()
    return numpy_data_type


def load_img_as_array(filename, verbose=False):
    """
    Load the whole image into an numpy array with gdal

    Paremeters
    ----------
    filename : str
        Path of the input image

    Returns
    -------
    array : numpy.ndarray
        Image as array
    """

    # Get size of output array
    data_set = open_image(filename, verbose=verbose)
    nb_lignes, nb_col, nb_band = get_image_dimension(data_set, verbose=verbose)

    # Get data type
    band = data_set.GetRasterBand(1)
    gdal_data_type = gdal.GetDataTypeName(band.DataType)
    numpy_data_type = convert_data_type_from_gdal_to_numpy(gdal_data_type)

    # Initialize an empty array
    array = np.empty((nb_lignes, nb_col, nb_band), dtype=numpy_data_type)

    # Fill the array
    for idx_band in range(nb_band):
        idx_band_gdal = idx_band + 1
        array[:, :, idx_band] = data_set.GetRasterBand(idx_band_gdal).ReadAsArray()

    # close data_set
    data_set = None
    band = None

    return array


def write_image(out_filename, array, data_set=None, gdal_dtype=None,
                transform=None, projection=None, driver_name=None,
                nb_col=None, nb_ligne=None, nb_band=None):
    """
    Write a array into an image file.

    Parameters
    ----------
    out_filename : str
        Path of the output image.
    array : numpy.ndarray
        Array to write
    nb_col : int (optional)
        If not indicated, the function consider the `array` number of columns
    nb_ligne : int (optional)
        If not indicated, the function consider the `array` number of rows
    nb_band : int (optional)
        If not indicated, the function consider the `array` number of bands
    data_set : osgeo.gdal.Dataset
        `gdal_dtype`, `transform`, `projection` and `driver_name` values
        are infered from `data_set` in case there are not indicated.
    gdal_dtype : int (optional)
        Gdal data type (e.g. : gdal.GDT_Int32).
    transform : tuple (optional)
        GDAL Geotransform information same as return by
        data_set.GetGeoTransform().
    projection : str (optional)
        GDAL projetction information same as return by
        data_set.GetProjection().
    driver_name : str (optional)
        Any driver supported by GDAL. Ignored if `data_set` is indicated.
    Returns
    -------
    None
    """
    # Get information from array if the parameter is missing
    nb_col = nb_col if nb_col is not None else array.shape[1]
    nb_ligne = nb_ligne if nb_ligne is not None else array.shape[0]
    array = np.atleast_3d(array)
    nb_band = nb_band if nb_band is not None else array.shape[2]


    # Get information from data_set if provided
    transform = transform if transform is not None else data_set.GetGeoTransform()
    projection = projection if projection is not None else data_set.GetProjection()
    gdal_dtype = gdal_dtype if gdal_dtype is not None \
        else data_set.GetRasterBand(1).DataType
    driver_name = driver_name if driver_name is not None \
        else data_set.GetDriver().ShortName

    # Create DataSet
    driver = gdal.GetDriverByName(driver_name)
    output_data_set = driver.Create(out_filename, nb_col, nb_ligne, nb_band,
                                    gdal_dtype)
    output_data_set.SetGeoTransform(transform)
    output_data_set.SetProjection(projection)

    # Fill it and write image
    for idx_band in range(nb_band):
        output_band = output_data_set.GetRasterBand(idx_band + 1)
        output_band.WriteArray(array[:, :, idx_band])  # not working with a 2d array.
                                                       # this is what np.atleast_3d(array)
                                                       # was for
        output_band.FlushCache()

    del output_band
    output_data_set = None


def xy_to_rowcol(x, y, image_filename):
    """
    Convert geographic coordinates into row/col coordinates

    Paremeters
    ----------
    x : float
      x geographic coordinate
    y : float
        y geographic coordinate
    image_filename : str
        Path of the image.

    Returns
    -------
    row : int
    col : int
    """
    # get image infos
    data_set = open_image(image_filename)
    origin_x, origin_y = get_origin_coordinates(data_set)
    psize_x, psize_y = get_pixel_size(data_set)

    # convert x y to row col
    col = int((x - origin_x) / psize_x)
    row = - int((origin_y - y) / psize_y)

    return row, col


def get_xy_from_file(filename):
    """
    Get x y coordinates from a vector point file

    Parameters
    ----------
    filename : str
        Path of the vector point file

    Returns
    -------
    list_x : np.array
    list_y : np.array
    """
    gdf = gpd.read_file(filename)
    geometry = gdf.loc[:, 'geometry']
    list_x = geometry.x.values
    list_y = geometry.y.values

    return list_x, list_y

def get_row_col_from_file(point_file, image_file):
    """
    Getrow col image coordinates from a vector point file
    and image file

    Parameters
    ----------
    point_file : str
        Path of the vector point file
    image_file : str
        Path of the raster image file

    Returns
    -------
    list_row : np.array
    list_col : np.array
    """
    list_row = []
    list_col = []
    list_x, list_y = get_xy_from_file(point_file)
    for x, y in zip(list_x, list_y):
        row, col = xy_to_rowcol(x, y, image_file)
        list_row.append(row)
        list_col.append(col)
    return list_row, list_col


def get_data_for_scikit(point_file, image_file, field_name):
    """
    Get a sample matrix and a label matrix from a point vector file and an
    image.

    Parameters
    ----------
    point_file : str
        Path of the vector point file
    image_file : str
        Path of the raster image file
    field_name : str
        Field name containing the numeric label of the sample.

    Returns
    -------
     X : ndarray or dict of ndarra
        The sample matrix. A nXd matrix, where n is the number of referenced
        pixels and d is the number of variables. Each line of the matrix is a
        pixel.
    Y : ndarray
        the label of the pixel
    """

    list_row, list_col = get_row_col_from_file(point_file, image_file)
    image = load_img_as_array(image_file)
    X = image[(list_row, list_col)]

    gdf = gpd.read_file(point_file)
    Y = gdf.loc[:, field_name].values
    Y = np.atleast_2d(Y).T

    return X, Y

########### --- Ces fonctions proviennent du script plots.py

"""
Created on 06/4/2020

@author: Marc LANG
@mail: marc.lang@toulouse-inp.fr
"""
from museotoolbox.charts import PlotConfusionMatrix
from matplotlib.pyplot import cm as colorMap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_cm(cm, labels, out_filename=None):
    """
    Plot a confusion matrix

    Parameters
    ----------
    cm : np.array
        Confusion matrix, reference are expected in rows and prediction in
        columns
    labels : list of string,
        Labels of the classes.
    out_filename : str (optional)
        If indicated, the chart is saved at the `out_filename` location
    """
    fig1, ax1 = plt.subplots(figsize=(16, 12))
    ax1.set_frame_on(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1 = PlotConfusionMatrix(cm, cmap=colorMap.YlGn)
    ax1.add_text(font_size=12)
    ax1.add_x_labels(labels, rotation=45)
    ax1.add_y_labels(labels)
    ax1.color_diagonal(diag_color=colorMap.YlGn,
                         matrix_color=colorMap.Reds)
    ax1.add_accuracy(invert_PA_UA=False, user_acc_label='Recall',
                       prod_acc_label='Precision')
    ax1.add_f1()
    '''    pltCm = PlotConfusionMatrix(cm, cmap=colorMap.YlGn)

        pltCm.add_text(font_size=12)
        pltCm.add_x_labels(labels, rotation=45)
        pltCm.add_y_labels(labels)
        pltCm.color_diagonal(diag_color=colorMap.YlGn,
                             matrix_color=colorMap.Reds)
        pltCm.add_accuracy(invert_PA_UA=False, user_acc_label='Recall',
                           prod_acc_label='Precision')
        pltCm.add_f1()'''
    if out_filename:
        plt.savefig(out_filename, bbox_inches='tight')

########### --- Ces fonctions proviennent du script classification.py

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

    if (raster.RasterXSize!=roi.RasterXSize) or \
            (raster.RasterYSize!=roi.RasterYSize):
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
            coord = np.where(Y==lab)[0]
            dict_X[lab] = X[coord]
            dict_t[lab] = (t[0][coord], t[1][coord])

        return dict_X, Y, dict_t
    else:
        return X, Y, t,


def report_from_dict_to_df(dict_report):
    '''

    Parameters
    ----------
    dict_report : dict
        DESCRIPTION.

    Returns
    -------
    report_df : dataframe
        DESCRIPTION.

    '''
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

