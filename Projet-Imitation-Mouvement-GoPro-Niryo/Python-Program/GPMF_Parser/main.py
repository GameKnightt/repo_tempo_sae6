import os
import sys
from gpmf2json import process_video_to_json
from IMU_parser import get_gyro_accel_data, reorder_data
from adapt_json_niryo import convert_to_robot_format, save_movements_to_json

def display_intro():
    """Display the project introduction and wait for user input"""
    # Lire et afficher le contenu du fichier SAE-6.txt
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sae-6.txt'), 'r') as f:
            print(f.read())
    except Exception as e:
        print("Erreur lors de la lecture du fichier sae-6.txt:", str(e))

    # Afficher la description du projet
    print("\n" + "="*80)
    print(" "*30 + "🤖 Projet SAE-6 GEII 🤖")
    print("="*80)
    print("""
Description du Projet:
---------------------
Ce programme permet d'analyser les mouvements capturés par une GoPro et de les reproduire
avec un robot Niryo. Il fait partie du projet final de BUT GEII à l'IUT de Nantes.

Développé par:
-------------
👨‍💻 Alexy LESAULNIER
👨‍💻 Kylian MOURGUES

Fonctionnalités:
---------------
1. Extraction des données IMU depuis les fichiers GoPro
2. Traitement et analyse des mouvements
3. Conversion en commandes pour le robot Niryo
    """)
    print("="*80)
    input("\n🚀 Appuyez sur ENTER pour démarrer l'analyse de la vidéo...")
    print("\n")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    base_dir = os.path.dirname(__file__)
    directories = [
        "1-IMU-Json-Extract",
        "2-Reorder-IMU-Data",
        "3-Json-adapt-niryo-movement"
    ]
    created_dirs = {}
    for dir_name in directories:
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        created_dirs[dir_name] = dir_path
    return created_dirs

def process_gopro_video(video_path, output_path=None):
    """
    Traitement complet d'une vidéo GoPro.
    
    Étapes:
    1. Extraction des données GPMF de la vidéo
    2. Traitement des données IMU (accéléromètre et gyroscope)
    3. Conversion en mouvements robot
    4. Sauvegarde des résultats
    """
    try:
        print("\n=== 🎥 Starting Video Processing ===")
        print(f"📽️ Processing video: {os.path.basename(video_path)}")
        
        # Ensure all directories exist
        print("📁 Creating necessary directories...")
        dirs = ensure_directories()
        print("✅ Directories created successfully")
        
        # Step 1: Extract GPMF data to JSON
        print("\n=== 📊 Step 1: Extracting GPMF data ===")
        if output_path is None:
            output_path = os.path.join(
                dirs["1-IMU-Json-Extract"],
                os.path.splitext(os.path.basename(video_path))[0] + ".json"
            )
        
        print(f"⚡ Extracting data from {os.path.basename(video_path)}...")
        json_files = process_video_to_json(video_path, output_path)
        print(f"✅ GPMF data extracted successfully to {len(json_files)} files:")
        for f in json_files:
            print(f"  📄 {os.path.basename(f)}")
        
        # Step 2: Process each extracted JSON file
        print("\n=== 🔄 Step 2: Processing IMU data ===")
        for json_file in json_files:
            print(f"\n📝 Processing IMU file: {os.path.basename(json_file)}")
            print("📊 Reading and parsing IMU data...")
            imu_data = get_gyro_accel_data(json_file)
            base_filename = os.path.basename(json_file)
            print("💾 Reordering and saving processed data...")
            reordered_data = reorder_data(imu_data, base_filename)
            
            # Step 3: Convert to Niryo format
            print("\n=== 🤖 Step 3: Converting to Niryo format ===")
            print("🔄 Converting data to robot movements...")
            movements = convert_to_robot_format(reordered_data)
            print("💾 Saving robot movements data...")
            save_movements_to_json(movements, base_filename)
        
        print("\n=== ✨ Processing Complete ===")
        print("🎉 All steps completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: An error occurred during processing:")
        print(f"  ⚠️ {str(e)}")
        return False

def process_directory(input_dir):
    """Process all GoPro videos in a directory"""
    print(f"\n=== 📁 Processing Directory: {input_dir} ===")
    success_count = 0
    failed_count = 0
    total_files = len([f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mov'))])
    current_file = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.mp4', '.mov')):
            current_file += 1
            video_path = os.path.join(input_dir, filename)
            print(f"\n🎥 Processing video {current_file}/{total_files}: {filename}")
            if process_gopro_video(video_path):
                success_count += 1
            else:
                failed_count += 1
    
    print("\n=== 📊 Directory Processing Complete ===")
    print(f"📈 Total files processed: {total_files}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    return success_count, failed_count

def get_videos_directory():
    """Return the absolute path to the videos directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(script_dir, "videos")
    
    # Vérifier si le dossier existe
    if not os.path.exists(videos_dir):
        try:
            os.makedirs(videos_dir)
            print(f"\n📁 Nouveau dossier 'videos' créé à : {videos_dir}")
            print("➡️ Veuillez y placer vos fichiers vidéo GoPro et relancer le programme.")
            sys.exit(1)
        except PermissionError:
            print(f"\n❌ Erreur: Impossible de créer le dossier 'videos' à : {videos_dir}")
            print("➡️ Vérifiez vos permissions et réessayez.")
            sys.exit(1)
    
    # Vérifier les permissions
    if not os.access(videos_dir, os.R_OK):
        print(f"\n❌ Erreur: Impossible de lire le dossier 'videos' à : {videos_dir}")
        print("➡️ Vérifiez vos permissions et réessayez.")
        sys.exit(1)
    
    return videos_dir

def select_video(input_dir):
    """
    Interface utilisateur pour la sélection de la vidéo à traiter.
    Affiche la liste des vidéos disponibles et permet à l'utilisateur de choisir.
    """
    # Vérifier si le dossier est accessible
    if not os.path.exists(input_dir):
        print(f"\n❌ Erreur: Le dossier {input_dir} n'existe pas.")
        return None
    
    # Obtenir la liste des vidéos avec vérification des extensions
    videos = []
    try:
        for f in os.listdir(input_dir):
            if f.lower().endswith(('.mp4', '.mov')):
                full_path = os.path.join(input_dir, f)
                if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                    videos.append(f)
    except PermissionError:
        print(f"\n❌ Erreur: Impossible d'accéder au dossier {input_dir}")
        return None
    
    if not videos:
        print(f"\n⚠️ Aucune vidéo MP4/MOV trouvée dans: {input_dir}")
        print("➡️ Veuillez ajouter des vidéos et réessayer.")
        return None
    
    print("\n=== Vidéos disponibles ===")
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video}")
    
    while True:
        try:
            choice = input("\nChoisissez le numéro de la vidéo à analyser (ou 'q' pour quitter) : ")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(videos):
                return os.path.join(input_dir, videos[index])
            else:
                print("Choix invalide. Veuillez réessayer.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    # Afficher l'introduction avant de commencer
    display_intro()
    
    if len(sys.argv) > 1:
        input_path = os.path.abspath(sys.argv[1])
    else:
        # Utiliser la nouvelle fonction pour obtenir le chemin du dossier videos
        input_path = get_videos_directory()
    
    if os.path.isdir(input_path):
        selected_video = select_video(input_path)
        if selected_video:
            process_gopro_video(selected_video)
        else:
            print("\n👋 Programme terminé.")
    elif os.path.isfile(input_path):
        process_gopro_video(input_path)
    else:
        print(f"\n❌ Erreur : {input_path} n'est pas un fichier ou dossier valide")
        print("\n💡 Utilisation : python main.py [video_file_or_directory]")
        print("   ou placez simplement vos vidéos dans le dossier 'videos'")
