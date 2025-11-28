# Ejemplos de Uso de VIBE

Este documento contiene ejemplos de cómo interactuar con VIBE para diferentes tareas comunes.

## 📋 Ejemplos Básicos

### 1. Crear un Modelo en Laravel

**Usuario:**
```
Crea un modelo Product con migración que tenga: name, description, price, stock
```

**VIBE debería responder:**
```
Voy a crear el modelo Product con su migración.

TOOL:bash(command="php artisan make:model Product -m", description="Crear modelo y migración")

TOOL:read(file_path="database/migrations/xxxx_create_products_table.php")

TOOL:edit(file_path="database/migrations/xxxx_create_products_table.php",
    old_string="Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->timestamps();
        });",
    new_string="Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('description')->nullable();
            $table->decimal('price', 10, 2);
            $table->integer('stock')->default(0);
            $table->timestamps();
        });")

✅ Modelo y migración creados correctamente.
```

### 2. Buscar Código Específico

**Usuario:**
```
Muéstrame todos los controladores que tienen el método store
```

**VIBE debería responder:**
```
Voy a buscar controladores con el método store.

TOOL:grep(pattern="function store", glob_pattern="**/*Controller.php", output_mode="files_with_matches")

Encontrados los siguientes controladores:
- app/Http/Controllers/UserController.php
- app/Http/Controllers/ProductController.php
- app/Http/Controllers/OrderController.php
```

### 3. Agregar una Nueva Ruta

**Usuario:**
```
Agrega una ruta GET para /dashboard que use DashboardController@index
```

**VIBE debería responder:**
```
Voy a agregar la ruta al archivo web.php.

TOOL:read(file_path="routes/web.php")

TOOL:edit(file_path="routes/web.php",
    old_string="Route::get('/', function () {
    return view('welcome');
});",
    new_string="Route::get('/', function () {
    return view('welcome');
});

Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');")

✅ Ruta agregada correctamente.
```

### 4. Refactorizar Código

**Usuario:**
```
Refactoriza UserController para mover la lógica de creación de usuarios a un servicio
```

**VIBE debería responder:**
```
Voy a crear un UserService y refactorizar el controlador.

TOOL:write(file_path="app/Services/UserService.php", content="<?php

namespace App\\Services;

use App\\Models\\User;
use Illuminate\\Support\\Facades\\Hash;

class UserService
{
    public function createUser(array $data): User
    {
        return User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
        ]);
    }
}")

TOOL:read(file_path="app/Http/Controllers/UserController.php")

TOOL:edit(file_path="app/Http/Controllers/UserController.php",
    old_string="public function store(Request $request)
    {
        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
        ]);

        return redirect()->route('users.index');
    }",
    new_string="public function store(Request $request, UserService $userService)
    {
        $userService->createUser($request->validated());

        return redirect()->route('users.index');
    }")

✅ Código refactorizado con éxito.
```

### 5. Ejecutar Tests

**Usuario:**
```
Ejecuta los tests y muéstrame los resultados
```

**VIBE debería responder:**
```
Voy a ejecutar los tests de PHPUnit.

TOOL:bash(command="php artisan test", description="Ejecutar tests")

[Resultados de los tests...]
```

## 🔍 Ejemplos Avanzados

### 1. Implementar una Feature Completa

**Usuario:**
```
Implementa un sistema de comentarios para productos: modelo, migración, controlador y rutas
```

**VIBE debería:**
1. Crear el modelo Comment con migración
2. Establecer relaciones en el modelo Product
3. Crear CommentController
4. Agregar rutas API
5. Ejecutar la migración

### 2. Análisis de Código

**Usuario:**
```
Analiza el código de UserController y sugiere mejoras
```

**VIBE debería:**
1. Leer el archivo UserController
2. Identificar problemas (validación, seguridad, etc.)
3. Sugerir mejoras específicas
4. Opcionalmente aplicar las mejoras

### 3. Debugging

**Usuario:**
```
Tengo un error en ProductController línea 45, ayúdame a solucionarlo
```

**VIBE debería:**
1. Leer el archivo ProductController
2. Analizar el código alrededor de la línea 45
3. Identificar el problema
4. Proponer y aplicar la solución

## 🎯 Tips para Mejores Resultados

### ✅ Buenas Prácticas

1. **Sé específico:**
   - ❌ "Crea un controlador"
   - ✅ "Crea un ProductController con métodos index, show, store, update y destroy"

2. **Proporciona contexto:**
   - ❌ "Agrega validación"
   - ✅ "Agrega validación al método store de ProductController para name (required), price (numeric, min:0)"

3. **Indica el framework si no es Laravel:**
   - ✅ "Usando Symfony, crea una nueva entidad User"

4. **Pide revisión de código:**
   - ✅ "Lee ProductController y busca posibles problemas de seguridad"

### ❌ Qué Evitar

1. **No uses comandos destructivos sin confirmar:**
   - ❌ "Elimina todos los archivos de migración"
   - ✅ "Muéstrame las migraciones antiguas antes de eliminarlas"

2. **No pidas cambios masivos sin contexto:**
   - ❌ "Cambia todos los controladores"
   - ✅ "Actualiza UserController para usar inyección de dependencias"

3. **No asumas que VIBE conoce tu proyecto:**
   - ❌ "Arregla ese bug"
   - ✅ "Tengo un error en app/Services/PaymentService.php línea 23, ayúdame"

## 🚀 Casos de Uso Reales

### Caso 1: Setup Inicial de Proyecto

```
Tú: Configura un proyecto Laravel con autenticación usando Breeze
VIBE: [instala breeze, configura, ejecuta migraciones]

Tú: Crea modelos para: Category, Product, Order, OrderItem con sus relaciones
VIBE: [crea modelos, migraciones y relaciones]

Tú: Genera seeders con datos de prueba
VIBE: [crea seeders y ejecuta]
```

### Caso 2: Implementar API REST

```
Tú: Crea una API REST completa para Product con autenticación Sanctum
VIBE: [crea controlador API, rutas, middleware, recursos]

Tú: Agrega paginación y filtros a la lista de productos
VIBE: [modifica el método index]

Tú: Documenta los endpoints en un archivo
VIBE: [crea documentación]
```

### Caso 3: Debugging y Optimización

```
Tú: Analiza ProductController y busca N+1 queries
VIBE: [lee código, identifica problemas, sugiere eager loading]

Tú: Aplica las mejoras sugeridas
VIBE: [modifica código]

Tú: Agrega caché a las consultas más frecuentes
VIBE: [implementa caché]
```

## 📚 Comandos Útiles de Laravel

Estos son comandos que puedes pedirle a VIBE que ejecute:

```bash
# Crear recursos
php artisan make:model Product -mcr
php artisan make:controller ProductController --resource
php artisan make:migration create_products_table
php artisan make:seeder ProductSeeder
php artisan make:request StoreProductRequest

# Ejecutar
php artisan migrate
php artisan db:seed
php artisan serve

# Caché y optimización
php artisan cache:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Testing
php artisan test
php artisan test --filter ProductTest

# Otros
php artisan route:list
php artisan tinker
php artisan queue:work
```

## 🎓 Entrenando al Modelo

Si el modelo no está usando las herramientas correctamente, puedes entrenarlo con ejemplos:

**Usuario:**
```
Cuando te pida crear un archivo, usa: TOOL:write(file_path="ruta", content="contenido")
Cuando te pida editar, primero usa: TOOL:read(file_path="ruta") y luego TOOL:edit(...)
```

## 💡 Ideas para Experimentar

1. **Generación de código:**
   - "Genera un CRUD completo para un blog"
   - "Crea un sistema de roles y permisos"

2. **Refactoring:**
   - "Convierte este controlador a usar repositorios"
   - "Implementa el patrón Service para la lógica de negocio"

3. **Testing:**
   - "Crea tests unitarios para UserService"
   - "Genera factories para todos los modelos"

4. **Documentación:**
   - "Documenta todos los métodos de ProductController"
   - "Crea un README para este módulo"

## 🐍 Ejemplos con Python

### 1. Crear una API con FastAPI

**Usuario:**
```
Crea una API FastAPI con un endpoint para listar usuarios
```

**VIBE debería responder:**
```
Voy a crear la API con FastAPI.

TOOL:write(file_path="main.py", content="from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

users_db = [
    User(id=1, name=\"Juan\", email=\"juan@example.com\"),
    User(id=2, name=\"María\", email=\"maria@example.com\"),
]

@app.get(\"/users\", response_model=List[User])
async def get_users():
    return users_db
")

✅ API creada correctamente. Ejecuta con: uvicorn main:app --reload
```

### 2. Crear un Modelo Django

**Usuario:**
```
Crea un modelo Product en Django con name, price y stock
```

**VIBE debería responder:**
```
Voy a buscar el archivo models.py.

TOOL:glob(pattern="**/models.py")

TOOL:read(file_path="app/models.py")

TOOL:edit(file_path="app/models.py",
    old_string="from django.db import models",
    new_string="from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name")

✅ Modelo creado. Ejecuta: python manage.py makemigrations
```

### 3. Crear Tests con Pytest

**Usuario:**
```
Crea tests para la función calculate_total en utils.py
```

**VIBE debería responder:**
```
Voy a crear el archivo de tests.

TOOL:write(file_path="test_utils.py", content="import pytest
from utils import calculate_total

def test_calculate_total_with_items():
    items = [10, 20, 30]
    assert calculate_total(items) == 60

def test_calculate_total_empty():
    assert calculate_total([]) == 0

def test_calculate_total_negative():
    items = [-10, 20]
    assert calculate_total(items) == 10
")

✅ Tests creados. Ejecuta con: pytest test_utils.py
```

---

**¡Experimenta y descubre todo lo que VIBE puede hacer por ti!**

