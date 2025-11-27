# VIBE - Tu Programador Personal para PHP

VIBE es un asistente de programación inteligente similar a Claude Code, pero optimizado para proyectos PHP con soporte para múltiples frameworks.

## 🚀 Características

- **Detección automática de frameworks**: Laravel, Symfony, CodeIgniter, CakePHP, Yii, Slim
- **Herramientas avanzadas**: Edición inteligente, búsqueda de código, ejecución de comandos
- **Contexto del proyecto**: Entiende tu proyecto automáticamente
- **Ejecución automática**: No requiere confirmaciones manuales para comandos
- **Interfaz elegante**: Usando Rich para una mejor experiencia visual

## 📋 Requisitos

```bash
pip install ollama rich
```

## 🔧 Instalación

1. Asegúrate de tener Ollama instalado y corriendo:
```bash
ollama serve
```

2. Descarga un modelo de código (recomendado):
```bash
ollama pull qwen2.5-coder:7b
# o
ollama pull deepseek-coder:6.7b
# o
ollama pull codellama:13b
```

3. Opcionalmente, configura el modelo por defecto:
```bash
export VIBE_MODEL="qwen2.5-coder:7b"
```

## 🎯 Uso

```bash
python vibe.py
```

## 🛠️ Herramientas Disponibles

VIBE tiene acceso a las siguientes herramientas que se ejecutan automáticamente:

### 1. **bash** - Ejecutar comandos
```
TOOL:bash(command="php artisan migrate", description="Ejecutar migraciones")
```

### 2. **read** - Leer archivos
```
TOOL:read(file_path="app/Models/User.php")
```

### 3. **write** - Crear archivos nuevos
```
TOOL:write(file_path="app/Services/NewService.php", content="<?php\n...")
```

### 4. **edit** - Editar archivos existentes
```
TOOL:edit(file_path="routes/web.php", old_string="texto_original", new_string="texto_nuevo")
```

### 5. **glob** - Buscar archivos por patrón
```
TOOL:glob(pattern="app/Models/*.php")
```

### 6. **grep** - Buscar en contenido de archivos
```
TOOL:grep(pattern="class User", glob_pattern="**/*.php", output_mode="content")
```

## 💡 Ejemplos de Uso

### Crear un nuevo controlador en Laravel
```
Tú: Crea un controlador para manejar productos con métodos CRUD
```

### Agregar una nueva ruta
```
Tú: Agrega una ruta API para listar usuarios
```

### Buscar código específico
```
Tú: Encuentra todos los modelos que usan SoftDeletes
```

### Ejecutar migraciones
```
Tú: Ejecuta las migraciones pendientes
```

### Refactorizar código
```
Tú: Refactoriza el UserController para usar servicios
```

## 🎨 Frameworks Soportados

- ✅ **Laravel** (con detección de Livewire e Inertia.js)
- ✅ **Symfony**
- ✅ **CodeIgniter**
- ✅ **CakePHP**
- ✅ **Yii**
- ✅ **Slim**
- ✅ Proyectos PHP genéricos

## 🔍 Diferencias con Claude Code

| Característica | VIBE | Claude Code |
|---------------|------|-------------|
| **Lenguaje** | Python | Rust/Node |
| **Enfoque** | PHP/Web | General |
| **Modelo** | Local (Ollama) | Claude API |
| **Costo** | Gratis | Requiere API key |
| **Privacidad** | 100% local | Requiere conexión |
| **Frameworks** | Auto-detección PHP | General |

## ⚙️ Configuración Avanzada

### Cambiar modelo por defecto

Edita la línea 21 en `vibe.py`:
```python
MODEL = os.getenv("VIBE_MODEL", "tu-modelo-preferido")
```

### Ignorar directorios adicionales

Edita las listas `ignore` en las funciones `glob` y `grep` (líneas 141 y 158):
```python
ignore = {'.git', '__pycache__', 'node_modules', 'tu_directorio'}
```

## 🐛 Solución de Problemas

### Error: "No hay modelos disponibles"
```bash
ollama list  # Ver modelos instalados
ollama pull qwen2.5-coder:7b  # Instalar modelo
```

### Error: "Error al conectar con Ollama"
```bash
ollama serve  # Iniciar servidor Ollama
```

### El asistente no usa las herramientas
- Asegúrate de usar un modelo de código (qwen2.5-coder, deepseek-coder, codellama)
- Los modelos más grandes suelen seguir mejor las instrucciones

## 📝 Ejemplo de Sesión Completa

```
VIBE - Tu Programador Personal para PHP
Modelo: qwen2.5-coder:7b

Detectando framework...
✓ Framework: Laravel
  Características: Inertia.js

Escribe tu tarea o 'exit' para salir

Tú: Crea un controlador ProductController con métodos CRUD

🤔 Vibe pensando...

Vibe:
Voy a crear el controlador ProductController con los métodos CRUD básicos.

TOOL:write(file_path="app/Http/Controllers/ProductController.php", content="<?php...")

✓ write: Archivo escrito: app/Http/Controllers/ProductController.php

✅ Controlador creado con éxito.

────────────────────────────────────────────────────────────

Tú: Agrega las rutas correspondientes

🤔 Vibe pensando...

Vibe:
Voy a leer el archivo de rutas y agregar las rutas para el ProductController.

TOOL:read(file_path="routes/web.php")

✓ read: [contenido del archivo]

TOOL:edit(file_path="routes/web.php", old_string="...", new_string="...")

✓ edit: Archivo editado: routes/web.php

✅ Rutas agregadas correctamente.

────────────────────────────────────────────────────────────

Tú: exit

¡Hasta luego! 👋
```

## 🤝 Contribuciones

Este es un proyecto personal, pero las sugerencias son bienvenidas.

## 📄 Licencia

MIT License - Úsalo libremente en tus proyectos.

## 🎯 Roadmap

- [ ] Soporte para más frameworks (Express.js, Django, etc.)
- [ ] Sistema de plugins
- [ ] Modo batch para procesar múltiples tareas
- [ ] Integración con Git
- [ ] Historial de conversaciones persistente
- [ ] Modo de depuración avanzado
- [ ] Soporte para pruebas automatizadas

---

**Hecho con ❤️ para desarrolladores PHP**
