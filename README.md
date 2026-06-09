# API de Gestión de Tareas

API REST para gestionar tareas construida con **FastAPI** y **SQLAlchemy**. Permite crear, consultar, actualizar y eliminar tareas. Cada tarea tiene un identificador, título, descripción opcional, categoría opcional, estado (`pending`, `in_progress`, `done`) y fecha de creación automática.

---

## Requisitos previos

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.12+         |
| pip       | 23+           |

### Dependencias principales

| Paquete     | Versión  | Descripción                          |
|-------------|----------|--------------------------------------|
| FastAPI     | 0.136.1  | Framework web asíncrono              |
| SQLAlchemy  | 2.0.49   | ORM para acceso a base de datos      |
| Pydantic    | 2.13.4   | Validación de datos                  |
| Uvicorn     | 0.46.0   | Servidor ASGI                        |
| pytest      | 9.0.3    | Framework de tests                   |
| httpx       | 0.28.1   | Cliente HTTP para tests de FastAPI   |

---

## Instalación paso a paso

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/dgarciap88/gestor-tareas-api.git
   cd gestor-tareas-api
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv

   # Linux / macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Cómo arrancar la aplicación

```bash
uvicorn aplicacion.principal:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

La documentación interactiva (Swagger UI) se encuentra en `http://127.0.0.1:8000/docs`.

---

## Endpoints

La API expone seis endpoints bajo el prefijo `/tasks`. Todos aceptan y devuelven JSON.

### Modelo de respuesta (`TaskResponse`)

```json
{
  "id": 1,
  "title": "Revisar código",
  "description": "Revisar el PR #10",
  "categoria": null,
  "status": "pending",
  "created_at": "2025-05-28T14:00:00"
}
```

Los valores válidos para `status` son: `pending`, `in_progress`, `done`.

---

### 1. Listar todas las tareas

| Campo  | Valor            |
|--------|------------------|
| Método | `GET`            |
| Ruta   | `/tasks/`        |

**Parámetros:** ninguno.

**Ejemplo de petición:**

```bash
curl http://127.0.0.1:8000/tasks/
```

**Ejemplo de respuesta** (`200 OK`):

```json
[
  {
    "id": 1,
    "title": "Revisar código",
    "description": "Revisar el PR #10",
    "categoria": null,
    "status": "pending",
    "created_at": "2025-05-28T14:00:00"
  }
]
```

---

### 2. Contar tareas

| Campo  | Valor            |
|--------|------------------|
| Método | `GET`            |
| Ruta   | `/tasks/count`   |

**Parámetros:** ninguno.

**Ejemplo de petición:**

```bash
curl http://127.0.0.1:8000/tasks/count
```

**Ejemplo de respuesta** (`200 OK`):

```json
{
  "count": 5
}
```

---

### 3. Obtener una tarea por id

| Campo  | Valor              |
|--------|--------------------|
| Método | `GET`              |
| Ruta   | `/tasks/{task_id}` |

**Parámetros de ruta:**

| Parámetro | Tipo  | Descripción                  |
|-----------|-------|------------------------------|
| `task_id` | `int` | Identificador de la tarea    |

**Ejemplo de petición:**

```bash
curl http://127.0.0.1:8000/tasks/1
```

**Ejemplo de respuesta** (`200 OK`):

```json
{
  "id": 1,
  "title": "Revisar código",
  "description": "Revisar el PR #10",
  "categoria": null,
  "status": "pending",
  "created_at": "2025-05-28T14:00:00"
}
```

**Error** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

---

### 4. Crear una nueva tarea

| Campo  | Valor    |
|--------|----------|
| Método | `POST`   |
| Ruta   | `/tasks/`|

**Cuerpo de la petición (`TaskCreate`):**

| Campo         | Tipo     | Obligatorio | Valor por defecto | Descripción               |
|---------------|----------|-------------|-------------------|---------------------------|
| `title`       | `string` | Sí          | —                 | Título de la tarea        |
| `description` | `string` | No          | `null`            | Descripción opcional      |
| `categoria`   | `string` | No          | `null`            | Categoría de la tarea     |
| `status`      | `string` | No          | `"pending"`       | Estado inicial            |

**Ejemplo de petición:**

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Escribir tests", "description": "Cubrir los endpoints CRUD"}'
```

**Ejemplo de respuesta** (`201 Created`):

```json
{
  "id": 2,
  "title": "Escribir tests",
  "description": "Cubrir los endpoints CRUD",
  "categoria": null,
  "status": "pending",
  "created_at": "2025-05-28T14:05:00"
}
```

---

### 5. Actualizar parcialmente una tarea

| Campo  | Valor              |
|--------|--------------------|
| Método | `PATCH`            |
| Ruta   | `/tasks/{task_id}` |

**Parámetros de ruta:**

| Parámetro | Tipo  | Descripción                  |
|-----------|-------|------------------------------|
| `task_id` | `int` | Identificador de la tarea    |

**Cuerpo de la petición (`TaskUpdate`):**

| Campo         | Tipo     | Obligatorio | Descripción                        |
|---------------|----------|-------------|------------------------------------|
| `title`       | `string` | No          | Nuevo título                       |
| `description` | `string` | No          | Nueva descripción                  |
| `categoria`   | `string` | No          | Nueva categoría                    |
| `status`      | `string` | No          | Nuevo estado                       |

Solo se actualizan los campos enviados en el cuerpo; los demás permanecen sin cambios.

**Ejemplo de petición:**

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

**Ejemplo de respuesta** (`200 OK`):

```json
{
  "id": 2,
  "title": "Escribir tests",
  "description": "Cubrir los endpoints CRUD",
  "categoria": null,
  "status": "in_progress",
  "created_at": "2025-05-28T14:05:00"
}
```

**Error** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

---

### 6. Eliminar una tarea

| Campo  | Valor              |
|--------|--------------------|
| Método | `DELETE`            |
| Ruta   | `/tasks/{task_id}` |

**Parámetros de ruta:**

| Parámetro | Tipo  | Descripción                  |
|-----------|-------|------------------------------|
| `task_id` | `int` | Identificador de la tarea    |

**Ejemplo de petición:**

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/2
```

**Respuesta exitosa:** `204 No Content` (sin cuerpo).

**Error** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

---

## Cómo ejecutar los tests

```bash
pytest tests/ -v
```

Los tests utilizan una base de datos SQLite en memoria con `StaticPool` para garantizar aislamiento entre casos. No modifican el archivo `tareas.db` de producción.

---

## Estructura del proyecto

```
gestor-tareas-api/
├── aplicacion/                 # Paquete principal de la aplicación
│   ├── __init__.py
│   ├── principal.py            # Punto de entrada: instancia FastAPI y registro de routers
│   ├── base_de_datos.py        # Configuración del engine y sesión de SQLAlchemy
│   ├── modelos.py              # Modelos ORM (tabla tasks, enum TaskStatus)
│   ├── esquemas.py             # Esquemas Pydantic de entrada y respuesta
│   └── rutas/                  # Definición de endpoints REST
│       ├── __init__.py
│       └── tareas.py           # Endpoints CRUD de tareas
├── tests/                      # Suite de tests con pytest
│   ├── __init__.py
│   └── test_tasks.py           # Tests de los endpoints de tareas
├── requirements.txt            # Dependencias del proyecto
├── AGENTS.md                   # Instrucciones para agentes de IA
└── README.md                   # Este archivo
```
