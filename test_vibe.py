#!/usr/bin/env python3
"""
Script de prueba para verificar que VIBE funciona correctamente
Ejecuta: python test_vibe.py
"""

import sys
from pathlib import Path

def test_imports():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")

    try:
        import ollama
        print("  ✅ ollama")
    except ImportError:
        print("  ❌ ollama - Instala con: pip install ollama")
        return False

    try:
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.table import Table
        from rich.panel import Panel
        print("  ✅ rich")
    except ImportError:
        print("  ❌ rich - Instala con: pip install rich")
        return False

    return True

def test_ollama_connection():
    """Verifica la conexión con Ollama"""
    print("\n🔍 Verificando conexión con Ollama...")

    try:
        import ollama
        models = ollama.list()

        if not models.get('models'):
            print("  ⚠️  Ollama está corriendo pero no hay modelos instalados")
            print("     Instala un modelo con: ollama pull qwen2.5-coder:7b")
            return False

        print("  ✅ Ollama está corriendo")
        print(f"     Modelos disponibles: {len(models['models'])}")

        # for model in models['models']:
        #     print(f"       - {model['NAME']}")

        return True

    except Exception as e:
        print(f"  ❌ Error al conectar con Ollama: {e}")
        print("     Asegúrate de que Ollama esté corriendo: ollama serve")
        return False

def test_tools():
    """Verifica que las herramientas funcionen correctamente"""
    print("\n🔍 Verificando herramientas...")

    # Importar el módulo vibe
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from vibe import Tools, ToolResult
        print("  ✅ Módulo vibe importado correctamente")
    except Exception as e:
        print(f"  ❌ Error al importar vibe: {e}")
        return False

    # Test bash
    try:
        result = Tools.bash("echo test", "Prueba de comando")
        if result.success and "test" in result.output:
            print("  ✅ Herramienta bash")
        else:
            print(f"  ❌ Herramienta bash - {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Herramienta bash - {e}")
        return False

    # Test write y read
    try:
        test_file = Path("test_vibe_temp.txt")
        test_content = "Test content"

        # Write
        write_result = Tools.write(str(test_file), test_content)
        if not write_result.success:
            print(f"  ❌ Herramienta write - {write_result.error}")
            return False

        # Read
        read_result = Tools.read(str(test_file))
        if read_result.success and test_content in read_result.output:
            print("  ✅ Herramientas write y read")
        else:
            print(f"  ❌ Herramienta read - {read_result.error}")
            return False

        # Edit
        edit_result = Tools.edit(str(test_file), "Test", "Modified")
        if edit_result.success:
            verify_result = Tools.read(str(test_file))
            if "Modified" in verify_result.output:
                print("  ✅ Herramienta edit")
            else:
                print("  ❌ Herramienta edit - No se aplicó el cambio")
                return False
        else:
            print(f"  ❌ Herramienta edit - {edit_result.error}")
            return False

        # Cleanup
        test_file.unlink()

    except Exception as e:
        print(f"  ❌ Herramientas de archivo - {e}")
        return False

    # Test glob
    try:
        glob_result = Tools.glob("*.py")
        if glob_result.success and "vibe.py" in glob_result.output:
            print("  ✅ Herramienta glob")
        else:
            print(f"  ❌ Herramienta glob - {glob_result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Herramienta glob - {e}")
        return False

    # Test grep
    try:
        grep_result = Tools.grep(pattern="def test_", glob_pattern="test_vibe.py",
                                output_mode="files_with_matches")
        if grep_result.success:
            print("  ✅ Herramienta grep")
        else:
            print(f"  ❌ Herramienta grep - {grep_result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Herramienta grep - {e}")
        return False

    return True

def test_framework_detection():
    """Verifica la detección de frameworks"""
    print("\n🔍 Verificando detección de frameworks...")

    try:
        from vibe import detect_framework

        framework_info = detect_framework()
        print(f"  ✅ Framework detectado: {framework_info['name']}")

        if framework_info['features']:
            print(f"     Características: {', '.join(framework_info['features'])}")

        return True

    except Exception as e:
        print(f"  ❌ Error en detección de frameworks: {e}")
        return False

def test_tool_parser():
    """Verifica el parser de llamadas a herramientas"""
    print("\n🔍 Verificando parser de herramientas...")

    try:
        from vibe import parse_tool_calls

        test_text = """
        Voy a ejecutar algunos comandos.

        TOOL:bash(command="ls -la", description="Listar archivos")

        TOOL:read(file_path="vibe.py")

        TOOL:edit(file_path="test.php", old_string="old", new_string="new", replace_all=true)
        """

        calls = parse_tool_calls(test_text)

        if len(calls) == 3:
            print(f"  ✅ Parser detectó {len(calls)} llamadas correctamente")

            # Verificar primera llamada
            if calls[0]['tool'] == 'bash' and 'command' in calls[0]['params']:
                print("     ✓ Llamada bash parseada correctamente")

            # Verificar segunda llamada
            if calls[1]['tool'] == 'read' and 'file_path' in calls[1]['params']:
                print("     ✓ Llamada read parseada correctamente")

            # Verificar tercera llamada
            if calls[2]['tool'] == 'edit' and calls[2]['params'].get('replace_all') == True:
                print("     ✓ Llamada edit parseada correctamente (incluyendo boolean)")

            return True
        else:
            print(f"  ❌ Parser detectó {len(calls)} llamadas, se esperaban 3")
            return False

    except Exception as e:
        print(f"  ❌ Error en parser: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("═" * 60)
    print("VIBE - Test Suite")
    print("═" * 60)

    results = []

    # Ejecutar pruebas
    results.append(("Dependencias", test_imports()))
    results.append(("Conexión Ollama", test_ollama_connection()))
    results.append(("Herramientas", test_tools()))
    results.append(("Detección Framework", test_framework_detection()))
    results.append(("Parser", test_tool_parser()))

    # Resumen
    print("\n" + "═" * 60)
    print("RESUMEN")
    print("═" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "─" * 60)
    print(f"Resultados: {passed}/{total} pruebas pasaron")
    print("─" * 60)

    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! VIBE está listo para usar.")
        print("\nEjecuta: python vibe.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
