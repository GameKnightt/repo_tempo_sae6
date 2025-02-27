import numpy as np
import os
import json
from scipy import integrate
from scipy.signal import butter, filtfilt

class SimpleKalmanFilter:
    def __init__(self, q=0.1, r=0.1):
        self.q = q  # Process noise
        self.r = r  # Measurement noise
        self.p = 1000  # Initial estimation error covariance
        self.x = 0  # Initial estimate
        
    def update(self, measurement):
        # Prediction
        self.p = self.p + self.q
        
        # Update
        k = self.p / (self.p + self.r)  # Kalman gain
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * self.p
        
        return self.x

class IMUProcessor:
    def __init__(self, dt=0.01):
        self.dt = dt
        # Un filtre pour chaque axe
        self.kf_x = SimpleKalmanFilter()
        self.kf_y = SimpleKalmanFilter()
        self.kf_z = SimpleKalmanFilter()
        # Paramètres du filtre passe-haut
        self.cutoff_freq = 0.1  # Fréquence de coupure à 0.1 Hz
        self.filter_order = 2   # Ordre du filtre

    def apply_highpass_filter(self, data):
        """Applique un filtre passe-haut Butterworth sur les données"""
        nyquist = 1.0 / (2.0 * self.dt)
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.filter_order, normal_cutoff, btype='high', analog=False)
        
        filtered_data = np.zeros_like(data)
        for i in range(3):  # Pour chaque axe x,y,z
            filtered_data[:, i] = filtfilt(b, a, data[:, i])
            
        return filtered_data

    def integrate_acceleration(self, accel_data):
        """
        Intègre l'accélération filtrée deux fois pour obtenir la position
        """
        dt = self.dt
        time = np.arange(0, len(accel_data) * dt, dt)
        
        # Conversion en array numpy et application du filtre passe-haut
        accel_array = np.array(accel_data)
        filtered_accel = self.apply_highpass_filter(accel_array)
        
        # Première intégration: accélération -> vitesse
        velocity = np.zeros((len(filtered_accel), 3))
        for i in range(3):
            # Utilisation de cumulative_trapezoid au lieu de cumtrapz
            velocity[:, i] = integrate.cumulative_trapezoid(
                filtered_accel[:, i],
                time,
                initial=0
            )
        
        # Deuxième intégration: vitesse -> position
        position = np.zeros((len(velocity), 3))
        for i in range(3):
            # Utilisation de cumulative_trapezoid au lieu de cumtrapz
            position[:, i] = integrate.cumulative_trapezoid(
                velocity[:, i],
                time,
                initial=0
            )
            
        return velocity, position

    def process_acceleration(self, accel_data, sampling_rate=1.0):
        """Process acceleration data with simplified Kalman filters"""
        velocity, raw_position = self.integrate_acceleration(accel_data)
        filtered_data = []
        
        step = int(1.0 / sampling_rate / self.dt)
        
        for i in range(0, len(accel_data), step):
            # Filtrer chaque axe séparément
            x = self.kf_x.update(raw_position[i][0])
            y = self.kf_y.update(raw_position[i][1])
            z = self.kf_z.update(raw_position[i][2])
            
            filtered_data.append([x, y, z])
            
        return filtered_data

class WorkspaceTransformer:
    def __init__(self):
        # Définition des limites de l'espace de travail du Niryo (en mètres)
        self.workspace_limits = {
            'x': {'min': 0.15, 'max': 0.35},    # Profondeur
            'y': {'min': -0.2, 'max': 0.2},     # Largeur
            'z': {'min': 0.0, 'max': 0.35}      # Hauteur
        }
        
        # Point central de l'espace de travail
        self.workspace_center = {
            'x': (self.workspace_limits['x']['max'] + self.workspace_limits['x']['min']) / 2,
            'y': (self.workspace_limits['y']['max'] + self.workspace_limits['y']['min']) / 2,
            'z': (self.workspace_limits['z']['max'] + self.workspace_limits['z']['min']) / 2
        }

    def normalize_and_scale_positions(self, positions):
        """
        Normalise et adapte les positions à l'espace de travail du Niryo
        """
        positions = np.array(positions)
        
        # Trouver les min/max pour chaque axe
        min_vals = np.min(positions, axis=0)
        max_vals = np.max(positions, axis=0)
        
        # Normaliser les positions entre 0 et 1
        normalized = np.zeros_like(positions)
        for i in range(3):
            if max_vals[i] != min_vals[i]:
                normalized[:, i] = (positions[:, i] - min_vals[i]) / (max_vals[i] - min_vals[i])
            else:
                normalized[:, i] = 0.5  # Valeur centrale si pas de variation
        
        # Adapter à l'espace de travail du Niryo
        transformed = np.zeros_like(positions)
        axes = ['x', 'y', 'z']
        for i, axis in enumerate(axes):
            workspace_range = self.workspace_limits[axis]['max'] - self.workspace_limits[axis]['min']
            transformed[:, i] = (normalized[:, i] * workspace_range) + self.workspace_limits[axis]['min']
        
        # Centrer les mouvements dans l'espace de travail
        transformed[:, 0] = self.workspace_center['x'] + (transformed[:, 0] - np.mean(transformed[:, 0]))
        transformed[:, 1] = self.workspace_center['y'] + (transformed[:, 1] - np.mean(transformed[:, 1]))
        transformed[:, 2] = self.workspace_center['z'] + (transformed[:, 2] - np.mean(transformed[:, 2]))
        
        # Vérifier et ajuster les limites
        for i, axis in enumerate(axes):
            transformed[:, i] = np.clip(
                transformed[:, i],
                self.workspace_limits[axis]['min'],
                self.workspace_limits[axis]['max']
            )
        
        return transformed

def convert_to_robot_format(imu_data, sampling_rate=1.0):
    """Convert IMU data to Niryo robot format"""
    processor = IMUProcessor()
    workspace_transformer = WorkspaceTransformer()
    
    # Extract acceleration and gyro data from the correct structure
    accel_data = []
    gyro_data = []
    
    try:
        # Debug print pour voir la structure des données
        print("DEBUG: Structure of first IMU data entry:", json.dumps(imu_data[0] if imu_data else {}, indent=2))
        
        for entry in imu_data:
            # Vérifier si les données sont dans la structure correcte
            if isinstance(entry, dict):
                # Essayer différentes structures possibles
                if "Accelerometer" in entry and "Gyroscope" in entry:
                    accel = entry["Accelerometer"].get("3-axis accelerometer", [])
                    gyro = entry["Gyroscope"].get("3-axis gyroscope", [])
                elif "3-axis accelerometer" in entry and "3-axis gyroscope" in entry:
                    accel = entry["3-axis accelerometer"]
                    gyro = entry["3-axis gyroscope"]
                else:
                    print(f"Warning: Skipping entry with unknown structure: {list(entry.keys())}")
                    continue

                # Traitement des données accéléromètre
                if isinstance(accel, list):
                    if accel and isinstance(accel[0], list):
                        # Si nous avons une liste de listes, prenons la première mesure
                        accel = accel[0]
                    if len(accel) == 3:
                        try:
                            accel = [float(x) for x in accel]
                            accel_data.append(accel)
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not convert acceleration data: {e}")
                            continue

                # Traitement des données gyroscope
                if isinstance(gyro, list):
                    if gyro and isinstance(gyro[0], list):
                        # Si nous avons une liste de listes, prenons la première mesure
                        gyro = gyro[0]
                    if len(gyro) == 3:
                        try:
                            gyro = [float(x) for x in gyro]
                            gyro_data.append(gyro)
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not convert gyroscope data: {e}")
                            continue

        if not accel_data or not gyro_data:
            print("DEBUG: No data collected.")
            print(f"Accelerometer data count: {len(accel_data)}")
            print(f"Gyroscope data count: {len(gyro_data)}")
            raise ValueError("No valid acceleration or gyroscope data found in input")

        print(f"DEBUG: Successfully collected {len(accel_data)} data points")
        
        # Conversion en tableau numpy pour le traitement
        accel_data = np.array(accel_data, dtype=np.float64)
        gyro_data = np.array(gyro_data, dtype=np.float64)
        
        # Process positions
        positions = processor.process_acceleration(accel_data, sampling_rate)
        
        # Transform positions to fit Niryo workspace
        transformed_positions = workspace_transformer.normalize_and_scale_positions(positions)
        
        # Calculate step size based on sampling rate
        step = int(1.0 / sampling_rate / processor.dt)
        
        # Combine positions and orientations
        combined_movements = []
        for pos, gyro in zip(transformed_positions, gyro_data[::step]):
            if isinstance(pos, (list, np.ndarray)) and isinstance(gyro, (list, np.ndarray)):
                # Les positions sont déjà en mètres après la transformation
                movement = list(pos[:3]) + list(gyro[:3])  # Combine position and orientation
                combined_movements.append(movement)
        
        # Convert to robot format
        movements = {}
        for i, movement in enumerate(combined_movements):
            movements[f"movement_{i}"] = {
                "coordinates": [round(x, 6) for x in movement]
            }
        
        return movements
    
    except Exception as e:
        print(f"Error processing IMU data: {str(e)}")
        raise

def save_movements_to_json(movements, filename_base):
    """Save processed movements to JSON file"""
    # Créer le dossier s'il n'existe pas
    output_dir = os.path.join(os.path.dirname(__file__), "3-Json-adapt-niryo-movement")
    os.makedirs(output_dir, exist_ok=True)
    
    # Correction du nom de fichier
    filename_base = filename_base.replace('.json', '')  # Enlever l'extension .json si présente
    output_file = os.path.join(output_dir, f"niryo_{filename_base}.json")
    
    try:
        with open(output_file, 'w') as f:
            json.dump(movements, f, indent=4)
        print(f"Successfully saved movements to {output_file}")
    except Exception as e:
        print(f"Error saving movements to {output_file}: {str(e)}")

def load_and_process_imu_data(input_file):
    """Load IMU data from JSON and process it"""
    try:
        with open(input_file, 'r') as f:
            imu_data = json.load(f)
        
        movements = convert_to_robot_format(imu_data)
        filename_base = input_file.split('/')[-1].replace('.json', '')
        save_movements_to_json(movements, filename_base)
        
        return True
    except Exception as e:
        print(f"Error processing IMU data: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    input_dir = os.path.join(os.path.dirname(__file__), "2-Reorder-IMU-Data")
    for json_file in os.listdir(input_dir):
        if json_file.endswith('.json'):
            input_path = os.path.join(input_dir, json_file)
            load_and_process_imu_data(input_path)
