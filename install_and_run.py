import subprocess
import sys
import os

def install_requirements():
    try:
        # Instalar dependencias
        print("Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi==0.104.1", "uvicorn[standard]==0.23.2", "pydantic==2.3.0"])
        print("Dependencias instaladas correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias: {e}")
        return False

def run_app():
    try:
        print("Iniciando aplicación...")
        subprocess.check_call([sys.executable, "app.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar la aplicación: {e}")

if __name__ == "__main__":
    if install_requirements():
        run_app()