# ROADMAP

## Projet : Imitation des mouvements de pince par un robot industriel

### Contexte
Le projet consiste à permettre à un robot industriel Niryo à 6 axes de reproduire les mouvements réalisés par une pince équipée d'une GoPro Hero 10 Black. La pince est utilisée par un opérateur humain, et ses mouvements sont capturés en vidéo ainsi que via des données d'accéléromètre et de gyroscope au format GPMF.

### Objectifs
1. Enregistrer les mouvements d'une pince en vidéo.
2. Extraire les données d'accélérométrie et de gyroscopie (format GPMF).
3. Traiter et analyser ces données pour les convertir en commandes robotiques.
4. Programmer un robot Niryo pour reproduire les mouvements enregistrés.

---

## Étapes du projet

### 1. **Enregistrement des mouvements**
- **Outil** : Open GoPro Python SDK.
- **Tâches** :
  - Contrôler la GoPro via Wi-Fi (démarrer et arrêter l'enregistrement).
  - Configurer les paramètres d'enregistrement : résolution, fréquence d'image, etc.
  - Capturer des vidéos des mouvements de la pince.

Exemple de code :
```python
from goprocam import GoProCamera
gopro = GoProCamera.GoPro()
gopro.shoot_video(duration=10)  # Enregistre une vidéo de 10 secondes
```

---

### 2. **Extraction des données GPMF**
- **Outil** : py-gpmf-parser.
- **Tâches** :
  - Charger une vidéo et extraire les données GPMF.
  - Identifier les champs pertinents :
    - `ACCL` pour les données d'accélération.
    - `GYRO` pour les données gyroscopiques.
  - Convertir les données extraites en un format exploitable (tableaux, fichiers CSV, etc.).

Exemple de code :
```python
from gpmf_parser import Parser

with open("video.mp4", "rb") as f:
    parser = Parser(f.read())
    data = parser.parse()
    accel_data = data.get('ACCL')  # Récupère les données d'accélération
    gyro_data = data.get('GYRO')  # Récupère les données gyroscopiques
```

---

### 3. **Traitement et analyse des données**
- **Outils** : `numpy`, `pandas`.
- **Tâches** :
  - Synchroniser les données avec les images vidéo.
  - Détecter les ouvertures et fermetures de la pince à partir des données ou des images.
  - Identifier les mouvements significatifs pour les convertir en commandes robotiques.

Exemple de traitement :
```python
import pandas as pd

accel_df = pd.DataFrame(accel_data, columns=["time", "x", "y", "z"])
gyro_df = pd.DataFrame(gyro_data, columns=["time", "roll", "pitch", "yaw"])

# Calcul de la magnitude des accélérations
accel_df['magnitude'] = (accel_df['x']**2 + accel_df['y']**2 + accel_df['z']**2)**0.5
peaks = accel_df[accel_df['magnitude'] > seuil]  # Identifier des mouvements importants
```

---

### 4. **Programmation du robot Niryo**
- **Outil** : PyNiryo v1.1.2.
- **Tâches** :
  - Connecter le robot Niryo via son adresse IP.
  - Envoyer des commandes pour effectuer les mouvements détectés.
  - Tester et calibrer le robot pour garantir la précision des reproductions.

Exemple de commande :
```python
from pyniryo import NiryoRobot

robot = NiryoRobot("192.168.x.x")  # Adresse IP du robot
robot.calibrate_auto()

# Exemple de mouvement
robot.move_joints([0.5, -0.3, 0.1, 0.2, -0.1, 0.0])
robot.close_gripper()  # Fermer la pince
robot.open_gripper()   # Ouvrir la pince

robot.close_connection()
```

---

## Bibliothèques utilisées
- **Open GoPro Python SDK** : Contrôle de la caméra GoPro Hero 10 Black.
- **py-gpmf-parser** : Extraction des données GPMF.
- **PyNiryo v1.1.2** : Contrôle du robot Niryo.
- **numpy**, **pandas** : Analyse et traitement des données.
- **opencv** *(optionnel)* : Traitement des images vidéo pour détecter visuellement l’état de la pince.

---

## Points critiques
1. **Synchronisation des données** : Veiller à aligner les timestamps des données GPMF avec ceux de la vidéo.
2. **Calibrations initiales** : Vérifier la calibration du robot et de la GoPro avant chaque utilisation.
3. **Tests par étapes** : Valider chaque partie du pipeline (GoPro, extraction GPMF, analyse, robot Niryo) avant l'intégration finale.

---

## Ressources et liens utiles
- **Open GoPro SDK** : [Lien GitHub](https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control)
- **py-gpmf-parser** : [Lien GitHub](https://github.com/urbste/py-gpmf-parser)
- **PyNiryo** : [Documentation PyNiryo](https://pyniryo.readthedocs.io)

---

## Chronologie suggérée
1. **Semaine 1-2** : Mise en place des outils et tests unitaires (GoPro, extraction GPMF, connexion Niryo).
2. **Semaine 3-4** : Extraction et traitement des données, synchronisation des résultats.
3. **Semaine 5-6** : Programmation et tests des mouvements avec le robot Niryo.
4. **Semaine 7** : Ajustements finaux et démonstration.

---

### Bonne chance pour votre projet ! 🚀
