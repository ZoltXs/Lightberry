#!/usr/bin/env python3
"""
LightBerry OS - Modo Kiosk
Script alternativo para ejecutar en modo kiosk completo
"""

import subprocess
import sys
import os
import time

def setup_kiosk_mode():
    """Configurar modo kiosk"""
    try:
        # Desactivar screensaver
        subprocess.run(['xset', 's', 'off'], check=False)
        subprocess.run(['xset', '-dpms'], check=False)
        subprocess.run(['xset', 's', 'noblank'], check=False)
        
        # Ocultar cursor
        subprocess.run(['unclutter', '-idle', '0.5', '-root'], check=False)
        
        print("Modo kiosk configurado")
        return True
    except Exception as e:
        print(f"Error configurando kiosk: {e}")
        return False

def launch_app():
    """Lanzar aplicación principal"""
    try:
        # Cambiar al directorio de la aplicación
        app_dir = os.path.expanduser("~/lightberry-os")
        if os.path.exists(app_dir):
            os.chdir(app_dir)
        
        # Ejecutar aplicación principal
        subprocess.run([sys.executable, "light_phone_os.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando aplicación: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Archivo light_phone_os.py no encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

def main():
    """Función principal del modo kiosk"""
    print("Iniciando LightBerry OS en modo kiosk...")
    
    # Esperar a que X se estabilice
    time.sleep(2)
    
    # Configurar modo kiosk
    if setup_kiosk_mode():
        print("Configuración kiosk exitosa")
    else:
        print("Advertencia: Configuración kiosk falló")
    
    # Lanzar aplicación
    launch_app()

if __name__ == "__main__":
    main()
