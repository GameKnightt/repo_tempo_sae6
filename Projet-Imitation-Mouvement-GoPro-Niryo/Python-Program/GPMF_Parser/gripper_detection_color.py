import cv2
import numpy as np
import os
import json
import time
from pyniryo import *  # Import de la bibliothèque Niryo

class GripperDetector:
    def __init__(self):
        self.roi = None
        self.roi_points = None
        self.red_threshold = 0.1
        self.window_name = "Détection Pince"
        self.last_state = None  # Ajout du suivi d'état
        self.robot = None  # Référence au robot
        self.scale = 1.0  # Ajout d'un facteur d'échelle

    def connect_to_robot(self, ip="172.21.182.56"):  # Remplacez par l'IP de votre robot
        """Connecte au robot Niryo"""
        try:
            self.robot = NiryoRobot(ip)
            self.robot.calibrate_auto()
            print("Robot connecté et calibré avec succès!")
            return True
        except Exception as e:
            print(f"Erreur de connexion au robot: {e}")
            return False

    def update_gripper_state(self, is_closed):
        """Met à jour l'état de la pince du robot"""
        if self.robot is None:
            return

        current_state = "closed" if is_closed else "open"
        
        # Ne mettre à jour que si l'état a changé
        if current_state != self.last_state:
            try:
                if current_state == "closed":
                    self.robot.close_gripper()
                else:
                    self.robot.open_gripper()
                self.last_state = current_state
                print(f"Pince {current_state}")
            except Exception as e:
                print(f"Erreur lors du contrôle de la pince: {e}")

    def select_roi(self, frame):
        """Permet à l'utilisateur de sélectionner la zone ROI"""
        print("\nInstructions de sélection de la zone:")
        print("1. Cliquez et glissez pour sélectionner la zone")
        print("2. Appuyez sur ESPACE ou ENTRÉE pour valider")
        print("3. Appuyez sur 'c' pour recommencer la sélection")
        
        # Créer une nouvelle fenêtre temporaire pour la sélection
        selection_window = "Selection ROI"
        cv2.namedWindow(selection_window, cv2.WINDOW_NORMAL)
        cv2.imshow(selection_window, frame)
        cv2.waitKey(100)  # Attendre que la fenêtre soit créée
        
        # Faire la sélection
        self.roi_points = cv2.selectROI(selection_window, frame, False)
        
        # Fermer la fenêtre de sélection
        cv2.destroyWindow(selection_window)
        
        # Sauvegarder la ROI et les dimensions originales
        self.roi = {
            'x1': int(self.roi_points[0]),
            'y1': int(self.roi_points[1]),
            'x2': int(self.roi_points[0] + self.roi_points[2]),
            'y2': int(self.roi_points[1] + self.roi_points[3]),
            'original_width': frame.shape[1],  # Sauvegarder les dimensions originales
            'original_height': frame.shape[0]
        }
        
        with open('roi_config.json', 'w') as f:
            json.dump(self.roi, f)
        
        return frame

    def load_roi(self):
        """Charge la configuration ROI si elle existe"""
        try:
            with open('roi_config.json', 'r') as f:
                self.roi = json.load(f)
                self.roi_points = (
                    self.roi['x1'],
                    self.roi['y1'],
                    self.roi['x2'] - self.roi['x1'],
                    self.roi['y2'] - self.roi['y1']
                )
                return True
        except FileNotFoundError:
            return False

    def detect_red(self, frame):
        """Détecte la présence de rouge dans la ROI"""
        if self.roi is None:
            return False, frame

        # Vérifier les dimensions de l'image
        height, width = frame.shape[:2]
        
        # Calculer l'échelle si les dimensions ont changé
        if 'original_width' in self.roi:
            scale_x = width / self.roi['original_width']
            scale_y = height / self.roi['original_height']
            self.scale = min(scale_x, scale_y)
        
        # Ajuster les coordonnées de la ROI avec l'échelle
        x1 = max(0, min(int(self.roi['x1'] * self.scale), width-1))
        y1 = max(0, min(int(self.roi['y1'] * self.scale), height-1))
        x2 = max(0, min(int(self.roi['x2'] * self.scale), width))
        y2 = max(0, min(int(self.roi['y2'] * self.scale), height))
        
        # Vérifier si la ROI est valide
        if x2 <= x1 or y2 <= y1:
            print("ROI invalide, veuillez la resélectionner")
            return False, frame

        try:
            # Extraire la ROI avec les coordonnées sécurisées
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                print("ROI vide, veuillez la resélectionner")
                return False, frame
            
            # Convertir en HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Définir la plage de rouge en HSV
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            # Créer les masques pour le rouge
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
            
            # Calculer le pourcentage de pixels rouges
            red_ratio = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
            
            # Dessiner la ROI sur l'image
            color = (0, 0, 255) if red_ratio > self.red_threshold else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Ajouter le texte d'état
            text = "PINCE FERMEE" if red_ratio > self.red_threshold else "PINCE OUVERTE"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            return red_ratio > self.red_threshold, frame
            
        except Exception as e:
            print(f"Erreur lors de la détection: {e}")
            return False, frame

    def add_instructions(self, frame):
        """Ajoute les instructions à l'image"""
        instructions = [
            "q: Quitter",
            "r: Resélectionner la zone"
        ]
        
        y = 60
        for instruction in instructions:
            cv2.putText(frame, instruction, (10, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 25
        
        return frame

def list_videos():
    """Liste les vidéos disponibles"""
    # Liste plus complète des extensions vidéo courantes
    video_extensions = (
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
        '.webm', '.m4v', '.mpg', '.mpeg', '.MP4', '.AVI',
        '.MOV', '.MKV'
    )
    
    video_dir = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(video_dir):
        print(f"Dossier vidéo non trouvé: {video_dir}")
        return []
    
    videos = []
    # Parcourir récursivement le dossier vidéo
    for root, _, files in os.walk(video_dir):
        for file in files:
            if file.endswith(video_extensions):
                # Chemin relatif par rapport au dossier vidéo
                rel_path = os.path.relpath(os.path.join(root, file), video_dir)
                videos.append(rel_path)
    
    if not videos:
        print(f"Aucune vidéo trouvée dans {video_dir}")
    else:
        print(f"{len(videos)} vidéos trouvées")
    
    return videos

def main():
    detector = GripperDetector()
    
    # Connexion au robot
    if not detector.connect_to_robot():
        print("Impossible de continuer sans connexion au robot")
        return

    # Demander si l'utilisateur veut redéfinir la zone
    redefine = input("Voulez-vous redéfinir la zone de détection ? (o/n): ").lower()
    
    # Sélection de la vidéo avec meilleur affichage
    videos = list_videos()
    if not videos:
        print("Aucune vidéo trouvée dans le dossier 'video'")
        return

    print("\nVidéos disponibles:")
    for i, video in enumerate(videos, 1):
        print(f"{i:2d}. {video}")
    
    try:
        choice = int(input("\nChoisissez une vidéo: ")) - 1
        if choice < 0 or choice >= len(videos):
            print("Choix invalide")
            return
    except ValueError:
        print("Entrée invalide")
        return

    video_path = os.path.join(os.path.dirname(__file__), 'video', videos[choice])
    cap = cv2.VideoCapture(video_path)
    
    # Lire la première frame pour les dimensions
    ret, frame = cap.read()
    if not ret:
        print("Impossible de lire la vidéo")
        return
    
    # Définir le framerate
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_time = int((1000/fps) if fps > 0 else 33)  # Temps entre chaque frame en ms
    
    # Gestion de la ROI avant toute modification de taille
    if redefine == 'o' or not detector.load_roi():
        detector.select_roi(frame)
    
    # Retourner au début de la vidéo
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Créer la fenêtre principale
    cv2.namedWindow(detector.window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(detector.window_name, 800, 600)  # Taille de fenêtre fixe
    cv2.waitKey(100)
    
    last_time = time.time()
    try:
        while True:
            # Contrôle du framerate
            current_time = time.time()
            elapsed = (current_time - last_time) * 1000
            if elapsed < frame_time:
                delay = max(1, int(frame_time - elapsed))
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    break
                continue
            
            last_time = current_time
            
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            frame = detector.add_instructions(frame)
            is_closed, frame = detector.detect_red(frame)
            
            # Mettre à jour l'état de la pince du robot
            detector.update_gripper_state(is_closed)
            
            cv2.imshow(detector.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                detector.select_roi(frame)
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if detector.robot:
            detector.robot.close_connection()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
