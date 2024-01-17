# Lien téléchargement

Les deux images finales du script pre_traitement.py : https://filesender.renater.fr/?s=download&token=60796c71-1347-45f6-84ce-a213a76152f9

# Verification

## Questions pour le prof : 

- pour le masque_foret.tif, il doit apparaitre déjà créé dans le dossier final ?
- envoyer les images dézippées dans le dossier final ?

## Images
 
 - [x] des images acquises entre janvier 2021 et février 2022 ;
 - [x] des images de la tuile T31TCJ 
 - [x] des images qui ont une couverture de nuages inférieure à 15%
 - [ ] des images en réflectance (niveau 2A)
 - [x] une date en hiver ;
> [!NOTE]  
> 25 janvier 2022
 - [x] quatre dates en automne/printemps, idéalement deux pour chaque saison ;
> [!NOTE]  
>  31 mars 2021, 15 avril 2021, 16 décembre 2021 et 17 octobre 2021 (couverture à 17% --> OK), 
 - [x] une date en été
> [!NOTE]  
> 19 juillet 2021

## pre_traitement.py
Fonctionne en 1h38
### Conventions/noms fichier à vérifier
- [x] Nom du fichier : pre_traitement.py
- [x] Fonctions mises dans script my_function.py à part
- [x] Nom du fichier : masque_foret.tif
- [x] Nom du fichier : Serie_temp_S2_allbands.tif
- [x] Nom du fichier : Serie_temp_S2_ndvi.tif 
- [x] Espaces, virgules, ...
- [x] Structure épurée du code
- [x] suppression de bouts de code résiduels
- [x] execution d'un seul tenant

### A mettre dans la notice utilisation 
- [ ] Expliquer ce que doit comprendre le dossier avec les données d'entrée 
- [ ] Préciser qu'il vaut mieux le mettre dans le dossier projet_teledection_sigmaM2_group4
- [ ] Préciser les consignes d'éxécution

### Masque à partir de la BD_FORET
 - [x] suppression des polygones de type Lande, Formation Herbacée et de type "forêts ouvertes"
 - [x] format raster GeoTiff ;
 - [x] encodé en 8 bits ;
>  Octet - nombre entier non signé de huit bits
 - [x] même emprise spatiale et résolution spatiale que les images S2 utilisées ;
> Globalement, les mêmes

| Fichier | Emprise |
| --- | --- |
| masque_foret | 501127.9697000000160187,6240654.0235999999567866 : 609757.9697000000160187,6314464.0235999999567866 |
| Serie_temp_S2_allbands | 501006.0829747776733711,6240658.9746725969016552 : 609757.6257253842195496,6313703.5941410586237907 |
| Serie_temp_S2_ndvi | 501006.0829747776733711,6240658.9746725969016552 : 609757.6257253842195496,6313703.5941410586237907 |

| Fichier | Résolution spatiale |
| --- | --- |
| masque_foret | 10,-10 |
| Serie_temp_S2_allbands | 10.00474174338606481,-10.00474174338606481 |
| Serie_temp_S2_ndvi | 10.00474174338606481,-10.00474174338606481|
 - [x] nom du fichier masque_foret.tif ;
 - [x] contient les valeurs suivantes : Zone de forêt = valeur du pixel 1 & Zone hors forêt = valeur du pixel 0

### Production d'une image Serie_temp_S2_allbands.tif
 - [x] contient les 10 bandes : 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, pour les 6 dates (60 bandes) |
 - [x] découpée selon l'emprise du fichier emprise_etude.shp
> OK dans le script et QGIS   
 - [x] avec un résolution spatiale de 10m ;
 - [x] projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 - [x] où les zones de non forêt sont masquées (valeur des pixels = 0) ~~grâce au masque masque_foret.tif que vous avez créé~~ ;
> OK dans QGIS  : interprétation directe comme "sans donnée" --> Bien indiqué comme 'Aucune valeur de données : 0' dans Propriétés de la couche

> pas avec le masque_foret.tif --> prof OK
 - [x] encodée en uint16 ~~(ou uint8 cf remarque ci-après).~~
 - [x] Vous nommerez l'image finale Serie_temp_S2_allbands.tif.

### Production d'une image NDVI Serie_temp_S2_ndvi.tif
 - [x] découpée selon l'emprise du fichier emprise_etude.shp ;
> OK dans le script et OK sur QGIS  
 - [x] avec un résolution spatiale de 10m ;
 - [x] projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 - [x] où les zones de non forêt sont masquées (valeur des pixels = 0) ~~grâce au masque masque_foret.tif que vous avez créé~~ ;
> OK dans QGIS  : interprétation directe comme "sans donnée" --> Bien indiqué comme 'Aucune valeur de données : 0' dans Propriétés de la couche

> pas avec le masque_foret.tif --> prof OK
 - [x] encodée en float32 (ou float).
 - [x] Vous nommerez l'image finale Serie_temp_S2_ndvi.tif

## Sample_BD_foret_T31TCJ.shp

 - [ ] les échantillons doivent être inclus dans l'emprise des images S2 que vous allez utiliser (après découpe Cf section Pré-traitement des images);
 - [x] utilisez uniquement les classes présentes dans la nomenclature du prof
> utilisation de la nomenclature envoyé par Louis-Marie
 - [x] certaines classes TFV ne sont pas à prendre en compte pour tous les niveaux. Par exemple, les polygones de la classe Forêt fermée de feuillus purs en îlots ne sont pas à prendre en compte pour le niveau 3 (symbole Ø) mais bien à prendre en compte pour les niveaux 2 et 1 ;
 - [x] si une classe contient moins de 15 polygones, alors ne la prenez pas en compte.
> [!WARNING]
> En découpant avec l'emprise vectorielle, on tombe sur 10729 comme les autres groupes --> MAIS problème pour les diagrammes, ce n'est pas la même emprise entre le masque foret et le shp des échantillons

> [!WARNING]
> En découpant avec le masque foret, on tombe sur 10749 --> script diagramme opérationnel
- Comprend les champs : 
  - [ ] Nom_lvl3 ;
  - [ ] Code_lvl3 ;
  - [ ] Nom_lvl2 ;
  - [ ] Code_lvl2 ;
  - [ ] Nom_lvl1 ;
  - [ ] Code_lvl1.
- Laissez également les attributs déjà présents.
  - [ ] ID
  - [ ] CODE_TFV
  - [ ] TFV
  - [ ] TFV_G11
  - [ ] ESSENCE
- [ ]Nommez le fichier Sample_BD_foret_T31TCJ.shp (si vous utilisez le format shapefile).
> prof : je regarderai juste le fichier final en contrôlant que tous les attributs soient présents (et corrects) et qu'il y ait le bon nombres de polygones.

## sample_analysis.py
 - [ ] diag_baton_nb_poly_lvlXX (png ou html) ; x3 (par niveau de nomenclature)
 - [ ] diag_baton_nb_pix_lvlXX (png ou html) ; x3 (par niveau de nomenclature)
 - [ ] temp_mean_ndvi_lvlXX (png ou html) ; x3 (par niveau de nomenclature)

### Conventions/noms fichier à vérifier
- [ ] Nom du fichier : sample_analysis.py
- [ ] Fonctions mises dans script my_function.py à part
- [ ] Espaces, virgules, ...
- [ ] Structure épurée du code
- [ ] suppression de bouts de code résiduels
- [ ] execution d'un seul tenant

## classification.py
 - [ ]  faire une classification supervisée avec le classifieur 'RandomForestClassifier' de scikit learn en utilisant les hyperparamètres :

| Paramètre | Valeur |
| --- | --- |
| max_depth | 20* |
| oob_score | True |
| max_samples | 0.75 |
| class_weight | balanced |
| N_estimators | 	Valeur par défaut** |

> Utilisez la valeur par défaut pour les hyperparamètres qui ne figurent pas dans le tableau. Si la classification prend trop de temps passez à (*) 10, à (**) 50 voire 10.
Stratégie de validation.

### validation croisée à 5 folds qui est soit :
 - [ ]  stratifiée (projet évalué sur 16) ;
 - [ ]   stratifiée et qui prend en compte l'appartenance des pixels à un polygone (projet évalué sur 18) ;
 - [ ]  stratifiée et qui prend en compte l'appartenance des pixels à un polygone, répétée 30 fois avec résultats moyennées (projet évalué sur 20).

### production d'images
 - [ ]  carte_essences_lvl1.tif ;
 - [ ]  carte_essences_lvl2.tif ;
 - [ ]  carte_essences_lvl3.tif ;
 - [ ]  carte_essences_lvl2_fromlvl3.tif ;
 - [ ]  carte_essences_lvl1_fromlvl2.tif ;
 - [ ] carte_essences_lvl1_fromlvl3.tif

## my_function.py
 - [ ]   ajout des commentaires "" ""
 - [ ]   suppression des commentaires en #
 - [ ]   



# Fichiers à rendre

Fichier attendus :

 - [ ]     Masque forêt : masque_foret.tif
 - [ ]     fichier d'échantillons : Sample_BD_foret_T31TCJ.shp.
-  script Python :
 - [ ]         sample_analysis.py
 - [ ]         pre_traitement.py
 - [ ]         classification.py
 - [ ]         my_function.py
 - [ ]     le rapport final : projet_teledection_sigmaM2_groupXX (pdf ou html)
 - [ ]     l'ensemble de ces fichiers devra être rassemblé dans une archive zip nommée projet_teledection_sigmaM2_groupXX.zip.

Fichier non attendus mais que produirai grace à votre code :

- Analyse des échantillons :
 - [ ]         diag_baton_nb_poly_lvlXX (png ou html) ;
 - [ ]         diag_baton_nb_pix_lvlXX (png ou html) ;
 - [ ]         temp_mean_ndvi_lvlXX (png ou html) ;
- Série temporelles :
 - [ ]         Serie_temp_S2_allbands.tif ;
 - [ ]         Serie_temp_S2_ndvi.tif ;
- carte_essences :
 - [ ]         carte_essences_lvl1.tif ;
 - [ ]         carte_essences_lvl2.tif ;
 - [ ]         carte_essences_lvl3.tif ;
 - [ ]         carte_essences_lvl2_fromlvl3.tif ;
 - [ ]         carte_essences_lvl1_fromlvl2.tif ;
 - [ ]        carte_essences_lvl1_fromlvl3.tif.



