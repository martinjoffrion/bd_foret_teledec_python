## Verification : pre_traitement.py
### Conventions à vérifier
- [ ] Nom du fichier : pre_traitement.py
- [ ] Fonctions mises dans script my_function.py à part
- [ ] Nom du fichier : masque_foret.tif
- [ ] Nom du fichier : Serie_temp_S2_allbands.tif
- [ ] Nom du fichier : Serie_temp_S2_ndvi.tif 

### Conventions à vérifier
- [x] Espaces, virgules, ...
- [x] Structure épurée du code

### A mettre dans la notice utilisation 
- [ ] Expliquer ce que doit comprendre le dossier avec les données d'entrée 
- [ ] Préciser qu'il vaut mieux le mettre dans le dossier projet_teledection_sigmaM2_group4
- [ ] Préciser les consignes d'éxécution

### Masque à partir de la BD_FORET
 - [ ] suppression des polygones de type Lande, Formation Herbacée et de type "forêts ouvertes"
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

