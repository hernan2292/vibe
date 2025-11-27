#!/usr/bin/env python3
"""
Vibe - Tu programador personal para PHP
Ejecuta: python vibe.py
"""

import ollama
import os
import subprocess
import re
import json
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from typing import List, Dict, Optional
from dataclasses import dataclass

console = Console()
MODEL = os.getenv("VIBE_MODEL", "qwen3-coder:30b")  # Modelo por defecto (cambiado de gpt-oss:20b)

# ═══════════════════════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    content: str
    status: str  # pending, in_progress, completed
    activeForm: str

@dataclass
class ToolResult:
    tool: str
    success: bool
    output: str
    error: Optional[str] = None

# ═══════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════

class Tools:
    """Conjunto de herramientas disponibles para el asistente"""

    @staticmethod
    def bash(command: str, description: str = "") -> ToolResult:
        """Ejecuta un comando bash"""
        try:
            console.print(f"[dim]🔧 {description or command}[/]")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout + result.stderr
            return ToolResult(
                tool="bash",
                success=result.returncode == 0,
                output=output.strip(),
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )
        except subprocess.TimeoutExpired:
            return ToolResult(tool="bash", success=False, output="", error="Timeout (5 min)")
        except Exception as e:
            return ToolResult(tool="bash", success=False, output="", error=str(e))

    @staticmethod
    def read(file_path: str, offset: int = 0, limit: Optional[int] = None) -> ToolResult:
        """Lee un archivo completo o parcial"""
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(tool="read", success=False, output="", error="Archivo no encontrado")

            content = path.read_text(encoding='utf-8')
            lines = content.splitlines()

            if limit:
                lines = lines[offset:offset + limit]

            # Formato con números de línea (estilo cat -n)
            numbered = "\n".join(f"{i+1+offset:6d}\t{line}" for i, line in enumerate(lines))

            return ToolResult(tool="read", success=True, output=numbered)
        except Exception as e:
            return ToolResult(tool="read", success=False, output="", error=str(e))

    @staticmethod
    def write(file_path: str, content: str) -> ToolResult:
        """Escribe un archivo nuevo o sobrescribe existente"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return ToolResult(tool="write", success=True, output=f"Archivo escrito: {file_path}")
        except Exception as e:
            return ToolResult(tool="write", success=False, output="", error=str(e))

    @staticmethod
    def edit(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> ToolResult:
        """Edita un archivo reemplazando texto exacto"""
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(tool="edit", success=False, output="", error="Archivo no encontrado")

            content = path.read_text(encoding='utf-8')

            if not replace_all:
                # Verificar que old_string sea único
                count = content.count(old_string)
                if count == 0:
                    return ToolResult(tool="edit", success=False, output="",
                                    error="old_string no encontrado en el archivo")
                elif count > 1:
                    return ToolResult(tool="edit", success=False, output="",
                                    error=f"old_string encontrado {count} veces. Usa replace_all=True o proporciona más contexto")

                new_content = content.replace(old_string, new_string, 1)
            else:
                new_content = content.replace(old_string, new_string)

            path.write_text(new_content, encoding='utf-8')
            return ToolResult(tool="edit", success=True,
                            output=f"Archivo editado: {file_path}")
        except Exception as e:
            return ToolResult(tool="edit", success=False, output="", error=str(e))

    @staticmethod
    def glob(pattern: str, path: str = ".") -> ToolResult:
        """Busca archivos por patrón glob"""
        try:
            base_path = Path(path)
            matches = sorted(base_path.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

            # Filtrar directorios comunes a ignorar
            ignore = {'.git', '__pycache__', 'node_modules', 'storage', 'vendor', 'bootstrap/cache', '.next', 'dist', 'build'}
            matches = [m for m in matches if not any(ig in m.parts for ig in ignore)]

            output = "\n".join(str(m) for m in matches[:100])  # Limitar a 100 resultados
            return ToolResult(tool="glob", success=True, output=output or "No se encontraron archivos")
        except Exception as e:
            return ToolResult(tool="glob", success=False, output="", error=str(e))

    @staticmethod
    def grep(pattern: str, path: str = ".", glob_pattern: str = "*",
             output_mode: str = "files_with_matches", case_insensitive: bool = False,
             context_lines: int = 0) -> ToolResult:
        """Busca texto en archivos usando regex"""
        try:
            base_path = Path(path)
            matches = []

            ignore = {'.git', '__pycache__', 'node_modules', 'storage', 'vendor', 'bootstrap/cache'}

            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)

            for file_path in base_path.rglob(glob_pattern):
                if not file_path.is_file() or any(ig in file_path.parts for ig in ignore):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')

                    if output_mode == "files_with_matches":
                        if regex.search(content):
                            matches.append(str(file_path))
                    elif output_mode == "content":
                        lines = content.splitlines()
                        for i, line in enumerate(lines, 1):
                            if regex.search(line):
                                context = []
                                if context_lines > 0:
                                    start = max(0, i - 1 - context_lines)
                                    end = min(len(lines), i + context_lines)
                                    context = lines[start:end]
                                    matches.append(f"{file_path}:{i}:\n" + "\n".join(context))
                                else:
                                    matches.append(f"{file_path}:{i}: {line}")
                except:
                    continue

            output = "\n".join(matches[:100]) if matches else "No se encontraron coincidencias"
            return ToolResult(tool="grep", success=True, output=output)
        except Exception as e:
            return ToolResult(tool="grep", success=False, output="", error=str(e))

    @staticmethod
    def list_models() -> ToolResult:
        """Lista los modelos disponibles en Ollama"""
        try:
            models = ollama.list()
            if not models.get('models'):
                return ToolResult(tool="list_models", success=False, output="",
                                error="No hay modelos disponibles en Ollama")

            output_lines = ["Modelos disponibles en Ollama:\n"]
            for model in models['models']:
                name = model.get('name', 'unknown')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                modified = model.get('modified_at', 'unknown')
                output_lines.append(f"  • {name} ({size_gb:.2f} GB) - Modificado: {modified}")

            return ToolResult(tool="list_models", success=True, output="\n".join(output_lines))
        except Exception as e:
            return ToolResult(tool="list_models", success=False, output="",
                            error=f"Error al listar modelos: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# DETECCIÓN DE FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════

def detect_framework() -> Dict[str, any]:
    """Detecta el framework PHP utilizado en el proyecto"""

    framework_info = {
        "name": "Unknown",
        "version": None,
        "features": [],
        "config_files": []
    }

    # Laravel
    if Path("artisan").exists() and Path("composer.json").exists():
        framework_info["name"] = "Laravel"
        try:
            composer = json.loads(Path("composer.json").read_text())
            if "laravel/framework" in composer.get("require", {}):
                framework_info["version"] = composer["require"]["laravel/framework"]
        except:
            pass

        # Detectar características de Laravel
        if Path("routes/web.php").exists():
            framework_info["config_files"].append("routes/web.php")
        if Path("routes/api.php").exists():
            framework_info["config_files"].append("routes/api.php")
        if Path("package.json").exists():
            try:
                pkg = json.loads(Path("package.json").read_text())
                if "livewire" in str(pkg):
                    framework_info["features"].append("Livewire")
                if "@inertiajs" in str(pkg):
                    framework_info["features"].append("Inertia.js")
            except:
                pass

    # Symfony
    elif Path("bin/console").exists() and Path("symfony.lock").exists():
        framework_info["name"] = "Symfony"
        framework_info["config_files"].append("config/routes.yaml")

    # CodeIgniter
    elif Path("system/CodeIgniter.php").exists():
        framework_info["name"] = "CodeIgniter"
        framework_info["config_files"].append("application/config/config.php")

    # CakePHP
    elif Path("bin/cake").exists():
        framework_info["name"] = "CakePHP"

    # Yii
    elif Path("yii").exists():
        framework_info["name"] = "Yii"

    # Slim
    elif Path("composer.json").exists():
        try:
            composer = json.loads(Path("composer.json").read_text())
            if "slim/slim" in composer.get("require", {}):
                framework_info["name"] = "Slim"
        except:
            pass

    return framework_info

# ═══════════════════════════════════════════════════════════════════════════
# GESTOR DE CONTEXTO
# ═══════════════════════════════════════════════════════════════════════════

def get_project_context(framework_info: Dict) -> str:
    """Genera contexto del proyecto basado en el framework detectado"""

    context_parts = []

    # Información del framework
    context_parts.append(f"Framework: {framework_info['name']}")
    if framework_info['version']:
        context_parts.append(f"Versión: {framework_info['version']}")
    if framework_info['features']:
        context_parts.append(f"Características: {', '.join(framework_info['features'])}")

    # Leer archivos clave
    important_files = framework_info.get('config_files', [])

    # Agregar archivos comunes según framework
    if framework_info['name'] == 'Laravel':
        important_files.extend(['composer.json', 'package.json', '.env.example'])

    for file_path in important_files[:5]:  # Limitar a 5 archivos
        path = Path(file_path)
        if path.exists() and path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (truncado)"
                context_parts.append(f"\n--- {file_path} ---\n{content}")
            except:
                pass

    return "\n".join(context_parts)

# ═══════════════════════════════════════════════════════════════════════════
# GESTOR DE TAREAS
# ═══════════════════════════════════════════════════════════════════════════

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, content: str, active_form: str, status: str = "pending"):
        self.tasks.append(Task(content=content, status=status, activeForm=active_form))

    def update_task(self, index: int, status: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].status = status

    def display(self):
        if not self.tasks:
            return

        table = Table(title="📋 Lista de Tareas")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Estado", width=12)
        table.add_column("Tarea")

        status_emoji = {
            "pending": "⏳ Pendiente",
            "in_progress": "🔄 En progreso",
            "completed": "✅ Completado"
        }

        for i, task in enumerate(self.tasks):
            status_display = status_emoji.get(task.status, task.status)
            task_text = task.activeForm if task.status == "in_progress" else task.content
            table.add_row(str(i + 1), status_display, task_text)

        console.print(table)

# ═══════════════════════════════════════════════════════════════════════════
# PARSER DE LLAMADAS A HERRAMIENTAS
# ═══════════════════════════════════════════════════════════════════════════

def parse_tool_calls(text: str) -> List[Dict]:
    """Extrae llamadas a herramientas del texto del asistente"""

    tool_calls = []

    # Eliminar bloques de código markdown que podrían contener ejemplos
    # Esto evita que los ejemplos en código sean parseados como herramientas reales
    text_without_code_blocks = re.sub(r'```[\s\S]*?```', '', text)
    text_without_inline_code = re.sub(r'`[^`]+`', '', text_without_code_blocks)

    # Eliminar tablas markdown que contienen ejemplos
    # Las tablas empiezan con | y contienen líneas con ━ o -
    lines = text_without_inline_code.split('\n')
    filtered_lines = []
    in_table = False

    for line in lines:
        # Detectar inicio/contenido de tabla
        if '|' in line or '━' in line or (in_table and line.strip().startswith('-')):
            in_table = True
            continue
        # Salir de la tabla cuando hay una línea sin | y sin ━
        elif in_table and '|' not in line:
            in_table = False

        if not in_table:
            filtered_lines.append(line)

    filtered_text = '\n'.join(filtered_lines)

    # Patrón mejorado para detectar llamadas a herramientas
    # Formato: TOOL:nombre_herramienta(param1="valor1", param2="valor2")
    # Buscar TOOL:nombre( y luego encontrar el ) correspondiente manejando balance
    tool_pattern = r'TOOL:(\w+)\('

    tool_matches = list(re.finditer(tool_pattern, filtered_text))

    for tool_match in tool_matches:
        tool_name = tool_match.group(1)
        start_pos = tool_match.end()

        # Encontrar el paréntesis de cierre balanceando paréntesis
        paren_count = 1
        end_pos = start_pos
        while end_pos < len(filtered_text) and paren_count > 0:
            if filtered_text[end_pos] == '(':
                paren_count += 1
            elif filtered_text[end_pos] == ')':
                paren_count -= 1
            end_pos += 1

        if paren_count == 0:
            params_str = filtered_text[start_pos:end_pos-1]

            # Parsear parámetros con mejor manejo de comillas
            params = {}

            # Patrón mejorado que maneja strings multi-línea
            param_pattern = r'(\w+)=("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^,)]+)'

            for param_match in re.finditer(param_pattern, params_str):
                key = param_match.group(1)
                value = param_match.group(2).strip()

                # Remover comillas externas
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                    # Decodificar escapes
                    value = value.replace('\\"', '"').replace("\\'", "'").replace('\\n', '\n')

                # Convertir valores booleanos
                if isinstance(value, str):
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False

                params[key] = value

            tool_calls.append({
                "tool": tool_name,
                "params": params
            })

    return tool_calls

def execute_tool(tool_name: str, params: Dict) -> ToolResult:
    """Ejecuta una herramienta con los parámetros dados"""

    tools_map = {
        "bash": Tools.bash,
        "read": Tools.read,
        "write": Tools.write,
        "edit": Tools.edit,
        "glob": Tools.glob,
        "grep": Tools.grep,
        "list_models": Tools.list_models
    }

    if tool_name not in tools_map:
        return ToolResult(tool=tool_name, success=False, output="",
                         error=f"Herramienta desconocida: {tool_name}")

    try:
        return tools_map[tool_name](**params)
    except TypeError as e:
        return ToolResult(tool=tool_name, success=False, output="",
                         error=f"Parámetros incorrectos: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# SISTEMA DE PROMPTS
# ═══════════════════════════════════════════════════════════════════════════

def build_system_prompt(framework_info: Dict, project_context: str) -> str:
    """Construye el prompt del sistema basado en el framework"""

    return f"""Eres VIBE, un asistente experto en Laravel y PHP.

REGLAS CRÍTICAS:
1. SIEMPRE responde con información útil, NUNCA vacío
2. Cuando uses herramientas, COMPLETA la tarea hasta el final
3. Después de RESULTADOS: continúa investigando O da respuesta final
4. Si te preguntan sobre vibe.py: ese es TU código Python, puedes leerlo y modificarlo
5. Puedes trabajar con CUALQUIER archivo del proyecto, no solo Laravel
6. IMPORTANTE: Cuando recibas resultados suficientes, da la RESPUESTA FINAL inmediatamente, NO uses más herramientas innecesarias

Herramientas:
- TOOL:glob(pattern="**/*.php") - buscar archivos
- TOOL:read(file_path="ruta") - leer archivo
- TOOL:grep(pattern="texto", glob_pattern="*.php") - buscar en código
- TOOL:bash(command="cmd") - ejecutar comando
- TOOL:edit(file_path="ruta", old_string="viejo", new_string="nuevo") - editar
- TOOL:write(file_path="ruta", content="...") - crear archivo

Flujo de trabajo:
1. Usa herramientas para investigar (máximo 2-3 herramientas)
2. Recibe resultados
3. ¿Ya tienes suficiente información? → Da respuesta final INMEDIATAMENTE
4. ¿Falta información crítica? → Usa UNA herramienta más

Para CREAR archivos:
- NO uses herramientas para investigar primero
- Usa directamente TOOL:write(file_path="...", content="...") con el contenido completo

Ejemplo 1 (Análisis):
Usuario: ¿Qué versión de Laravel usa el proyecto?
Tú: Voy a revisar composer.json.
TOOL:read(file_path="composer.json")
[Recibes: contenido con "laravel/framework": "^7.0"]
Tú: El proyecto usa **Laravel 7.x** según composer.json.

Ejemplo 2 (Crear archivo):
Usuario: Crea un plan de migración a Laravel 12
Tú: Voy a crear el plan de migración.
TOOL:write(file_path="MIGRACION_LARAVEL12.md", content="# Plan de Migración a Laravel 12\n\n## Versión actual: Laravel 7\n\n...")

Ejemplo 3 (Análisis completo):
Usuario: Analiza AuthController
Tú: Voy a buscar AuthController.
TOOL:glob(pattern="**/AuthController.php")
[Recibes: app/Http/Controllers/Api/V1/AuthController.php]
Tú: Voy a leerlo.
TOOL:read(file_path="app/Http/Controllers/Api/V1/AuthController.php")
[Recibes: contenido del archivo]
Tú: ## Análisis de AuthController

**Problemas encontrados:**
1. Función login() muy larga (200 líneas) - viola Single Responsibility
2. Sin validación con FormRequest
3. Uso de DB::raw() sin binding (línea 45) - vulnerable a SQL injection

**Recomendaciones:**
- Refactorizar login() en métodos más pequeños
- Crear LoginRequest para validación
- Reemplazar DB::raw() con Query Builder
"""

# ═══════════════════════════════════════════════════════════════════════════
# CHAT PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def vibe_chat():
    """Loop principal del chat"""
    global MODEL

    # Banner inicial
    console.print(Panel.fit(
        "[bold cyan]VIBE[/] - Tu Programador Personal para PHP\n"
        f"Modelo: [yellow]{MODEL}[/]",
        border_style="cyan"
    ))

    # Detectar framework
    console.print("\n[dim]Detectando framework...[/]")
    framework_info = detect_framework()

    console.print(f"[green]✓[/] Framework: [bold]{framework_info['name']}[/]")
    if framework_info['features']:
        console.print(f"  Características: {', '.join(framework_info['features'])}")

    # Obtener contexto del proyecto
    project_context = get_project_context(framework_info)

    # Sistema de mensajes
    messages = [
        {
            "role": "system",
            "content": build_system_prompt(framework_info, project_context)
        }
    ]

    # Gestor de tareas
    task_manager = TaskManager()

    console.print("\n[dim]Escribe tu tarea o 'exit' para salir[/]\n")

    while True:
        # Input del usuario
        user_input = console.input("[bold yellow]Tú:[/] ").strip()

        if user_input.lower() in ['exit', 'quit', 'salir']:
            console.print("[red]¡Hasta luego! 👋[/]")
            break

        if not user_input:
            continue

        # Comandos especiales
        if user_input.lower() == '/models':
            try:
                models_list = ollama.list()
                console.print("\n[bold cyan]Modelos disponibles en Ollama:[/]")
                for model in models_list.get('models', []):
                    name = model.get('name', 'unknown')
                    size_gb = model.get('size', 0) / (1024**3)
                    console.print(f"  • {name} ({size_gb:.2f} GB)")
                console.print(f"\n[dim]Modelo actual: {MODEL}[/]")
                console.print("[dim]Cambia con: /model nombre_modelo[/]\n")
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
            continue

        if user_input.lower().startswith('/model '):
            new_model = user_input[7:].strip()
            MODEL = new_model
            console.print(f"[green]✓ Modelo cambiado a: {MODEL}[/]")
            console.print("[yellow]Reinicia la conversación para que surta efecto completo[/]\n")
            continue

        if user_input.lower() == '/help':
            console.print("\n[bold cyan]Comandos especiales:[/]")
            console.print("  /models - Lista modelos disponibles")
            console.print("  /model <nombre> - Cambia de modelo")
            console.print("  /help - Muestra esta ayuda")
            console.print("  exit/quit/salir - Salir\n")
            continue

        # Agregar mensaje del usuario
        messages.append({"role": "user", "content": user_input})

        # Llamar a Ollama
        console.print("\n[bold blue]🤔 Vibe pensando...[/]\n")

        try:
            response = ollama.chat(model=MODEL, messages=messages)
            assistant_msg = response['message']['content']

            # DEBUG: Mostrar respuesta raw si está vacía
            if not assistant_msg.strip():
                console.print(f"[red]DEBUG - Respuesta vacía del modelo[/]")
                console.print(f"[dim]Response completo: {response}[/]")

                # Intentar con un prompt más simple
                console.print("[yellow]Reintentando con prompt simplificado...[/]")
                simple_prompt = f"Responde a esta pregunta sobre Laravel: {user_input}"
                messages[-1] = {"role": "user", "content": simple_prompt}
                response = ollama.chat(model=MODEL, messages=messages)
                assistant_msg = response['message']['content']

            messages.append({"role": "assistant", "content": assistant_msg})

            # Loop de ejecución de herramientas (permite múltiples rondas)
            max_iterations = 20  # Límite de seguridad aumentado
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Parsear y ejecutar herramientas
                tool_calls = parse_tool_calls(assistant_msg)

                # Mostrar respuesta del asistente
                if assistant_msg.strip():
                    console.print("\n[bold green]Vibe:[/]")
                    console.print(Markdown(assistant_msg))
                    console.print()  # Línea en blanco
                else:
                    console.print("[yellow]⚠ El modelo no generó respuesta[/]")
                    break

                # Si no hay herramientas, terminar el loop
                if not tool_calls:
                    break

                # Ejecutar herramientas
                console.print(f"[dim]Ejecutando {len(tool_calls)} herramienta(s)... (iteración {iteration}/{max_iterations})[/]\n")

                results = []
                for call in tool_calls:
                    result = execute_tool(call['tool'], call['params'])
                    results.append(result)

                    # Mostrar resultado
                    if result.success:
                        output_preview = result.output[:200] if len(result.output) > 200 else result.output
                        console.print(f"[green]✓ {result.tool}:[/] {output_preview}")
                    else:
                        console.print(f"[red]✗ {result.tool}:[/] {result.error}")

                # Agregar resultados al contexto
                results_text = "\n\n".join(
                    f"Resultado de {r.tool}:\n{r.output if r.success else f'Error: {r.error}'}"
                    for r in results
                )

                messages.append({
                    "role": "user",
                    "content": f"RESULTADOS DE HERRAMIENTAS:\n{results_text}"
                })

                # Llamar al modelo nuevamente para que procese los resultados
                console.print(f"\n[dim]🤔 Procesando resultados (iteración {iteration})...[/]\n")
                try:
                    response = ollama.chat(model=MODEL, messages=messages)
                    assistant_msg = response['message']['content']

                    if not assistant_msg.strip():
                        console.print("[yellow]⚠ El modelo no generó respuesta después de procesar[/]")
                        break

                    messages.append({"role": "assistant", "content": assistant_msg})
                    # El loop continúa para procesar la nueva respuesta
                except Exception as e:
                    console.print(f"[red]Error al procesar resultados: {e}[/]")
                    break

            if iteration >= max_iterations:
                console.print(f"[yellow]⚠ Se alcanzó el límite de {max_iterations} iteraciones[/]")

            console.print("\n" + "─" * 60 + "\n")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/]")
            console.print("[yellow]¿El modelo está disponible? Verifica con 'ollama list'[/]")
            break

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Verificar que Ollama está disponible
        models = ollama.list()
        if not models.get('models'):
            console.print("[red]No hay modelos disponibles en Ollama.[/]")
            console.print("[yellow]Instala un modelo con: ollama pull qwen2.5-coder:7b[/]")
        else:
            vibe_chat()
    except Exception as e:
        console.print(f"[red]Error al conectar con Ollama: {str(e)}[/]")
        console.print("[yellow]Asegúrate de que Ollama esté corriendo: ollama serve[/]")
