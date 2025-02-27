import asyncio
from open_gopro import *
import time
import json
import os

async def test_wifi_connection():
    try:
        print("🔄 Initialisation de la connexion WiFi GoPro...")
        # Créer une instance de GoPro (utilise la découverte WiFi)
        gopro = WirelessGoPro(wifi_interface="Xiaomi 13T A", sudo_password="Newton29$")

        gopro.connect_to_access_point("Xiaomi 13T A", "Newton29$")
        
        print("🔍 Recherche de la GoPro...")
        # Tenter la connexion
        await gopro.open()
        
        print("⚡ Configuration du keep-alive...")
        await gopro.http_command.set_keep_alive()
        await asyncio.sleep(1)
        
        # Vérifier l'état de la connexion
        print("\n📊 État de la connexion:")
        print(f"🌐 WiFi connecté: {gopro.is_http_connected}")
        print(f"✨ Client prêt: {gopro.is_open}")
        print(f"📱 GoPro prête: {await gopro.is_ready}")
        
        # Obtenir les informations de la caméra
        print("\n📸 Informations de la caméra:")
        state = await gopro.http_command.get_camera_state()
        print(json.dumps(state, indent=2))
        
        print("\n✅ GoPro connectée avec succès!")
        
        # Maintenir la connexion jusqu'à ce que l'utilisateur décide de la fermer
        print("\n⏳ Appuyez sur Enter pour fermer la connexion...")
        input()
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    finally:
        print("👋 Fermeture de la connexion...")
        await gopro.close()

if __name__ == "__main__":
    # Exécuter la fonction asynchrone
    asyncio.run(test_wifi_connection())
