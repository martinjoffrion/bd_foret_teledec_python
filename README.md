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
### Conventions/noms fichier à vérifier
- [ ] Nom du fichier : pre_traitement.py
- [ ] Fonctions mises dans script my_function.py à part
- [ ] Nom du fichier : masque_foret.tif
- [ ] Nom du fichier : Serie_temp_S2_allbands.tif
- [ ] Nom du fichier : Serie_temp_S2_ndvi.tif 
- [x] Espaces, virgules, ...
- [x] Structure épurée du code

### A mettre dans la notice utilisation 
- [ ] Expliquer ce que doit comprendre le dossier avec les données d'entrée 
- [ ] Préciser qu'il vaut mieux le mettre dans le dossier projet_teledection_sigmaM2_group4
- [ ] Préciser les consignes d'éxécution

### Masque à partir de la BD_FORET
 - [ ] suppression des polygones de type Lande, Formation Herbacée et de type "forêts ouvertes"
> [!WARNING]
>  Manque la suppresion des forets ouverts
 - [ ] format raster GeoTiff ;
 - [ ] encodé en 8 bits ;
 - [ ] même emprise spatiale et résolution spatiale que les images S2 utilisées ;
 - [ ] nom du fichier masque_foret.tif ;
 - [ ] contient les valeurs suivantes : Zone de forêt = valeur du pixel 1 & Zone hors forêt = valeur du pixel 0

### Production d'une image Serie_temp_S2_allbands.tif
 - [ ] contient les 10 bandes : 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, pour les 6 dates (60 bandes) |
 - [ ] découpée selon l'emprise du fichier emprise_etude.shp
 - [ ] avec un résolution spatiale de 10m ;
 - [ ] projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 - [ ] où les zones de non forêt sont masquées (valeur des pixels = 0) grâce au masque masque_foret.tif que vous avez créé ;
 - [ ] encodée en uint16 (ou uint8 cf remarque ci-après).
 - [ ] Vous nommerez l'image finale Serie_temp_S2_allbands.tif.

### Production d'une image NDVI Serie_temp_S2_ndvi.tif
 - [ ] découpée selon l'emprise du fichier emprise_etude.shp ;
 - [ ] avec un résolution spatiale de 10m ;
 - [ ] projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 - [ ] où les zones de non forêt sont masquées (valeur des pixels = 0) grâce au masque masque_foret.tif que vous avez créé ;
 - [ ] encodée en float32 (ou float).
 - [ ] Vous nommerez l'image finale Serie_temp_S2_ndvi.tif

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



