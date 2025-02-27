import json
import matplotlib.pyplot as plt
import numpy as np
import os
from mpl_toolkits.mplot3d import Axes3D  # Pour le tracé 3D


def get_gyro_accel_data(imu_json):
    """Extract and flatten gyroscopic, accelerometer, and time data from the IMU data .json file"""
    print(f"Reading JSON file: {os.path.basename(imu_json)}")
    with open(imu_json, 'r') as f:
        imu_data = json.load(f)

    print("Extracting gyroscope and accelerometer data...")
    data = []

    for entry in imu_data:
        if "Gyroscope" in entry and "3-axis gyroscope" in entry["Gyroscope"]:
            gyro_data = entry["Gyroscope"]["3-axis gyroscope"]
        else:
            gyro_data = []

        if "Accelerometer" in entry and "3-axis accelerometer" in entry["Accelerometer"]:
            accel_data = entry["Accelerometer"]["3-axis accelerometer"]
        else:
            accel_data = []

        if "Interval in ms" in entry:
            start_time, end_time = map(int, entry["Interval in ms"].strip("()").split(", "))
            interval_duration = end_time - start_time
            sample_interval = interval_duration / 199
        else:
            start_time = 0
            sample_interval = 0

        for i in range(len(gyro_data)):
            timestamp = start_time + i * sample_interval
            data_entry = {
                "3-axis gyroscope": gyro_data[i] if i < len(gyro_data) else None,
                "3-axis accelerometer": accel_data[i] if i < len(accel_data) else None,
                "Timestamp in ms": timestamp
            }
            data.append(data_entry)

    return data


def reorder_data(data, base_filename):
    print(f"Reordering data axes for {base_filename}")
    output_dir = os.path.join(os.path.dirname(__file__), "2-Reorder-IMU-Data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"reordered_{base_filename}")
    
    print("Reorganizing axis orientations...")
    # Data order in gyro and accel is Y, -X, Z and we want X, Y, Z
    for entry in data:
        gyro = entry["3-axis gyroscope"]
        accel = entry["3-axis accelerometer"]
        entry["3-axis gyroscope"] = [-gyro[1], gyro[0], gyro[2]]
        entry["3-axis accelerometer"] = [-accel[1], accel[0], accel[2]]

    print(f"Saving reordered data to: {os.path.basename(output_path)}")
    # Write the reordered data to a JSON file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    return data


def get_gravity_data(imu_json):
    """Extract and flatten gravity data from the IMU data .json file"""
    # Utiliser un chemin absolu
    imu_json = r'c:\Users\alexy\Dropbox\PC\Desktop\IUT Nantes\GEII\BUT_3\SAé6-GoPro_Niryo\Projet-Imitation-Mouvement-GoPro-Niryo\gopro-telemetry2json\IMU_test.json'
    with open(imu_json, 'r') as f:
        imu_data = json.load(f)

    gravity_data = []
    gravity_timestamps = []

    for entry in imu_data:
        if "Gravity Vector" in entry:
            gravity_vector = entry["Gravity Vector"]["Gravity Vector"]
            timestamp = entry["Gravity Vector"]["Timestamp in microseconds"] / 1000.0  # Convert to milliseconds
            sample_interval = 1001 / 59  # 60 samples over 1001ms interval

            for i, vector in enumerate(gravity_vector):
                gravity_data.append(vector)
                gravity_timestamps.append(timestamp + i * sample_interval)

    return gravity_data, gravity_timestamps


def plot_data(data):
    """Plot gyroscope and accelerometer data"""
    timestamps = [entry["Timestamp in ms"] for entry in data]
    gyro_x = [entry["3-axis gyroscope"][0] for entry in data]
    gyro_y = [entry["3-axis gyroscope"][1] for entry in data]
    gyro_z = [entry["3-axis gyroscope"][2] for entry in data]
    accel_x = [entry["3-axis accelerometer"][0] for entry in data]
    accel_y = [entry["3-axis accelerometer"][1] for entry in data]
    accel_z = [entry["3-axis accelerometer"][2] for entry in data]

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(timestamps, gyro_x, label='Gyro X')
    plt.plot(timestamps, gyro_y, label='Gyro Y')
    plt.plot(timestamps, gyro_z, label='Gyro Z')
    plt.title('Gyroscope Data')
    plt.xlabel('Timestamp (ms)')
    plt.ylabel('Gyroscope (rad/s)')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(timestamps, accel_x, label='Accel X')
    plt.plot(timestamps, accel_y, label='Accel Y')
    plt.plot(timestamps, accel_z, label='Accel Z')
    plt.title('Accelerometer Data')
    plt.xlabel('Timestamp (ms)')
    plt.ylabel('Accelerometer (m/s²)')
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_data_3d(data):
    """Plot gyroscope and accelerometer data in 3D"""
    # Extraire les données
    gyro_x = [entry["3-axis gyroscope"][0] for entry in data]
    gyro_y = [entry["3-axis gyroscope"][1] for entry in data]
    gyro_z = [entry["3-axis gyroscope"][2] for entry in data]
    accel_x = [entry["3-axis accelerometer"][0] for entry in data]
    accel_y = [entry["3-axis accelerometer"][1] for entry in data]
    accel_z = [entry["3-axis accelerometer"][2] for entry in data]

    # Créer une figure avec deux sous-plots 3D
    fig = plt.figure(figsize=(15, 6))
    
    # Plot gyroscope
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot(gyro_x, gyro_y, gyro_z)
    ax1.set_title('Données gyroscope 3D')
    ax1.set_xlabel('X (rad/s)')
    ax1.set_ylabel('Y (rad/s)')
    ax1.set_zlabel('Z (rad/s)')
    
    # Plot accelerometer
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot(accel_x, accel_y, accel_z)
    ax2.set_title('Données accéléromètre 3D')
    ax2.set_xlabel('X (m/s²)')
    ax2.set_ylabel('Y (m/s²)')
    ax2.set_zlabel('Z (m/s²)')
    
    plt.tight_layout()
    plt.show()


def plot_niryo_movements_3d(json_file_path):
    """
    Visualise les mouvements du Niryo en 3D à partir d'un fichier JSON
    """
    try:
        # Charger les données du fichier JSON
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Extraire les coordonnées x, y, z
        x_coords = []
        y_coords = []
        z_coords = []
        
        for movement in data.values():
            coords = movement['coordinates']
            x_coords.append(coords[0])
            y_coords.append(coords[1])
            z_coords.append(coords[2])
        
        # Créer la figure 3D avec un ratio d'aspect égal
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Tracer la trajectoire avec des marqueurs plus petits et plus fréquents
        ax.plot(x_coords, y_coords, z_coords, 'b-', linewidth=1, label='Trajectoire')
        ax.scatter(x_coords, y_coords, z_coords, c='r', marker='.', s=30, alpha=0.5)
        
        # Ajouter les points de départ et d'arrivée
        ax.scatter(x_coords[0], y_coords[0], z_coords[0], c='g', marker='o', s=100, label='Départ')
        ax.scatter(x_coords[-1], y_coords[-1], z_coords[-1], c='r', marker='o', s=100, label='Arrivée')
        
        # Configurer les axes avec des échelles égales
        max_range = np.array([
            max(x_coords) - min(x_coords),
            max(y_coords) - min(y_coords),
            max(z_coords) - min(z_coords)
        ]).max() / 2.0
        
        mid_x = (max(x_coords) + min(x_coords)) * 0.5
        mid_y = (max(y_coords) + min(y_coords)) * 0.5
        mid_z = (max(z_coords) + min(z_coords)) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        # Définir un angle de vue fixe
        ax.view_init(elev=20, azim=45)
        
        # Configurer les labels et le titre
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Trajectoire du robot Niryo')
        
        # Ajouter une légende
        ax.legend()
        
        # Ajouter une grille
        ax.grid(True)
        
        # Forcer un ratio d'aspect égal pour tous les axes
        ax.set_box_aspect([1,1,1])
        
        plt.show()
        
    except Exception as e:
        print(f"Erreur lors de la visualisation: {str(e)}")


def plot_niryo_movements_2d(json_file_path):
    """
    Visualise les mouvements du Niryo en 2D à partir d'un fichier JSON du dossier 3-Json-adapt-niryo-movement
    """
    try:
        # Charger les données du fichier JSON
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Extraire les coordonnées et angles
        movements = []
        for movement in data.values():
            movements.append(movement['coordinates'])
        
        movements = np.array(movements)
        
        # Créer la figure avec 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Indices des mouvements
        movement_indices = range(len(movements))
        
        # Plot des positions (x, y, z)
        ax1.plot(movement_indices, movements[:, 0], 'r-', label='X')
        ax1.plot(movement_indices, movements[:, 1], 'g-', label='Y')
        ax1.plot(movement_indices, movements[:, 2], 'b-', label='Z')
        ax1.set_title('Positions du robot')
        ax1.set_xlabel('Numéro de mouvement')
        ax1.set_ylabel('Position (m)')
        ax1.grid(True)
        ax1.legend()
        
        # Plot des orientations (roll, pitch, yaw)
        ax2.plot(movement_indices, movements[:, 3], 'r-', label='Roll')
        ax2.plot(movement_indices, movements[:, 4], 'g-', label='Pitch')
        ax2.plot(movement_indices, movements[:, 5], 'b-', label='Yaw')
        ax2.set_title('Orientations du robot')
        ax2.set_xlabel('Numéro de mouvement')
        ax2.set_ylabel('Angle (rad)')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Erreur lors de la visualisation 2D: {str(e)}")


def visualize_niryo_movements():
    """Interface pour sélectionner et visualiser les mouvements du Niryo"""
    # Chemin vers le dossier contenant les fichiers JSON du Niryo
    niryo_dir = os.path.join(os.path.dirname(__file__), "3-Json-adapt-niryo-movement")
    
    # Lister tous les fichiers JSON
    json_files = [f for f in os.listdir(niryo_dir) if f.endswith('.json')]
    
    if not json_files:
        print("Aucun fichier JSON trouvé dans le dossier 3-Json-adapt-niryo-movement")
        return
    
    # Afficher les fichiers disponibles
    print("\nFichiers de mouvements disponibles:")
    for i, file in enumerate(json_files, 1):
        print(f"{i}. {file}")
    
    # Demander à l'utilisateur de choisir un fichier
    while True:
        try:
            choice = input("\nChoisissez le numéro du fichier à visualiser (ou 'q' pour quitter): ")
            if choice.lower() == 'q':
                return
            
            index = int(choice) - 1
            if 0 <= index < len(json_files):
                file_path = os.path.join(niryo_dir, json_files[index])
                
                # Demander quel type de visualisation
                print("\nType de visualisation:")
                print("1. Vue 3D")
                print("2. Courbes 2D")
                viz_choice = input("Votre choix (1 ou 2): ")
                
                if viz_choice == "1":
                    plot_niryo_movements_3d(file_path)
                elif viz_choice == "2":
                    plot_niryo_movements_2d(file_path)
                else:
                    print("Choix de visualisation invalide")
                break
            else:
                print("Choix invalide. Veuillez réessayer.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")


def visualize_imu_data(json_file_path=None):
    """
    Fonction pour visualiser les données IMU depuis n'importe quel dossier
    Args:
        json_file_path: Chemin optionnel vers un fichier JSON spécifique
    """
    if json_file_path is None:
        # Si aucun fichier n'est spécifié, permettre à l'utilisateur de choisir
        directories = {
            "1": "1-IMU-Json-Extract",
            "2": "2-Reorder-IMU-Data",
            "3": "3-Json-adapt-niryo-movement"
        }
        
        print("\nChoisissez le dossier à analyser:")
        for key, directory in directories.items():
            print(f"{key}. {directory}")
        
        choice = input("\nVotre choix (1-3): ")
        if choice not in directories:
            print("Choix invalide")
            return
            
        directory = os.path.join(os.path.dirname(__file__), directories[choice])
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        if not json_files:
            print(f"Aucun fichier JSON trouvé dans {directory}")
            return
            
        print("\nFichiers disponibles:")
        for i, file in enumerate(json_files, 1):
            print(f"{i}. {file}")
            
        file_choice = input("\nChoisissez le numéro du fichier à analyser: ")
        try:
            file_index = int(file_choice) - 1
            if 0 <= file_index < len(json_files):
                json_file_path = os.path.join(directory, json_files[file_index])
            else:
                print("Numéro de fichier invalide")
                return
        except ValueError:
            print("Veuillez entrer un numéro valide")
            return
    
    # Charger et afficher les données
    try:
        data = get_gyro_accel_data(json_file_path)
        print("\nType de visualisation:")
        print("1. Graphiques 2D")
        print("2. Visualisation 3D")
        viz_choice = input("Votre choix (1 ou 2): ")
        
        if viz_choice == "1":
            plot_data(data)
        elif viz_choice == "2":
            plot_data_3d(data)
        else:
            print("Choix invalide")
    except Exception as e:
        print(f"Erreur lors de l'analyse des données: {str(e)}")


if __name__ == "__main__":
    print("\nQue souhaitez-vous visualiser ?")
    print("1. Données IMU brutes")
    print("2. Mouvements du Niryo en 3D")
    
    choice = input("\nVotre choix (1 ou 2): ")
    if choice == "1":
        visualize_imu_data()
    elif choice == "2":
        visualize_niryo_movements()
    else:
        print("Choix invalide")
