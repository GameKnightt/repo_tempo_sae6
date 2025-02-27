# Projet Imitation de Mouvement via GoPro pour Robot Niryo Ned 2

Ce projet permet de capturer, analyser et reproduire des mouvements filmés par une GoPro sur un robot Niryo Ned 2. Il s’inscrit dans le cadre du BUT GEII à l’IUT de Nantes.

## Fonctionnalités Principales
- **Extraction IMU** : Récupération des données de gyroscope et d’accéléromètre depuis la GoPro.  
- **Analyse et Réorganisation** : Traitement des données pour un usage ultérieur (recalage temporel, format JSON).  
- **Adaptation pour Niryo** : Conversion des données en commandes adaptées au robot Niryo Ned 2.  

## Structure du Projet
- `GPMF_Parser/main.py`  
  - Lance l’analyse des vidéos GoPro (fichiers uniques ou répertoires).  
  - Extrait les données IMU et prépare les fichiers pour le robot.  
- `adapt_json_niryo.py`  
  - Convertit les informations de gyroscope et d’accéléromètre en mouvements exploitables par le robot (Roll, Pitch, Yaw, etc.).  
- `3-Json-adapt-niryo-movement`  
  - Contient les fichiers JSON finaux prêts à être envoyés au Niryo Ned 2.  

## Installation et Utilisation
1. **Installer les dépendances** :  
   - Python 3.10.7  
   - Modules listés dans la documentation du projet.  
2. **Exécuter le script principal** :  
   - `python main.py [chemin_vers_vidéo_ou_dossier]`  
3. **Examiner les sorties** :  
   - Les données traitées se trouvent dans les dossiers créés pour chaque étape.  

## Contribution
Les contributions sont les bienvenues pour améliorer les fonctions de parsing, d’analyse et de commande robotique.

## Auteurs
- Alexy LESAULNIER  
- Kylian MOURGUES  

## Licence
Projet académique à but d’apprentissage. Réutilisation possible à des fins éducatives.
