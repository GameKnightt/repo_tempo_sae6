import cv2 #Video processing
import json
import requests
import asyncio
from open_gopro import * # GoPro control
from pyniryo import * # Robot control
import numpy as np # Data processing
import pandas as pd # Data processing

# Additional useful imports from standard library
import time
from pathlib import Path
from datetime import datetime

# Change the serial number to a string
gopro = WiredGoPro("910")

async def take_photo():
    try:
        print("🔄 Connecting to GoPro...")
        await gopro.open()
        await asyncio.sleep(2)

        # Add keep alive command
        print("🔄 Setting keep alive...")
        await gopro.http_command.set_keep_alive()
        await asyncio.sleep(1)

        # Enable USB control with direct value (1 = enable)
        print("🔌 Disabling USB control...")
        await gopro.http_command.wired_usb_control(control=0)
        print("🔌 Enabling USB control...")
        await gopro.http_command.wired_usb_control(control=1)
        
        # Configure camera for photo mode
        print("📸 Setting up photo mode...")
        await asyncio.sleep(1)
        
        # Take the photo
        print("📸 Taking photo...")
        await gopro.http_command.set_shutter(shutter=True)
        await asyncio.sleep(2)  # Wait for photo to be taken
        await gopro.http_command.set_shutter(shutter=False)
        
        # Get the last media info
        media_response = await gopro.http_command.get_media_list()
        # Accéder aux données réelles contenues dans la réponse
        media_list = media_response.data
        if media_list and len(media_list) > 0:
            last_photo = media_list[-1]
            print(f"✅ Photo taken successfully! File: {last_photo}")
        else:
            print("⚠️ No media found after capture")

    except Exception as e:
        print(f"❌ Error taking photo: {str(e)}")
    finally:
        await gopro.close()
        print("📤 Connection closed")

if __name__ == "__main__":
    asyncio.run(take_photo())

