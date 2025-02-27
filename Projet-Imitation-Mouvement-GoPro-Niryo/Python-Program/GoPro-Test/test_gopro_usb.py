import cv2 #Video processing
import json
import requests
import asyncio
from open_gopro import * # GoPro control
#from gpmf_parser import * # GPMF parser for telemetry data
from pyniryo import * # Robot control
import numpy as np # Data processing
import pandas as pd # Data processing

# Additional useful imports from standard library
import time
from pathlib import Path

# Change the serial number to a string
gopro = WiredGoPro("910") # GoPro IUT = "910"

#enable the usb control
gopro.http_command.wired_usb_control(control=1)

async def test_connection():
    try:
        print("🔄 Tentative de connexion à la GoPro...")
        await gopro.open()

         # Add keep alive command
        print("🔄 Setting keep alive...")
        await gopro.http_command.set_keep_alive()
        await asyncio.sleep(1)
        
        # Vérifications de l'état de connexion
        print(f"HTTP connecté: {gopro.is_http_connected}")  # Retiré les ()
        print(f"Client prêt: {gopro.is_open}")             # Retiré les ()
        print(f"GoPro prête: {await gopro.is_ready}")      # Ajout de await ici
        
        # Simple vérification de la connexion
        state = await gopro.http_command.get_camera_state()
        if state:
            print(state)
            print("✅ GoPro connectée avec succès!")
        
        # Attente de l'appui sur une touche pour fermer
        print("\nAppuyez sur Enter pour fermer la connexion...")
        input()
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
    finally:
        print("Fermeture de la connexion...")
        await gopro.close()

if __name__ == "__main__":
    asyncio.run(test_connection())

