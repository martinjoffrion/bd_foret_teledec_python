# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 13:10:56 2024

@author: clair & & 
"""
################################################
########### CHEMINS D'ACCES A RENSEIGNER #######
################################################


import os
os.environ['MYOTB'] = 'C:/OTB-8.1.2-Win64/bin' #path to the OTB bin folder
os.environ['MYRAM'] = '8000'
import geopandas as gpd
import my_function as f #Add to Python path manager
import pandas as pd

from sklearn.ensemble import RandomForestClassifier as RF
import numpy as np
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, GroupKFold, StratifiedGroupKFold
from sklearn.metrics import confusion_matrix, classification_report, \
    accuracy_score
#import plots
import matplotlib.pyplot as plt
import time


working_directory = 'C:/Users/dsii/Downloads/bd_foret_teledec_python-main'



#Initiate compteur
# get the start time
st = time.time()


# --- Répertoire de travail actuel 
os.chdir(working_directory)

# --- Création d'un nouveau sous-dossier pour y stocker les résultats intermédiaires
os.mkdir(f'{working_directory}/intermediate_result_4b')
# os.mkdir(os.path.join(working_directory,'intermediate_result_4b')
# enregistre le chemin complet sous une variable
iwdir = f'{working_directory}/intermediate_result_4b'
#iwdir = os.path.join(working_directory,'intermediate_result_4b'

################################################
###########         RASTERISATION        #######
################################################

########### --- Rasterisation des échantillons (Sample_BD_foret_T31TCJ.shp)

sample_bdforet = 'data/sample_div/Sample_BD_foret_T31TCJ_div2.shp'

image_filename = 'data/Serie_temp_S2_4bands.tif'

## Etape 1 : rasteriser le Sample_BD_foret_T31TCJ par valeur unique

# Création d'une colonne 'fid' avec des valeurs uniques
sample_bdforet_shp = gpd.read_file (sample_bdforet)
sample_bdforet_shp['fid'] = sample_bdforet_shp.reset_index().index + 1

# Necessité de l'enregistrer pour la fonction OTB (suite) : à enregistrer dans un dossier intermédiaire
sample_bdforet_shp.to_file(f'{iwdir}/Sample_BD_foret_T31TCJ_fid.shp',
                           driver="ESRI Shapefile")
#sample_bdforet_filename = os.path.join(iwdir,'Sample_BD_foret_T31TCJ_fid.shp')
#sample_bdforet_shp.to_file(sample_bdforet_filename,


nomencalture = ['Code_lvl1','Code_lvl2','Code_lvl3']
for i in nomencalture :
    print(f'for {i} nbr of NA is {sample_bdforet_shp[i].isna().sum()}')
    # sample_bdforet_shp[i]= sample_bdforet_shp[i].astype(int)


# Champs nécessaires pour la fonction cmd_Rasterization
sample_bdforet_filename = f'{iwdir}/Sample_BD_foret_T31TCJ_fid.shp'#def plus haut

field_name = 'fid' # champ nécessaire à la rasterisation

out_sample_filename = f'{iwdir}/sample_bdforet_id.tif'
#out_sample_filename = os.path.join(iwdir,'sample_bdforet_id.tif')

# Appel à la fonction
f.cmd_Rasterization(sample_bdforet_filename, out_sample_filename,
                    image_filename, field_name)

## Etape 2 : récupération de l'identifiant unique des polygones (groupes)

sample_bdforet_id = out_sample_filename

# Identifiants des polygones
_, groups, t_groups = f.get_samples_from_roi(image_filename, out_sample_filename)


# Dataframe avec tous les groupes
grps_df = pd.DataFrame({'id_groupe_polyg':groups.reshape(-1),
                        'Coord_lignes':t_groups[0],
                        'Coord_col':t_groups[1]})

et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
################################################
###########         CLASSIFICATION       #######
################################################

# Création d'une boucle sur les 3 niveaux de nomenclature

nomencalture = ['Code_lvl1','Code_lvl2','Code_lvl3']

list_metrics_lvl1 = []
list_metrics_lvl2 = []
list_metrics_lvl3 = []
list_metrics_lvl1_fromlvl3 = []
list_metrics_lvl2_fromlvl3 = []
list_metrics_lvl1_fromlvl2 = []


for niv in range(len(nomencalture)) : 

########### --- Rasterisation du fichier Sample_BD_foret_T31TCJ par classe 

    # Le champ nécessaire à la rasterisation (correspond au niveau 1, 2 puis 3)
    field_name = nomencalture[niv]  
    
    # Création du raster en sortie (s'adapte selon le niveau de nomenclature)
    sample_filename_niv = f'samples_{field_name}.tif'
    
    # Appel à la fonction
    f.cmd_Rasterization(sample_bdforet_filename, sample_filename_niv,
                        image_filename, field_name)
    
    ## Extraction des échantillons :
    X, Y, t = f.get_samples_from_roi(image_filename, sample_filename_niv)
    ## Correct Y shape
    Y = Y.reshape(-1)
    
    ## Création d'un dataframe avec les coordonnées de l'image
    t_df = pd.DataFrame({'Coord_lignes':t[0],'Coord_col':t[1]})

    # Jointure entre les coordonnées (t) de l'image et celles du df 'all_groups' pour ne garder que celles correspondantes
    grps_niv = t_df.merge(grps_df, how="left", on=["Coord_lignes", "Coord_col"])
    
    # Transformation en array pour la suite (StratifiedGroupKFold)
    grps_niv = grps_niv["id_groupe_polyg"].to_numpy()
    
    ## Paramètres pour la StratifiedGroupKFold
    nb_iter = 3 # pour la vf, mettre 30 itérations
    nb_folds = 5
    
    list_cm = []
    list_accuracy = []
    list_report = []
    
    list_cm_lvl2 = []
    list_accuracy_lvl2 = []
    list_report_lvl2 = []
    
    list_cm_lvl1 = []
    list_accuracy_lvl1 = []
    list_report_lvl1 = []
    
    et = time.time()
    elapsed_time = et - st
    print(f'Execution {field_name} time:', elapsed_time, 'seconds')
    
    # Iter on stratified K fold
    for _ in range(nb_iter):
      et = time.time()
      elapsed_time = et - st
      print('Execution time:', elapsed_time, 'seconds')
      print(f'begining {field_name} {nb_iter} iterations k fold')
      kf = StratifiedGroupKFold(n_splits=nb_folds, shuffle=True)
      for train, test in kf.split(X, Y, groups=grps_niv):
          X_train, X_test = X[train], X[test]
          Y_train, Y_test = Y[train], Y[test]
          
          print('k fold')
          
          # 3 --- Train
          #clf = SVC(cache_size=6000)
          clf = RF(max_depth = 20, 
                    oob_score = True,
                    max_samples = .75,
                    class_weight = 'balanced',
                    n_jobs = -1)
          
          clf.fit(X_train, Y_train)

          # 4 --- Test
          Y_predict = clf.predict(X_test)
          
          if field_name == nomencalture[2] :
              #level 2
              Y_predict_lvl2 = np.floor(Y_predict/10)

              Y_test_lvl2 = np.floor(Y_test/10)
              # compute quality
              list_cm_lvl2.append(confusion_matrix(Y_test_lvl2, Y_predict_lvl2))
              list_accuracy_lvl2.append(accuracy_score(Y_test_lvl2, Y_predict_lvl2))
              report_lvl2 = classification_report(Y_test_lvl2, Y_predict_lvl2,
                                             labels=np.unique(Y_predict_lvl2),
                                             output_dict=True)
              list_report_lvl2.append(f.report_from_dict_to_df(report_lvl2))
              
              #level 1
              Y_predict_lvl1 = np.floor(Y_predict/100)
              Y_test_lvl1 = np.floor(Y_test/100)
              # compute quality
              list_cm_lvl1.append(confusion_matrix(Y_test_lvl1, Y_predict_lvl1))
              list_accuracy_lvl1.append(accuracy_score(Y_test_lvl1, Y_predict_lvl1))
              report_lvl1 = classification_report(Y_test_lvl1, Y_predict_lvl1,
                                             labels=np.unique(Y_predict_lvl1),
                                             output_dict=True)
              list_report_lvl1.append(f.report_from_dict_to_df(report_lvl1))

          if field_name == nomencalture[1] :
              #level 1
              Y_predict_lvl1 = np.floor(Y_predict/10)
              Y_test_lvl1 = np.floor(Y_test/10)
              # compute quality
              list_cm_lvl1.append(confusion_matrix(Y_test_lvl1, Y_predict_lvl1))
              list_accuracy_lvl1.append(accuracy_score(Y_test_lvl1, Y_predict_lvl1))
              report_lvl1 = classification_report(Y_test_lvl1, Y_predict_lvl1,
                                             labels=np.unique(Y_predict_lvl1),
                                             output_dict=True)
              list_report_lvl1.append(f.report_from_dict_to_df(report_lvl1))
              

          # compute quality
          list_cm.append(confusion_matrix(Y_test, Y_predict))
          list_accuracy.append(accuracy_score(Y_test, Y_predict))
          report = classification_report(Y_test, Y_predict,
                                         labels=np.unique(Y_predict),
                                         output_dict=True)
          # store them        
          list_report.append(f.report_from_dict_to_df(report))

    
    ##Agregate métrics 
    
    #store in gdf
    if field_name == nomencalture[2]:
        list_metrics_lvl3.extend(f.agg_metrics(list_cm ,
                                                  list_accuracy,
                                                  list_report))
        
        list_metrics_lvl1_fromlvl3.extend(f.agg_metrics(list_cm_lvl1 ,
                                                  list_accuracy_lvl1,
                                                  list_report_lvl1))
        
        list_metrics_lvl2_fromlvl3.extend(f.agg_metrics(list_cm_lvl2 ,
                                                  list_accuracy_lvl2,
                                                  list_report_lvl2))
    elif field_name == nomencalture[1]:
        
        list_metrics_lvl2.extend(f.agg_metrics(list_cm ,
                                                  list_accuracy,
                                                  list_report))
        
        list_metrics_lvl1_fromlvl2.extend(f.agg_metrics(list_cm_lvl1 ,
                                                  list_accuracy_lvl1,
                                                  list_report_lvl1))

    elif field_name == nomencalture[0] :
        
        list_metrics_lvl1.extend(f.agg_metrics(list_cm ,
                                                  list_accuracy,
                                                  list_report))

        
    #Display Metrics by class


    if field_name == nomencalture[0]:
        f.display_metrics(list_metrics_lvl1, 
                        'Cm_Code_lvl1', 
                        'Cl_Code_lvl1')
        plt.pause(10)

    if field_name == nomencalture[1]:
        f.display_metrics(list_metrics_lvl1_fromlvl2,
                        'Cm_Code_lvl1_fromlvl2', 
                        'Cl_Code_lvl1_fromlvl2')
        plt.pause(10)
        f.display_metrics(list_metrics_lvl2,
                        'Cm_Code_lvl2', 
                        'Cl_Code_lvl2')
        plt.pause(10)

    if field_name == nomencalture[2]:
        f.display_metrics(list_metrics_lvl1_fromlvl3,
                        'Cm_Code_lvl1_fromlvl3', 
                        'Cl_Code_lvl1_fromlvl3')
        plt.pause(20)
        f.display_metrics(list_metrics_lvl2_fromlvl3,
                        'Cm_Code_lvl2_fromlvl3', 
                        'Cl_Code_lvl2_fromlvl3')
        plt.pause(20)
        list_metrics_lvl3[0] = list_metrics_lvl3[0].astype(int)
        f.display_metrics(list_metrics_lvl3,
                        'Cm_Code_lvl3', 
                        'Cl_Code_lvl3')

    

    # Classification

    clf.fit(X, Y)

    X_img, Y_img , t_img = f.get_samples_from_roi(image_filename,image_filename)

    Y_predict_img = clf.predict(X_img)
    
    #writting image
    
    image_output = f'carte_essences_{field_name}.tif'
    image = f.open_image(image_filename)
    nb_row, nb_col, _ = f.get_image_dimension(image)
    #initialization of the array
    img = np.zeros((nb_row, nb_col, 1), dtype='uint8')
    
    #np.Y_predict
    img[t_img[0], t_img[1], 0] = Y_predict_img
    
    f.write_image(image_output,img, data_set=image)
    
    if field_name == nomencalture[2] :
        #level 2
        Y_predict_img_lvl2 = np.floor(Y_predict_img/10)
        image_outputlvl2 = f'carte_essences__lvl2_from{field_name}.tif'
        img = np.floor(img/10)
        f.write_image(image_outputlvl2,img, data_set=image)
        
        #level 1
        Y_predict_img_lvl1 = np.floor(Y_predict_img/100)
        image_outputlvl1 = f'carte_essences__lvl1_from{field_name}.tif'
        img = np.floor(img/100)
        f.write_image(image_outputlvl1,img, data_set=image)
        
        et = time.time()
        elapsed_time = et - st
        print('Execution almost Achieved in :', elapsed_time, 'seconds')
        
    elif field_name == nomencalture[1] :
        #level 1
        Y_predict_img_lvl1 = np.floor(Y_predict_img/100)
        image_outputlvl1 = f'carte_essences__lvl1_from{field_name}.tif'
        img = np.floor(img/100)
        f.write_image(image_outputlvl1 ,img, data_set=image)


list_label = ['mean_cm' , 'mean_accuracy' , 'std_accuracy' ,
              'mean_df_report' , 'std_df_report']

Metrics_summerize = pd.DataFrame({
                                'metrics':list_label,
                                'lvl1':list_metrics_lvl1,
                                'lvl2':list_metrics_lvl2,
                                'lvl3':list_metrics_lvl3,
                                #'lvl1_fromlvl3':list_metrics_lvl1_fromlvl3,
                                'lvl2_fromlvl3':list_metrics_lvl2_fromlvl3,
                                'lvl1_fromlvl2':list_metrics_lvl1_fromlvl2,
                                })
Metrics_summerize.to_csv('Metrics_summerize.csv')












