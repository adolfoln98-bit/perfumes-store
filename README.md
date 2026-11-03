# Perfumes Store API

Backend de una tienda de perfumes desarrollado con **Python y FastAPI**, orientado a la gestión de catálogo, usuarios, carritos y pedidos. El proyecto aplica una arquitectura por capas, persistencia relacional con PostgreSQL y pruebas automatizadas.

> **Estado:** proyecto en desarrollo. La automatización de CI/CD y el despliegue cloud forman parte de las siguientes etapas.

## Tecnologías

- **Backend:** Python, FastAPI, Pydantic
- **Base de datos:** PostgreSQL, SQLAlchemy 2.x, psycopg 3
- **Migraciones:** Alembic
- **Seguridad:** JWT, OAuth2 Bearer, roles y control de propiedad de recursos (*ownership*)
- **Testing:** Pytest, PostgreSQL independiente para pruebas
- **Infraestructura:** Docker, Docker Compose
- **Operaciones:** PowerShell, `pg_dump`, `pg_restore`, logs y alertas SMTP mediante Python

## Funcionalidades

- Gestión de perfumes y marcas, con filtros y ordenación del catálogo.
- Descuentos opcionales y cálculo del precio final sin duplicarlo en la base de datos.
- Autenticación con JWT y autorización por roles (`USER`, `ADMIN`, `SUPERADMIN`).
- Protección de recursos privados mediante comprobaciones de *ownership*.
- Carrito por usuario, con operaciones para añadir, actualizar y eliminar líneas.
- Confirmación de pedidos dentro de una única transacción: comprobación de stock, creación de pedido y líneas, descuento de existencias y vaciado del carrito.
- Conservación de los datos históricos de compra en las líneas de pedido.
- Tests automatizados con base de datos PostgreSQL independiente y aislamiento transaccional.

## Arquitectura

La aplicación separa responsabilidades en varias capas:

```text
Router (HTTP / FastAPI)
        ↓
Servicio (casos de uso y transacciones)
        ↓
Repositorio (consultas y persistencia)
        ↓
SQLAlchemy / PostgreSQL
```

Los **servicios** coordinan las reglas de negocio y las transacciones. Los **repositorios** concentran el acceso a datos. Los **routers** gestionan la interfaz HTTP y traducen las excepciones de dominio a respuestas apropiadas.

## Integridad y seguridad

El checkout se ejecuta como una operación atómica: si una de sus etapas falla, se revierten los cambios de la transacción. El stock se comprueba al confirmar el pedido, no al añadir artículos al carrito.

La autenticación identifica al usuario mediante el `sub` del JWT; las autorizaciones se evalúan utilizando el rol vigente en la base de datos. Las operaciones sobre recursos privados comprueban su propietario para prevenir accesos indebidos.

## Docker y copias de seguridad

El proyecto utiliza Docker Compose para los servicios de aplicación y base de datos.

El sistema local de backups de PostgreSQL:

- Genera copias lógicas en formato personalizado con `pg_dump -Fc`.
- Verifica que el archivo puede leerse mediante `pg_restore --list` antes de conservarlo.
- Mantiene copias diarias de los últimos **7 días**, las **4 semanales** más recientes y las **3 mensuales** más recientes.
- Se programa diariamente a las **03:00** mediante el Programador de tareas de Windows.
- Evita ejecuciones simultáneas mediante un bloqueo exclusivo de archivo.
- Registra incidencias en `backups/logs/backup.log` y envía alertas por Gmail si falla el proceso principal.

**Alcance de la verificación:** `pg_restore --list` comprueba la lectura del archivo, pero no equivale a ensayar una restauración completa. Las alertas se han probado manualmente con un fallo simulado; queda pendiente validar su ejecución desde el Programador de tareas.

## Pruebas

La suite utiliza **Pytest** y una base de datos PostgreSQL exclusiva para testing, configurada mediante `TEST_DATABASE_URL`. Los tests se aíslan mediante transacciones que se revierten al finalizar cada caso.

### Requisitos

- Docker con el complemento Docker Compose.
- Para los backups programados: Windows, PowerShell, Python en `.venv` y acceso a Docker desde la cuenta que ejecuta la tarea.

### Variables de entorno

Los archivos `.env` contienen credenciales y **no deben incluirse en Git**. Antes de ejecutar Compose, crea estos archivos con valores propios:

| Archivo | Variables necesarias |
| --- | --- |
| `.env.docker` | `DATABASE_URL`, `TEST_DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` |
| `.env.postgres` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `.env.test.docker` | `DATABASE_URL`, `TEST_DATABASE_URL`, `SECRET_KEY` |
| `.env.prod` | `DATABASE_URL`, `SECRET_KEY` |
| `.env.postgres.prod` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `.env.migrations.prod` | `MIGRATION_DATABASE_URL` |

Para el entorno de pruebas, ambas URLs (`DATABASE_URL` y `TEST_DATABASE_URL`) apuntan al servicio `db_test` y a la base `perfumes_store_test`. La clave `SECRET_KEY` debe ser exclusiva de las pruebas.

Por ejemplo, la estructura de una URL interna es:

```dotenv
DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASENA@db_test:5432/BASE_DE_DATOS
```

Sustituye los marcadores por los valores de tu configuración local.

En las URLs de conexión ejecutadas **dentro de Docker**, utiliza `db` o `db_test` como hostname, según el servicio, no `localhost`.

El usuario, contraseña y nombre de base de datos deben coincidir con los del servicio PostgreSQL correspondiente. `SECRET_KEY` debe ser una clave aleatoria propia. No reutilices las credenciales de ejemplo en producción.

La variable `DATABASE_URL` de `.env.example` es solo un ejemplo de conexión desde el equipo anfitrión y debe personalizarse. La configuración de producción local **no equivale** a un despliegue público endurecido.

### Desarrollo con Docker

```bash
docker compose up --build -d
```

API: `http://localhost:8000`

Swagger UI (si está habilitado): `http://localhost:8000/docs`.

Aplicar las migraciones de desarrollo, con la API y la base de datos levantadas:

```bash
docker compose exec api alembic upgrade head
```

### Tests con Docker

```bash
docker compose --profile test run --build --rm tests
```

El servicio `tests` ejecuta `alembic upgrade head && pytest` y depende de `db_test`, una instancia independiente de PostgreSQL.

### Producción local con Docker Compose

```bash
docker compose -f compose.prod.yaml up --build -d db
docker compose -f compose.prod.yaml --profile migration run --build --rm migrations
docker compose -f compose.prod.yaml up --build -d
```

API: `http://localhost:8001`

Healthcheck interno: `/api/health/live`.

El servicio `migrations` aplica Alembic con `-x prod=true`; se ejecuta de manera explícita y no forma parte del arranque automático de `api`.

Esta configuración está orientada a un entorno local de producción, no a un despliegue cloud.

### Copias de seguridad

Con la base de datos de producción local disponible y la configuración local de alertas preparada, el script se ejecuta en Windows desde la raíz del repositorio:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\backup.ps1"
```

Las credenciales de Gmail utilizadas por las alertas se almacenan fuera del repositorio, protegidas mediante DPAPI para el usuario de Windows configurado.

El sistema de backups es **local**; todavía no sustituye una estrategia de copias externas ni una prueba de restauración completa.

## Decisiones técnicas

Las decisiones de arquitectura, sus motivos y las alternativas descartadas están documentadas en [DECISIONES_TECNICAS.md](./DECISIONES_TECNICAS.md).

## Próximos pasos

- Validar las alertas desde la ejecución programada de Windows.
- Configurar integración continua con GitHub Actions para ejecutar los tests automáticamente.
- Preparar el despliegue cloud y su estrategia de automatización.

## Autor

Proyecto personal de **Adolfo López Navas**, orientado al desarrollo backend con Python.