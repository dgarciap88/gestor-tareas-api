# ADR-001: Uso de SQLite como base de datos

| Campo  | Valor      |
|--------|------------|
| Estado | Aceptado   |
| Fecha  | 2025-05-28 |

---

## Contexto

La API de Gestión de Tareas necesita persistir tareas con campos como identificador, título, descripción opcional, estado (`pending`, `in_progress`, `done`) y fecha de creación. El proyecto está orientado a escenarios educativos de depuración y calidad de software, por lo que se prioriza la simplicidad de despliegue y la facilidad de incorporación de nuevos desarrolladores frente al rendimiento a gran escala.

El stack elegido (FastAPI + SQLAlchemy + Pydantic) es compatible con cualquier motor relacional soportado por SQLAlchemy, de modo que la elección del motor de base de datos es independiente del resto de la arquitectura.

---

## Decisión

Se adopta **SQLite** como motor de base de datos, almacenando los datos en el archivo local `tareas.db`.

### Razones principales

1. **Cero configuración**: SQLite no requiere instalar ni administrar un servidor de base de datos. Basta con tener Python instalado para que la aplicación funcione.
2. **Portabilidad**: la base de datos es un único archivo que se puede copiar, versionar o eliminar sin herramientas externas.
3. **Idoneidad para el caso de uso**: el volumen de datos esperado (cientos o pocos miles de tareas) y la concurrencia prevista (un usuario o un pequeño equipo) están dentro de los límites cómodos de SQLite.
4. **Alineación con el propósito educativo**: el proyecto se utiliza para prácticas de depuración y calidad de software. SQLite elimina la barrera de entrada de configurar infraestructura, permitiendo que los participantes se centren en el código.
5. **Compatibilidad con SQLAlchemy**: al usar el ORM, la lógica de acceso a datos no depende del motor. Migrar a otro motor en el futuro requiere cambiar únicamente la cadena de conexión y, en su caso, ajustar tipos de datos específicos.
6. **Tests en memoria**: SQLite permite crear bases de datos en memoria (`sqlite://`) con `StaticPool`, lo que acelera los tests y garantiza aislamiento completo entre casos de prueba.

---

## Alternativas consideradas

### PostgreSQL

| Aspecto | Detalle |
|---------|---------|
| **Ventajas** | Soporte avanzado de concurrencia (MVCC), tipos de datos ricos (JSONB, arrays, UUID nativo), extensiones (PostGIS, pg_trgm), replicación integrada y amplio ecosistema de herramientas de monitorización. Rendimiento superior en escenarios de escritura intensiva y consultas complejas. |
| **Inconvenientes** | Requiere instalar y mantener un servidor (o un contenedor Docker). Añade complejidad de configuración (usuarios, permisos, red) que no aporta valor en un contexto educativo con un volumen de datos mínimo. Incrementa los requisitos del entorno de desarrollo. |

### MySQL

| Aspecto | Detalle |
|---------|---------|
| **Ventajas** | Amplia adopción en la industria, buen rendimiento en lecturas, herramientas maduras de administración (MySQL Workbench, phpMyAdmin) y documentación abundante. Soporte de replicación maestro-esclavo y particionamiento de tablas. |
| **Inconvenientes** | Al igual que PostgreSQL, necesita un proceso servidor independiente. Históricamente tiene diferencias sutiles en el cumplimiento del estándar SQL y en el manejo de transacciones respecto a PostgreSQL. Añade la misma barrera de entrada innecesaria para un proyecto de alcance reducido. |

---

## Consecuencias

### Positivas

- Los nuevos desarrolladores pueden arrancar la aplicación en menos de un minuto sin dependencias externas.
- El pipeline de tests es rápido y autónomo gracias a las bases de datos en memoria.
- El despliegue en entornos de formación es trivial: copiar el proyecto y ejecutar `uvicorn`.

### Negativas y riesgos a largo plazo

- **Concurrencia limitada**: SQLite serializa las escrituras. Si el proyecto evoluciona hacia un entorno multiusuario con escrituras concurrentes frecuentes, será necesario migrar a PostgreSQL u otro motor cliente-servidor.
- **Funcionalidades SQL reducidas**: SQLite no soporta de forma nativa `ALTER TABLE DROP COLUMN` (versiones anteriores a 3.35), tipos como `ARRAY` o `JSONB`, ni procedimientos almacenados. Si la complejidad del modelo de datos crece, estas limitaciones pueden frenar el desarrollo.
- **Sin replicación ni alta disponibilidad**: SQLite opera en un único archivo local. No ofrece mecanismos nativos de replicación, respaldo en caliente ni failover, lo cual lo descarta para entornos de producción con requisitos de disponibilidad estrictos.
- **Acoplamiento al sistema de ficheros**: el archivo `tareas.db` está ligado al servidor que ejecuta la aplicación. Escalar horizontalmente (múltiples instancias) requiere una base de datos compartida en red.

### Plan de migración

Gracias al uso de SQLAlchemy como capa de abstracción, migrar a PostgreSQL o MySQL en el futuro implicaría:

1. Instalar el driver correspondiente (`psycopg2` o `pymysql`).
2. Actualizar `SQLALCHEMY_DATABASE_URL` en `aplicacion/base_de_datos.py`.
3. Revisar tipos de columna que aprovechen características específicas del nuevo motor.
4. Ejecutar las migraciones pertinentes (p. ej., con Alembic).

La decisión de migrar debería tomarse cuando se detecte alguna de las limitaciones descritas anteriormente como bloqueante para los requisitos del proyecto.
