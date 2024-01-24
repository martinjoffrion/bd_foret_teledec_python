# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 13:10:56 2024

@author: clair
"""
################################################
########### CHEMINS D'ACCES A RENSEIGNER #######
################################################

working_directory = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4'
import os
import geopandas as gpd
os.chdir(working_directory)

# --- Mettre le chemin d'accès du dossier OTB-8.1.2/bin :
# Exemple : os.environ['MYOTB'] = 'C:/Users/clair/Documents/OTB-8.1.2-Win64/bin'
#os.environ['MYOTB'] = 'le/chemin/vers/OTB-8.1.2-Win64/bin'
os.environ['MYOTB'] = 'C:/Users/clair/Documents/OTB-8.1.2-Win64/bin'

otb_bin_path = os.environ['MYOTB']
os.environ['MYRAM'] = '8000'
import my_function as f
import pandas as pd

import classification_f as cla
#import read_and_write as rw
from sklearn.ensemble import RandomForestClassifier as RF
import numpy as np
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, GroupKFold, StratifiedGroupKFold
from sklearn.metrics import confusion_matrix, classification_report, \
    accuracy_score
import plots
import matplotlib.pyplot as plt
import time


#Initiate compteur
# get the start time
st = time.time()


# --- Répertoire de travail actuel 
os.chdir(working_directory)

# --- Création d'un nouveau sous-dossier pour y stocker les résultats intermédiaires
os.mkdir(f'{working_directory}/intermediate_result')
# enregistre le chemin complet sous une variable
iwdir = f'{working_directory}/intermediate_result'

################################################
###########         RASTERISATION        #######
################################################

########### --- Rasterisation des échantillons (Sample_BD_foret_T31TCJ.shp)

sample_bdforet = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4/data_set/Sample_BD_foret_T31TCJ.shp'
image_filename = 'C:/Users/clair/Documents/projet_teledection_sigmaM2_group4/traitement/Serie_temp_S2_allbands.tif'

## Etape 1 : rasteriser le Sample_BD_foret_T31TCJ par valeur unique

# Création d'une colonne 'fid' avec des valeurs uniques
sample_bdforet_shp = gpd.read_file (sample_bdforet)
sample_bdforet_shp['fid'] = sample_bdforet_shp.reset_index().index + 1

# Necessité de l'enregistrer pour la fonction OTB (suite) : à enregistrer dans un dossier intermédiaire
sample_bdforet_shp.to_file(f'{iwdir}/Sample_BD_foret_T31TCJ_fid.shp', driver="ESRI Shapefile")

# Champs nécessaires pour la fonction cmd_Rasterization
sample_bdforet_filename = f'{iwdir}/Sample_BD_foret_T31TCJ_fid.shp'
field_name = 'fid' # champ nécessaire à la rasterisation
out_sample_filename = f'{iwdir}/sample_bdforet_id.tif'
# Appel à la fonction
f.cmd_Rasterization(sample_bdforet_filename, out_sample_filename, image_filename, field_name)

## Etape 2 : récupération de l'identifiant unique des polygones (groupes)

sample_bdforet_id = out_sample_filename

# Identifiants des polygones
_, groups, t_groups = cla.get_samples_from_roi(image_filename, out_sample_filename)  

# Dataframe avec tous les groupes
grps_df = pd.DataFrame(groups)
grps_df = grps_df.rename(columns={0: "id_groupe_polyg"})

# Dataframe avec les coordonnées (lignes, colonnes) de tous les groupes
t_grps_df = pd.DataFrame({'Coord_lignes':t_groups[0],'Coord_col':t_groups[1]})
all_groups = pd.concat([grps_df, t_grps_df], axis=1)


################################################
###########         CLASSIFICATION       #######
################################################

# Création d'une boucle sur les 3 niveaux de nomenclature
list_cm_3niv = []
list_accuracy_3niv = []
list_report_3niv = []

for niv in range(1,4) : # répétition de la boucle 3 fois

########### --- Rasterisation du fichier Sample_BD_foret_T31TCJ par classe 
    # Création du raster en sortie (s'adapte selon le niveau de nomenclature)
    sample_filename_niv = os.path.join(iwdir,'samples_model_lvl{}.tif'.format(niv))
    
    # Le champ nécessaire à la rasterisation (correspond au niveau 1, 2 puis 3)
    field_name = 'Code_lvl{}'.format(niv)  
    
    # Appel à la fonction
    f.cmd_Rasterization(sample_bdforet_filename=sample_bdforet_filename, out_sample_filename=sample_filename_niv, image_filename=image_filename, field_name=field_name)
    
    ## Extraction des échantillons :
    X, Y, t = cla.get_samples_from_roi(image_filename, sample_filename_niv)
    
    ## Création d'un dataframe avec les coordonnées de l'image
    t_df = pd.DataFrame({'Coord_lignes':t[0],'Coord_col':t[1]})

    # Jointure entre les coordonnées (t) de l'image et celles du df 'all_groups' pour ne garder que celles correspondantes
    grps_niv = t_df.merge(all_groups, how="left", on=["Coord_lignes", "Coord_col"])
    
    # Transformation en array pour la suite (StratifiedGroupKFold)
    grps_niv = grps_niv["id_groupe_polyg"].to_numpy()
    
    ## Paramètres pour la StratifiedGroupKFold
    nb_iter = 1 # pour la vf, mettre 30 itérations
    nb_folds = 5
    
    list_cm = []
    list_accuracy = []
    list_report = []
    
########### --- StratifiedGroupKFold

    kf = StratifiedGroupKFold(n_splits=nb_folds, shuffle=True)
    for train, test in kf.split(X, Y, groups=grps_niv):
        X_train, X_test = X[train], X[test]
        Y_train, Y_test = Y[train], Y[test]

        # Etape 1 : Train
        model = RF(max_depth=10, oob_score=True, max_samples=0.75, class_weight="balanced", n_jobs=-1)
        model.fit(X_train, Y_train)
    
        # Etape 2 : Test
        Y_predict = model.predict(X_test)
    
        # Etape 3 : compute quality
        list_cm.append(confusion_matrix(Y_test, Y_predict))
        list_accuracy.append(accuracy_score(Y_test, Y_predict))
        report = classification_report(Y_test, Y_predict,
                               labels=np.unique(Y_predict),
                               output_dict=True)
    
        # Etape 4 : store them
        list_report.append(plots.report_from_dict_to_df(report))

#compteur 
et = time.time()
elapsed_time = et - st
print('Execution time :', elapsed_time, 'seconds')    
    
###########################################################
#A INSERER DANS LA BOUCLE ET A ADAPTER AU CODE

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

# Display confusion matrix
plots.plot_cm(mean_cm, np.unique(Y_predict))
plt.savefig(out_matrix, bbox_inches='tight')

# Display class metrics
fig, ax = plt.subplots(figsize=(10, 7))
ax = mean_df_report.T.plot.bar(ax=ax, yerr=std_df_report.T, zorder=2)
ax.set_ylim(0.5, 1)
_ = ax.text(1.5, 0.95, 'OA : {:.2f} +- {:.2f}'.format(mean_accuracy,
                                                      std_accuracy),
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


