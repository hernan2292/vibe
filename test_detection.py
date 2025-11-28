#!/usr/bin/env python3
"""
Test de detección de frameworks para VIBE
"""

from vibe import detect_framework
from pathlib import Path
import tempfile
import os

def test_python_detection():
    """Prueba la detección de proyectos Python"""
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Test 1: Proyecto Python genérico (archivos .py)
            Path("main.py").write_text("print('hello')")
            info = detect_framework()
            assert info['name'] == 'Python Script'
            assert info['language'] == 'Python'
            print("✅ Test 1: Python Script detectado correctamente")
            
            # Test 2: Proyecto con requirements.txt
            Path("requirements.txt").write_text("fastapi==0.104.1\nuvicorn")
            info = detect_framework()
            assert info['name'] == 'FastAPI'
            assert info['language'] == 'Python'
            print("✅ Test 2: FastAPI detectado correctamente")
            
            # Limpiar para siguiente test
            Path("requirements.txt").unlink()
            
            # Test 3: Proyecto Flask
            Path("requirements.txt").write_text("flask==2.3.0")
            info = detect_framework()
            assert info['name'] == 'Flask'
            assert info['language'] == 'Python'
            print("✅ Test 3: Flask detectado correctamente")
            
            # Limpiar
            Path("requirements.txt").unlink()
            
            # Test 4: Proyecto Django
            Path("manage.py").write_text("#!/usr/bin/env python\nimport django")
            info = detect_framework()
            assert info['name'] == 'Django'
            assert info['language'] == 'Python'
            print("✅ Test 4: Django detectado correctamente")
            
        finally:
            os.chdir(original_dir)

def test_php_detection():
    """Prueba que la detección de PHP sigue funcionando"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Test Laravel
            Path("artisan").write_text("#!/usr/bin/env php")
            Path("composer.json").write_text('{"require": {"laravel/framework": "^10.0"}}')
            info = detect_framework()
            assert info['name'] == 'Laravel'
            assert info['language'] == 'PHP'
            print("✅ Test 5: Laravel detectado correctamente")
            
        finally:
            os.chdir(original_dir)

if __name__ == "__main__":
    print("🧪 Ejecutando tests de detección de frameworks...\n")
    test_python_detection()
    test_php_detection()
    print("\n✅ Todos los tests pasaron correctamente!")
