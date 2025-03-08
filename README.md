# Projet d'Imitation de Mouvements GoPro-Niryo

![Image](https://github.com/user-attachments/assets/29b6818c-3232-4d05-ae3f-b47af2946025)

## 📝 Description
Ce projet permet de capturer des mouvements avec une caméra GoPro et de les reproduire sur un robot Niryo, y compris l'état de la pince (ouverte/fermée). Le système extrait les données des capteurs IMU (Inertial Measurement Unit) de la GoPro à partir des métadonnées GPMF (GoPro Metadata Format), traite ces données, et génère des séquences de mouvements pour le robot.

![Image](https://github.com/user-attachments/assets/10542f42-1439-4394-b3a9-fc606ec81023)

![Image](https://github.com/user-attachments/assets/32683f64-60a4-4f4d-ba40-00aef9a1c183)

## 🌟 Fonctionnalités principales
- Extraction des données de mouvement (accéléromètre et gyroscope) à partir des fichiers vidéo GoPro
- Détection de l'état de la pince par analyse vidéo
- Conversion des mouvements en commandes pour le robot Niryo
- Visualisation des données et mouvements en 2D et 3D
- Interface utilisateur simple pour la sélection de vidéos et la configuration

### Détection de l'état de la pince
Le système détecte l'état de la pince (ouvert/fermé) en analysant la présence de couleur rouge dans une région d'intérêt définie:

| Pince Ouverte | Pince Fermée |
|---------------|--------------|
| ![Image](https://github.com/user-attachments/assets/07d0daec-5d20-4e2a-b6b6-2212aabb7448) | ![Image](https://github.com/user-attachments/assets/219d7b8e-a526-461b-8e24-23c6aedfcf74) |

### Interface de sélection de ROI
L'utilisateur peut définir la région d'intérêt pour la détection de la pince:

![Image](https://github.com/user-attachments/assets/886b4e7a-f886-4a3e-99b2-0a655bad0d5d)

## 🛠️ Prérequis
- Python 3.7 ou supérieur
- Robot Niryo connecté au réseau
- Vidéos GoPro contenant des métadonnées GPMF
- Bibliothèques Python (voir `requirements.txt`)

## 📂 Structure du projet
Le projet est organisé en trois étapes principales de traitement, chaque étape générant des données dans un dossier spécifique:

```
Projet-Imitation-Mouvement-GoPro-Niryo/
├── Python-Program/
│   └── GPMF_Parser/
│       ├── videos/                   # Dossier contenant les vidéos GoPro
│       ├── 1-IMU-Json-Extract/       # Données brutes extraites des vidéos
│       ├── 2-Reorder-IMU-Data/       # Données IMU réorganisées
│       ├── 3-Json-adapt-niryo-movement/ # Mouvements adaptés pour Niryo
│       ├── main.py                   # Point d'entrée principal
│       ├── gpmf2json.py              # Extraction des données GPMF
│       ├── IMU_parser.py             # Traitement des données IMU
│       ├── adapt_json_niryo.py       # Conversion pour le robot Niryo
│       ├── execute_robot_movement.py # Exécution des mouvements sur le robot
│       ├── gripper_detection_color.py # Détection de l'état de la pince
│       └── roi_config.json           # Configuration de la région d'intérêt
```

![Image](https://github.com/user-attachments/assets/b68bf1a2-0f8c-4778-82c7-6c82445735a0)

## 🚀 Installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/votre-utilisateur/repo_tempo_sae6.git
cd repo_tempo_sae6
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Placez vos vidéos GoPro dans le dossier `videos`

## 📋 Guide d'utilisation

### 1️⃣ Extraction et traitement des données

Pour traiter une vidéo GoPro et générer les fichiers de mouvement:

```bash
cd Projet-Imitation-Mouvement-GoPro-Niryo/Python-Program/GPMF_Parser
python main.py
```

L'interface vous guidera à travers:
- La sélection de la vidéo à traiter
- L'extraction des données GPMF
- La réorganisation des données IMU
- La génération des fichiers de mouvement pour le robot Niryo

![Image](https://github.com/user-attachments/assets/e05f0b08-ecc6-4479-942a-43f79f65cd3d)

### 2️⃣ Exécution des mouvements sur le robot

Pour reproduire les mouvements sur le robot Niryo:

```bash
python execute_robot_movement.py
```

Ce script:
1. Liste les fichiers de mouvement disponibles
2. Vous permet de sélectionner un fichier
3. Configure la détection de la pince
4. Se connecte au robot Niryo
5. Exécute les mouvements tout en reproduisant l'état de la pince

### 3️⃣ Visualisation des données

Pour visualiser les données IMU ou les mouvements du robot:

```bash
python IMU_parser.py
```

Vous pourrez choisir entre:
- Visualisation des données IMU en 2D/3D
- Visualisation des trajectoires du robot

#### Exemples de visualisations

**Trajectoire 3D du robot:**
![Image](https://github.com/user-attachments/assets/d53b63a4-b14d-406d-8df6-811877287b8a)

**Graphiques des données IMU:**
![Image](https://github.com/user-attachments/assets/e1aeb678-6a06-4fff-9433-568d28b9a09a)

## 🔍 Fonctionnement détaillé

### Étape 1: Extraction des données GPMF
Le programme extrait les métadonnées GPMF des vidéos GoPro et les convertit en format JSON. Ces données contiennent les informations des capteurs comme l'accéléromètre et le gyroscope.

### Étape 2: Traitement des données IMU
Les données brutes sont ensuite traitées et réorganisées pour aligner correctement les axes des capteurs. La structure de données est convertie d'un format Y, -X, Z vers X, Y, Z pour correspondre au système de coordonnées du robot Niryo.

### Étape 3: Génération des mouvements pour Niryo
Les données traitées sont converties en séquences de mouvements adaptées aux coordonnées spatiales du robot Niryo, prêtes à être exécutées.

### Détection de l'état de la pince
Le programme utilise l'analyse d'image par OpenCV pour détecter la présence de rouge dans une région d'intérêt prédéfinie. Si le ratio de pixels rouges dépasse un certain seuil, la pince est considérée comme fermée.

## 🤖 Configuration du robot Niryo

1. Le robot doit être connecté au même réseau que l'ordinateur exécutant le programme
2. L'adresse IP par défaut du robot est `172.21.182.56` (modifiable dans le code)
3. Avant l'exécution, le programme vous propose de calibrer le robot
4. Vous pouvez choisir entre la pince ou la ventouse comme outil

## 🔧 Dépannage

### Problèmes courants:
- **Erreur de connexion au robot**: Vérifiez que l'adresse IP est correcte et que le robot est allumé et connecté au réseau
- **Problème d'extraction GPMF**: Assurez-vous que votre vidéo GoPro contient bien des métadonnées GPMF
- **Détection incorrecte de la pince**: Réajustez la région d'intérêt (ROI) et le seuil de détection

### Astuces:
- Pour une meilleure détection de la pince, utilisez un objet rouge distinct
- Calibrez le robot avant chaque séquence de mouvements
- Effectuez des mouvements lents avec la GoPro pour une meilleure précision

## 👥 Auteurs
- Alexy LESAULNIER
- Kylian MOURGUES

## 📄 Licence
Ce projet est réalisé dans le cadre du projet final de BUT GEII à l'IUT de Nantes.

## 🔗 Liens utiles
- [Documentation pyniryo](https://docs.niryo.com/dev/pyniryo/v1.0.0/en/index.html)
- [Documentation GoPro GPMF](https://github.com/gopro/gpmf-parser)
- [OpenCV Documentation](https://docs.opencv.org/)
