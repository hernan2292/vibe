import subprocess
import sys
import os

def setup_environment():
    try:
        # Crear entorno virtual si no existe
        if not os.path.exists('venv'):
            print('Creando entorno virtual...')
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Instalar dependencias
        print('Instalando dependencias...')
        if sys.platform.startswith('win'):
            pip_path = 'venv\\Scripts\\pip'
        else:
            pip_path = 'venv/bin/pip'
        
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print('Dependencias instaladas correctamente')
        
    except subprocess.CalledProcessError as e:
        print(f'Error al instalar dependencias: {e}')
        return False
    
    return True

def run_app():
    try:
        print('Iniciando aplicación...')
        if sys.platform.startswith('win'):
            python_path = 'venv\\Scripts\\python'
        else:
            python_path = 'venv/bin/python'
        
        subprocess.run([python_path, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error al ejecutar la aplicación: {e}')

if __name__ == '__main__':
    if setup_environment():
        run_app()