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

DT-006 — Gestión de transacciones mediante la capa de servicios

Decisión

Centralizar la gestión de las transacciones de base de datos en la capa de servicios.

Motivo

La capa de servicios representa cada caso de uso de la aplicación y constituye la unidad de trabajo de SQLAlchemy. Por este motivo, es la responsable de abrir la sesión, realizar flush(), confirmar los cambios mediante commit() y revertirlos con rollback() cuando sea necesario.

Esta separación permite que los repositorios se limiten exclusivamente al acceso a datos, evitando que cada operación decida de forma independiente cuándo persistir los cambios. De este modo es posible coordinar varias operaciones sobre diferentes repositorios dentro de una única transacción.

Alternativas consideradas

Gestionar commit() y rollback() directamente desde cada repositorio.

Motivo del descarte

Este enfoque rompe el principio de responsabilidad única y dificulta coordinar varias operaciones dentro de una misma transacción. Además, obliga a que el repositorio tome decisiones que pertenecen al caso de uso y no al acceso a datos.

DT-007 — Separación entre repositorios y servicios

Decisión

Mantener una separación explícita entre la capa de repositorios y la capa de servicios.

Motivo

Los repositorios se encargan exclusivamente de interactuar con la base de datos y devolver entidades del dominio. La capa de servicios coordina la lógica de negocio, interpreta los resultados obtenidos, gestiona las transacciones y traduce las excepciones técnicas en excepciones propias de la aplicación.

Esta organización facilita el mantenimiento del código, mejora su reutilización y mantiene desacopladas las responsabilidades de persistencia y negocio.

Alternativas consideradas

Implementar toda la lógica directamente en los repositorios.

Motivo del descarte

Aunque reduce el número de clases en proyectos pequeños, termina mezclando acceso a datos, reglas de negocio y gestión de transacciones en un mismo componente, dificultando la evolución del proyecto conforme aumenta su complejidad.

DT-008 — Gestión de la evolución del esquema mediante Alembic

Decisión

Utilizar Alembic como herramienta para gestionar las migraciones del esquema de la base de datos.

Motivo

A medida que el proyecto evoluciona, la estructura de la base de datos cambia de forma continua. Alembic permite versionar estos cambios, mantener un historial de la evolución del esquema y aplicarlos de forma reproducible en distintos entornos.

Las migraciones pasan a formar parte del código fuente, evitando modificaciones manuales sobre la base de datos y garantizando que todos los entornos utilicen la misma versión del esquema.

Además, la integración con SQLAlchemy permite generar automáticamente propuestas de migración a partir de los modelos ORM, que posteriormente son revisadas y adaptadas cuando es necesario para preservar la integridad de los datos existentes.

Alternativas consideradas

Modificar manualmente la estructura de la base de datos mediante pgAdmin o scripts SQL ejecutados manualmente.

Motivo del descarte

Aunque este enfoque resulta suficiente durante las primeras fases del desarrollo, deja de ser escalable conforme aumenta el número de cambios o de entornos donde desplegar la aplicación. Además, dificulta reproducir el historial de modificaciones, aumenta el riesgo de inconsistencias entre bases de datos y obliga a gestionar manualmente la evolución del esquema.