DT-001 — Elección del SGBD

Decisión

Utilizar PostgreSQL como sistema gestor de bases de datos.

Motivo

El proyecto pretende simular un backend utilizado en un entorno profesional. PostgreSQL ofrece mejor soporte para concurrencia, transacciones, múltiples conexiones, usuarios, permisos y despliegues que SQLite.

Alternativas consideradas

SQLite.

Motivo del descarte

Aunque SQLite es excelente para aprendizaje y proyectos pequeños, su arquitectura basada en archivo no representa el escenario habitual de un backend profesional.

DT-002 — Uso del schema public

Decisión

Utilizar inicialmente el schema public.

Motivo

El proyecto solo contiene un dominio funcional y no existe todavía una necesidad de separar objetos en distintos schemas.

Alternativas consideradas

Crear schemas específicos (catalogo, ventas, usuarios, etc.).

Motivo del descarte

Introducir varios schemas aumentaría la complejidad sin aportar un beneficio real en esta fase del proyecto. Si el dominio crece o aparecen necesidades de separación entre módulos o permisos, se reevaluará esta decisión.

DT-003 — Driver PostgreSQL

Decisión

Utilizar psycopg (versión 3) como driver de PostgreSQL.

Motivo

Es la versión moderna del driver oficial para Python, está mantenida activamente y es la recomendada para proyectos nuevos.

Alternativas consideradas

psycopg2.

Motivo del descarte

Aunque sigue siendo ampliamente utilizada y aparece en muchos tutoriales, psycopg representa la evolución actual del proyecto y es la opción más adecuada para comenzar un desarrollo nuevo.

DT-004 — Configuración de la conexión a PostgreSQL

Decisión

Utilizar una única variable de entorno DATABASE_URL.

Motivo

Es el formato esperado por SQLAlchemy, Alembic y la mayoría de herramientas del ecosistema Python. Reduce código innecesario y facilita el despliegue en distintos entornos.

Alternativas consideradas

Separar la configuración en DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME.

Motivo del descarte

Aunque mejora la legibilidad individual de cada parámetro, obliga a construir la URL de conexión en el código o depender de mecanismos de interpolación que no están soportados de forma uniforme en todos los entornos.

DT-005 — Introducción de SQLAlchemy como ORM

Decisión

Utilizar SQLAlchemy como ORM para el acceso a datos.

Motivo

Tras comprender el funcionamiento de PostgreSQL, SQL y el acceso manual mediante psycopg, el crecimiento del modelo de dominio hace recomendable introducir un mayor nivel de abstracción. SQLAlchemy permite representar las tablas como objetos Python, gestionar las relaciones entre entidades y reducir el código repetitivo asociado a consultas, inserciones, actualizaciones y eliminaciones, manteniendo una separación clara entre el dominio de la aplicación y la persistencia de los datos.

Alternativas consideradas

Continuar utilizando exclusivamente psycopg y SQL manual.

Motivo del descarte

Aunque proporciona un control total sobre las consultas y sigue siendo una opción válida en determinados escenarios, requiere escribir y mantener manualmente el acceso a datos, el mapeo entre filas y objetos, y gran parte de la lógica de persistencia. A medida que el dominio del proyecto crece, este enfoque incrementa el esfuerzo de mantenimiento sin aportar un beneficio proporcional.