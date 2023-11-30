# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 09:41:17 2023

@author: dsii
"""
import os
import rasterio
#testcommentaire
otb_bin_path = os.environ['MYOTB']
##fonction


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

    
    
    
    
    
    
    
