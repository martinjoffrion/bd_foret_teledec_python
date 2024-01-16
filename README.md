## Verification
<details>
<summary>SCRIPT : pre_traitement.py</summary

| Etat     | VERIFICATION                                      |
|---------:|---------------------------------------------------|
|A vérifier| Nom du fichier : pre_traitement.py                |
|A vérifier| Fonctions mises dans script my_function.py à part.|
|A vérifier| masque_foret.tif                                  |
|A vérifier| Nom du fichier : Serie_temp_S2_allbands.tif       |
|A vérifier| Nom du fichier : Serie_temp_S2_ndvi.tif           |


> Conventions 
 | - Espaces
 | - Structure épurée du code

> Notice utilisation 
 | - Mettre le chemin sur le dossier projet_teledection_sigmaM2_group4
 | - Expliquer ce que doit comprendre le dossier avec les données d'entrée 
 | - Préciser qu'il vaut mieux le mettre dans le dossier projet_teledection_sigmaM2_group4
 | - Consignes éxécution :

> Masque à partir de la BD_FORET
 Manque les forets ouverts | - suppression des polygones de type Lande, Formation Herbacée et de type "forêts ouvertes"
 | - format raster GeoTiff ;
 | - encodé en 8 bits ;
 | - même emprise spatiale et résolution spatiale que les images S2 utilisées (après découpe Cf section Pré-traitement des images);
 | - nom du fichier masque_foret.tif ;
 | - contient les valeurs suivantes : Zone de forêt = valeur du pixel 1 & Zone hors forêt = valeur du pixel 0


> Production d'une image Serie_temp_S2_allbands.tif
 | - contient les 10 bandes : 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, pour les 6 dates (60 bandes) |
 | - découpée selon l'emprise du fichier emprise_etude.shp
 | - avec un résolution spatiale de 10m ;
 | - projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 | - où les zones de non forêt sont masquées (valeur des pixels = 0) grâce au masque masque_foret.tif que vous avez créé ;
 | - encodée en uint16 (ou uint8 cf remarque ci-après).
 | - Vous nommerez l'image finale Serie_temp_S2_allbands.tif.

> Production d'une image NDVI Serie_temp_S2_ndvi.tif
 | - découpée selon l'emprise du fichier emprise_etude.shp ;
 | - avec un résolution spatiale de 10m ;
 | - projetée selon le système de projection Lambert 93 (EPSG:2154) ;
 | - où les zones de non forêt sont masquées (valeur des pixels = 0) grâce au masque masque_foret.tif que vous avez créé ;
 | - encodée en float32 (ou float).
 | - Vous nommerez l'image finale Serie_temp_S2_ndvi.tif

