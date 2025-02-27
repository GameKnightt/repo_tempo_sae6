import os
from pyniryo import *
import json
import time
import cv2
import numpy as np
from threading import Thread, Event, Lock

class GripperDetector:
    def __init__(self, robot=None):
        self.robot = robot
        self.roi = None
        self.roi_points = None
        self.red_threshold = 0.1
        self.window_name = "Détection Pince"
        self.last_state = None
        self.scale = 1.0

    def select_roi(self, frame):
        """Permet à l'utilisateur de sélectionner la zone ROI"""
        print("\nSélectionnez la zone de détection de la pince:")
        print("1. Cliquez et glissez pour sélectionner la zone")
        print("2. Appuyez sur ESPACE ou ENTRÉE pour valider")
        print("3. Appuyez sur 'c' pour recommencer la sélection")
        
        selection_window = "Selection ROI"
        cv2.namedWindow(selection_window, cv2.WINDOW_NORMAL)
        cv2.imshow(selection_window, frame)
        cv2.waitKey(100)
        
        self.roi_points = cv2.selectROI(selection_window, frame, False)
        cv2.destroyWindow(selection_window)
        
        self.roi = {
            'x1': int(self.roi_points[0]),
            'y1': int(self.roi_points[1]),
            'x2': int(self.roi_points[0] + self.roi_points[2]),
            'y2': int(self.roi_points[1] + self.roi_points[3]),
            'original_width': frame.shape[1],
            'original_height': frame.shape[0]
        }
        
        with open('roi_config.json', 'w') as f:
            json.dump(self.roi, f)

    def try_load_roi(self):
        """Essaie de charger la ROI, retourne False si échec"""
        try:
            with open('roi_config.json', 'r') as f:
                self.roi = json.load(f)
            return True
        except FileNotFoundError:
            return False

    def detect_red(self, frame):
        """Détecte la présence de rouge dans la ROI"""
        if self.roi is None or frame is None or frame.size == 0:
            return False, frame if frame is not None else np.zeros((480, 640, 3), dtype=np.uint8)

        try:
            # Vérifier les dimensions de frame par rapport à la ROI
            frame_height, frame_width = frame.shape[:2]
            # Ajuster la ROI si nécessaire
            x1 = min(self.roi['x1'], frame_width - 1)
            y1 = min(self.roi['y1'], frame_height - 1)
            x2 = min(self.roi['x2'], frame_width)
            y2 = min(self.roi['y2'], frame_height)

            if x2 <= x1 or y2 <= y1:
                return False, frame

            # Extraire la ROI avec les dimensions vérifiées
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                return False, frame

            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
            red_ratio = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
            
            color = (0, 0, 255) if red_ratio > self.red_threshold else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            text = "PINCE FERMEE" if red_ratio > self.red_threshold else "PINCE OUVERTE"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            return red_ratio > self.red_threshold, frame
            
        except Exception as e:
            print(f"Erreur lors de la détection: {e}")
            return False, frame

    def update_gripper_state(self, is_closed):
        """Met à jour l'état de la pince"""
        if self.robot is None or is_closed == self.last_state:
            return

        try:
            if is_closed:
                self.robot.close_gripper()
                print("Fermeture pince")
            else:
                self.robot.open_gripper()
                print("Ouverture pince")
            self.last_state = is_closed
        except Exception as e:
            print(f"Erreur contrôle pince: {e}")

def load_movements(filename):
    """Charge les mouvements depuis le fichier JSON"""
    file_path = os.path.join(os.path.dirname(__file__), "3-Json-adapt-niryo-movement", filename)
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Convertir les données en format séquence
            sequence = {
                "positions": [
                    {
                        "name": key,  # Utiliser le nom original du mouvement (movement_X)
                        "coordinates": movement["coordinates"]
                    }
                    for key, movement in data.items()
                ]
            }
            sequence["positions"].sort(key=lambda x: int(x["name"].split("_")[1]))  # Trier par numéro de mouvement
            return sequence
    except FileNotFoundError:
        print(f"Erreur: Le fichier {file_path} n'existe pas")
        raise
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier {file_path} n'est pas un JSON valide")
        raise
    except Exception as e:
        print(f"Erreur lors du chargement du fichier: {str(e)}")
        raise

# Suppression des fonctions convert_color_to_value, rgb_cycle et orange_blink qui ne sont plus nécessaires

def calibrate_robot(robot):
    """Calibration du robot si nécessaire"""
    while True:
        response = input("Voulez-vous calibrer le robot ? (o/n): ").lower()
        if response in ['o', 'n']:
            if response == 'o':
                print("Démarrage de la calibration...")
                robot.calibrate_auto()
                print("Calibration terminée!")
            break
        print("Veuillez répondre par 'o' pour oui ou 'n' pour non.")

def configure_tool(robot):
    """Configuration de l'outil et du TCP"""
    # Définition des TCPs
    VACUUM_TCP = [0.05, 0, 0, 0, 0, 0]  # TCP pour la ventouse
    GRIPPER_TCP = [0.085, 0, 0, 0, 0, 0]  # TCP pour la pince

    while True:
        print("\nSélection de l'outil:")
        print("1. Pince")
        print("2. Ventouse")
        tool_type = input("Choisissez l'outil (1/2): ")
        
        if tool_type in ['1', '2']:
            # Sélection du TCP en fonction de l'outil
            selected_tcp = VACUUM_TCP if tool_type == "2" else GRIPPER_TCP
            tool_name = "Ventouse" if tool_type == "2" else "Pince"

            # Configuration du TCP
            print("\nConfiguration du TCP...")
            robot.reset_tcp()
            print('TCP Reset')
            robot.set_tcp(selected_tcp)
            print(f'TCP Set pour {tool_name}')
            robot.enable_tcp(True)
            print('TCP Activé')
            break
        print("Choix invalide. Veuillez sélectionner 1 ou 2.")

def execute_movement(robot, coordinates):
    """Exécute un mouvement"""
    try:
        robot.move_pose(*coordinates)
        return True
    except Exception as e:
        print(f"Erreur lors de l'exécution du mouvement: {e}")
        return False

def find_camera():
    """Trouve une caméra disponible"""
    def try_camera(source):
        try:
            cap = cv2.VideoCapture(source)
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"Caméra trouvée sur : {source}")
                    return cap
                cap.release()
        except Exception:
            pass
        return None

    # Essayer d'abord les chemins directs
    print("Recherche de caméras...")
    for dev_path in ['/dev/video0', '/dev/video1', '/dev/video2']:
        cap = try_camera(dev_path)
        if cap:
            return cap
    
    # Essayer les indices numériques
    for idx in range(10):  # Tester jusqu'à 10 indices
        cap = try_camera(idx)
        if cap:
            return cap
    
    return None

class VideoThread(Thread):
    """Thread dédié à la lecture et l'affichage de la vidéo"""
    def __init__(self, video_path, detector):
        Thread.__init__(self)
        self.video_path = video_path
        self.detector = detector
        self.cap = None
        self.frame = None
        self.is_closed = False
        self.running = True
        self.frame_lock = Lock()
        self.frame_ready = Event()
        self.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête

    def run(self):
        """Boucle principale du thread vidéo"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("Erreur: Impossible d'ouvrir la vidéo")
            return

        cv2.namedWindow('Detection Feed', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Detection Feed', 800, 600)

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reboucler la vidéo
                continue

            # Détection et mise à jour de l'état de la pince
            is_closed, processed_frame = self.detector.detect_red(frame)
            
            with self.frame_lock:
                self.frame = processed_frame
                self.is_closed = is_closed
                self.frame_ready.set()

            cv2.imshow('Detection Feed', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.03)  # ~30 FPS

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def get_current_state(self):
        """Récupère l'état actuel de la pince"""
        with self.frame_lock:
            return self.is_closed

    def stop(self):
        """Arrête le thread vidéo"""
        self.running = False
        if self.cap:
            self.cap.release()

def main():
    try:
        # Vérifier et créer le dossier si nécessaire
        niryo_dir = os.path.join(os.path.dirname(__file__), "3-Json-adapt-niryo-movement")
        os.makedirs(niryo_dir, exist_ok=True)

        # Liste des fichiers disponibles
        json_files = [f for f in os.listdir(niryo_dir) if f.endswith('.json')]
        
        if not json_files:
            print("Aucun fichier de séquence trouvé dans le dossier 3-Json-adapt-niryo-movement")
            print("Veuillez d'abord générer des fichiers de séquence.")
            return

        print("\nFichiers de séquence disponibles:")
        for i, file in enumerate(json_files, 1):
            print(f"{i}. {file}")

        # Demander à l'utilisateur de choisir un fichier
        try:
            choice = int(input("\nChoisissez le numéro du fichier à exécuter: ")) - 1
            if choice < 0 or choice >= len(json_files):
                print("Choix invalide")
                return
            selected_file = json_files[choice]
        except ValueError:
            print("Veuillez entrer un numéro valide")
            return

        # Sélection de la vidéo correspondante avant la connexion au robot
        video_name = selected_file.replace('niryo_', '').replace('.json', '.MP4')
        video_path = os.path.join(os.path.dirname(__file__), 'videos', video_name)
        
        if not os.path.exists(video_path):
            print(f"\n❌ Vidéo correspondante non trouvée: {video_path}")
            print(f"🔍 Recherche de: {video_name}")
            return

        # Configuration initiale de la vidéo et de la détection
        print("\n=== Configuration de la détection de la pince ===")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Erreur: Impossible d'ouvrir la vidéo")
            return

        # Créer le détecteur sans le robot pour le moment
        detector = GripperDetector()
        
        # Lire la première frame pour la configuration
        ret, frame = cap.read()
        if not ret:
            print("Erreur: Impossible de lire la vidéo")
            cap.release()
            return

        # Configurer la ROI si nécessaire
        if not detector.try_load_roi():
            detector.select_roi(frame)
        
        cap.release()
        cv2.destroyAllWindows()

        # Connexion au robot
        print("\n=== Configuration du robot ===")
        print("Connexion au robot...")
        robot = NiryoRobot("172.21.182.56")
        print("Robot connecté!")

        # Activer le mode autonome
        robot.set_arm_max_velocity(100)
        robot.set_learning_mode(False)

        # Calibration si nécessaire
        calibrate_robot(robot)

        # Configuration de l'outil et du TCP
        configure_tool(robot)

        # Mettre à jour le détecteur avec le robot
        detector.robot = robot

        # Ouvrir la pince au maximum
        print("Ouverture de la pince...")
        robot.open_gripper(speed=100)
        print("Pince ouverte!")

        # Charger les mouvements
        print("\nChargement des mouvements...")
        sequence_config = load_movements(selected_file)
        print(f"Nombre de mouvements chargés : {len(sequence_config['positions'])}")

        # Initialiser et démarrer le thread vidéo
        print("\n=== Démarrage de l'exécution ===")
        video_thread = VideoThread(video_path, detector)
        video_thread.start()
        time.sleep(1)  # Attendre que la vidéo démarre

        # Exécution immédiate des mouvements
        for position in sequence_config["positions"]:
            try:
                coordinates = position["coordinates"]
                print(f"\nDéplacement vers: {position['name']}")
                
                # Récupérer l'état de la pince depuis le thread vidéo
                is_closed = video_thread.get_current_state()
                detector.update_gripper_state(is_closed)
                
                # Exécuter le mouvement
                execute_movement(robot, coordinates)
                time.sleep(0.1)

            except Exception as e:
                print(f"Erreur lors du mouvement: {e}")
                break

    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if 'video_thread' in locals():
            video_thread.stop()
            video_thread.join()
        if 'robot' in locals():
            robot.close_connection()

if __name__ == "__main__":
    main()