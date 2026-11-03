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

DT-009 — Base de datos independiente para testing

Decisión

Utilizar una base de datos PostgreSQL independiente para la ejecución de los tests automatizados.

Motivo

Los tests necesitan crear, modificar y eliminar datos de forma controlada. Utilizar una base de datos específica para testing permite realizar estas operaciones sin afectar a los datos utilizados durante el desarrollo normal de la aplicación.

La base de datos de testing mantiene el mismo esquema que la base de desarrollo mediante las migraciones de Alembic. De este modo, los tests se ejecutan sobre una estructura equivalente a la utilizada por la aplicación y se comprueba además que el historial de migraciones permite reconstruir correctamente el esquema desde una base de datos vacía.

La conexión se configura mediante una variable de entorno independiente, TEST_DATABASE_URL, manteniendo separadas las configuraciones de desarrollo y testing.

Alternativas consideradas

Ejecutar los tests utilizando directamente la base de datos de desarrollo.

Motivo del descarte

Este enfoque haría que los tests dependieran del estado previo de los datos y podría provocar modificaciones o eliminaciones accidentales sobre información utilizada durante el desarrollo. Además, dificultaría garantizar que cada ejecución de los tests parte de un entorno controlado.

DT-010 — Testing automatizado con Pytest y aislamiento transaccional

Decisión

Utilizar Pytest como herramienta de testing automatizado y aislar cada test mediante una transacción independiente que se revierte al finalizar su ejecución.

Motivo

A medida que aumenta el número de casos de uso de la aplicación, las pruebas manuales dejan de ser suficientes para comprobar de forma eficiente que los cambios realizados no rompen funcionalidades existentes. Pytest permite automatizar estas comprobaciones y ejecutar de forma repetible toda la suite de tests.

Cada test utiliza una sesión conectada a la base de datos de testing dentro de una transacción exterior. Al finalizar el test se realiza rollback de dicha transacción, evitando que los datos generados durante una prueba permanezcan disponibles para las siguientes.

La infraestructura de testing sustituye temporalmente las sesiones utilizadas por los servicios por sesiones asociadas a la base de datos de testing. Esto permite mantener intacto el comportamiento del código de producción, incluyendo la responsabilidad de la capa de servicios sobre commit(), flush() y rollback(), al mismo tiempo que se garantiza el aislamiento entre tests.

Alternativas consideradas

Continuar utilizando exclusivamente scripts de pruebas manuales o permitir que cada test confirme permanentemente sus cambios en la base de datos de testing.

Motivo del descarte

Las pruebas manuales requieren intervención del desarrollador y resultan cada vez más costosas conforme aumenta el número de funcionalidades. Por otra parte, permitir que los tests mantengan permanentemente los datos creados introduciría dependencias entre pruebas y haría que sus resultados pudieran variar en función del orden o de ejecuciones anteriores.

DT-011 — Autenticación mediante JWT y OAuth2 Bearer

Decisión

Utilizar autenticación basada en tokens JWT enviados mediante el esquema OAuth2 Bearer.

Motivo

La API necesita identificar al usuario que realiza cada petición sin mantener estado de sesión en el servidor. Los tokens JWT permiten incluir la identidad del usuario en un token firmado que puede verificarse en cada petición protegida.

FastAPI integra este mecanismo mediante OAuth2PasswordBearer, permitiendo recibir el token a través de la cabecera Authorization y centralizar la obtención del usuario autenticado en una dependencia reutilizable.

Las credenciales del usuario se validan únicamente durante el inicio de sesión. A partir de ese momento, las operaciones protegidas utilizan la identidad obtenida del token y no reciben el identificador del usuario desde el cuerpo de la petición.

Alternativas consideradas

Mantener sesiones de usuario almacenadas en el servidor o enviar manualmente el identificador del usuario en cada operación protegida.

Motivo del descarte

Las sesiones de servidor requieren almacenar y gestionar estado adicional. Por otra parte, aceptar directamente el identificador del usuario desde el cliente permitiría intentar operar sobre recursos pertenecientes a otros usuarios y trasladaría al cliente una responsabilidad que debe resolver el sistema de autenticación.

DT-012 — Autorización mediante roles de usuario

Decisión

Definir roles USER, ADMIN y SUPERADMIN y centralizar las comprobaciones de autorización mediante dependencias de FastAPI.

Motivo

No todas las operaciones de la API deben estar disponibles para cualquier usuario autenticado. Las operaciones administrativas, como determinadas modificaciones sobre usuarios o catálogo, requieren distinguir entre usuarios normales, administradores y superadministradores. Las dependencias de autorización comprueban el rol vigente del usuario recuperado de la base de datos.

Centralizar esta comprobación en dependencias permite reutilizar la misma política de autorización en distintos endpoints y evita repetir lógica de permisos dentro de cada router.

Alternativas consideradas

Comprobar manualmente el rol dentro de cada endpoint o implementar permisos más granulares desde el inicio.

Motivo del descarte

Repetir las comprobaciones en cada endpoint aumentaría la duplicación y el riesgo de aplicar reglas diferentes para operaciones equivalentes. Un sistema de permisos más granular aportaría flexibilidad, pero introduciría complejidad que los requisitos actuales no necesitan.

DT-013 — Creación diferida del carrito

Decisión

Crear el carrito de un usuario únicamente cuando este realiza por primera vez una operación que requiere su existencia.

Motivo

No todos los usuarios registrados necesitan utilizar un carrito. Crear automáticamente un carrito durante el registro generaría registros que podrían no utilizarse nunca y acoplaría innecesariamente el proceso de creación de usuarios con la funcionalidad de compra.

El carrito se crea de forma diferida cuando un caso de uso lo necesita, por ejemplo al añadir el primer perfume. Una vez creado, el carrito permanece asociado al usuario incluso cuando se eliminan todas sus líneas, ya que un carrito vacío sigue siendo un estado válido.

Alternativas consideradas

Crear automáticamente un carrito para cada usuario durante el registro y eliminar el carrito cuando se elimine su última línea.

Motivo del descarte

La creación automática introduce datos y lógica innecesarios antes de que exista una necesidad real. Por otra parte, eliminar un carrito cuando queda vacío obligaría a recrearlo posteriormente y convertiría un estado perfectamente válido, el carrito vacío, en ausencia de carrito.

DT-014 — Modelado de la relación entre carrito y perfume mediante LineaCarrito

Decisión

Representar la relación entre Carrito y Perfume mediante una entidad intermedia LineaCarrito.

Motivo

Un carrito puede contener varios perfumes y un mismo perfume puede aparecer en los carritos de distintos usuarios, por lo que existe conceptualmente una relación muchos a muchos.

Esta relación necesita además almacenar información propia, concretamente la cantidad de unidades de cada perfume. LineaCarrito permite representar esta información y establece una restricción UNIQUE sobre la combinación carrito_id y perfume_id para impedir que un mismo perfume aparezca duplicado en un carrito.

Alternativas consideradas

Crear una relación muchos a muchos sin entidad intermedia explícita o almacenar directamente una colección de identificadores de perfumes dentro del carrito.

Motivo del descarte

Una tabla de asociación sin entidad propia no representaría adecuadamente atributos como cantidad. Almacenar colecciones de identificadores dentro de una columna rompería el modelo relacional y dificultaría las consultas, restricciones e integridad referencial.

DT-015 — Separación entre gestión del carrito y modificación de stock

Decisión

No modificar el stock de un perfume cuando se añade, modifica o elimina una línea del carrito.

Motivo

El carrito representa la intención de compra del usuario, pero no una compra confirmada. Añadir unidades al carrito no garantiza que el usuario vaya a finalizar el pedido.

Por este motivo, las operaciones POST, PATCH y DELETE sobre el carrito únicamente modifican LineaCarrito. El stock del perfume permanece sin cambios durante estas operaciones.

La modificación real del stock se realizará posteriormente durante el proceso de confirmación del pedido, donde será posible validar nuevamente la disponibilidad y ejecutar la operación dentro de una transacción.

Alternativas consideradas

Reducir el stock al añadir productos al carrito y restaurarlo cuando se eliminan.

Motivo del descarte

Este enfoque convertiría el carrito en un mecanismo de reserva de inventario. Los usuarios podrían bloquear unidades simplemente manteniéndolas en sus carritos y sería necesario introducir mecanismos adicionales de expiración y liberación de reservas.

Esta complejidad no resulta necesaria para los requisitos actuales del proyecto.

DT-016 — Semántica de las operaciones sobre cantidades del carrito

Decisión

Utilizar POST para añadir unidades de un perfume al carrito, PATCH para establecer una cantidad final y DELETE para eliminar completamente el perfume del carrito.

Motivo

Cada operación representa una intención diferente.

POST permite añadir un perfume al carrito y, si ya existe una línea para ese perfume, incrementar su cantidad.

PATCH representa una modificación parcial del recurso existente, por lo que la cantidad recibida se interpreta como el nuevo valor absoluto de la línea y no como un incremento o decremento.

DELETE elimina completamente la LineaCarrito correspondiente.

La cantidad de una línea debe ser siempre mayor que cero. Por tanto, establecer cantidad cero no se utiliza como mecanismo de eliminación.

Alternativas consideradas

Utilizar PATCH con incrementos positivos o negativos, o interpretar cantidad igual a cero como eliminación de la línea.

Motivo del descarte

Los incrementos relativos hacen que el significado de la petición dependa del estado previo del carrito y dificultan razonar sobre el resultado final de una operación.

Utilizar cantidad cero para eliminar introduciría además dos formas diferentes de expresar la misma operación y entraría en conflicto con la regla de dominio que establece que toda LineaCarrito existente debe tener una cantidad mayor que cero.

DT-017 — Una única transacción para casos de uso compuestos

Decisión

Ejecutar dentro de una misma sesión y transacción todas las operaciones de persistencia que forman parte de un mismo caso de uso.

Motivo

Algunas operaciones necesitan coordinar varios repositorios. Por ejemplo, añadir un perfume al carrito puede requerir obtener o crear el carrito, comprobar el perfume, consultar una línea existente y crearla o modificarla.

Todas estas acciones forman una única operación de negocio y deben confirmarse o revertirse conjuntamente. Para conseguirlo, los helpers internos reutilizables reciben la sesión existente en lugar de abrir sesiones independientes.

Alternativas consideradas

Permitir que cada servicio auxiliar o repositorio abra su propia sesión y confirme sus cambios de manera independiente.

Motivo del descarte

Dividir un caso de uso entre varias transacciones permitiría que una parte de la operación quedase confirmada aunque otra fallase posteriormente. Esto rompería la atomicidad y podría dejar la base de datos en un estado parcialmente actualizado.

DT-018 — Recuperación explícita del grafo completo mediante eager loading

Decisión

Utilizar eager loading cuando un caso de uso necesita devolver el carrito completo con sus líneas, perfumes y marcas.

Motivo

La respuesta del carrito contiene un grafo de objetos formado por Carrito, LineaCarrito, Perfume y Marca. Estas relaciones deben estar disponibles mientras la sesión está activa para que posteriormente FastAPI y Pydantic puedan construir correctamente la respuesta.

La consulta específica del carrito completo utiliza joinedload para recuperar explícitamente las relaciones necesarias. Cuando se carga una colección mediante joinedload, el resultado se procesa con unique() antes de obtener la entidad para evitar duplicados producidos por el JOIN.

Alternativas consideradas

Depender exclusivamente de la carga diferida de relaciones o realizar consultas independientes desde el router durante la serialización.

Motivo del descarte

La carga diferida puede intentar acceder a relaciones cuando la sesión ya se encuentra cerrada y hace menos explícito el coste de las consultas realizadas. Consultar relaciones desde el router mezclaría responsabilidades de presentación y persistencia.

DT-019 — Separación entre excepciones de dominio y respuestas HTTP

Decisión

Representar los errores de negocio mediante excepciones propias de la aplicación y traducirlas a respuestas HTTP únicamente en la capa de routers.

Motivo

La lógica de negocio no debe depender del protocolo HTTP. Los servicios expresan situaciones como recurso no encontrado, stock insuficiente o datos duplicados mediante excepciones de dominio específicas.

Los routers capturan estas excepciones y deciden su representación HTTP, por ejemplo 404 para recursos no encontrados o 409 para conflictos relacionados con el estado actual del recurso.

Esta separación permite reutilizar los servicios fuera de un endpoint HTTP y mantiene diferenciadas las responsabilidades de negocio y transporte.

Alternativas consideradas

Lanzar HTTPException directamente desde los servicios o repositorios.

Motivo del descarte

Introducir HTTPException en las capas internas acoplaría la lógica de negocio a FastAPI y al protocolo HTTP. Además, dificultaría reutilizar los mismos casos de uso desde otros contextos y mezclaría las reglas del dominio con decisiones propias de la interfaz de la API.

DT-020 — Modelado del pedido como snapshot histórico de la compra

Decisión

Representar cada pedido mediante las entidades Pedido y LineaPedido, almacenando en cada línea una copia del nombre del perfume y del precio unitario realmente pagado en el momento de la compra.

Motivo

Un pedido representa un hecho histórico y debe poder interpretarse correctamente aunque el catálogo cambie posteriormente. El nombre, el precio o el descuento de un perfume pueden modificarse después de una compra, pero esos cambios no deben alterar la información económica ni descriptiva del pedido ya confirmado.

Por este motivo, LineaPedido mantiene la referencia al perfume, pero conserva además los datos relevantes de la compra como snapshot histórico. El total del pedido se calcula a partir de las cantidades y precios unitarios almacenados en sus líneas.

Alternativas consideradas

Consultar siempre el nombre y el precio actuales del perfume o almacenar también un campo total persistido en Pedido.

Motivo del descarte

Depender únicamente del estado actual del catálogo haría que un pedido antiguo pudiera cambiar de significado con el tiempo. Almacenar el total introduciría un dato derivado que podría quedar desincronizado respecto a sus líneas; mientras no exista una necesidad específica de persistirlo, se calcula a partir de la información histórica de LineaPedido.

DT-021 — Confirmación del pedido y actualización de stock como operación atómica

Decisión

Realizar el checkout dentro de una única transacción que valida nuevamente el stock, crea el pedido y sus líneas, descuenta las existencias y vacía las líneas del carrito.

Motivo

El carrito representa intención de compra y no reserva inventario. Por ello, la disponibilidad debe comprobarse de nuevo en el momento de confirmar el pedido. Todas las modificaciones derivadas de la compra forman un único caso de uso y deben persistirse conjuntamente.

Si cualquiera de las operaciones falla, se ejecuta rollback para impedir estados parciales, como un pedido creado sin descontar stock o un carrito vaciado sin haberse completado correctamente la compra.

Alternativas consideradas

Descontar stock durante la gestión del carrito o confirmar por separado la creación del pedido, la actualización del stock y el vaciado del carrito.

Motivo del descarte

Reservar stock desde el carrito introduciría una política de reservas que no forma parte de los requisitos actuales. Dividir el checkout en varias transacciones rompería la atomicidad y permitiría inconsistencias si una operación intermedia fallase.

DT-022 — Descuentos integrados en Perfume sin entidad Oferta independiente

Decisión

Representar las ofertas actuales mediante un campo descuento opcional en Perfume, expresado como porcentaje entero entre 1 y 99. La ausencia de oferta se representa mediante NULL.

Motivo

Los requisitos actuales solo necesitan aplicar, modificar o retirar un descuento sobre un perfume. Crear una entidad Oferta independiente introduciría estructura adicional sin aportar funcionalidad necesaria en esta fase.

La base de datos protege la regla mediante una restricción CHECK que permite únicamente NULL o porcentajes válidos. La administración del descuento se mantiene como una operación específica del catálogo y no forma parte de la creación o actualización genérica de un perfume.

Alternativas consideradas

Crear una entidad Oferta con relaciones propias, utilizar 0 para representar ausencia de descuento o permitir descuentos del 100 %.

Motivo del descarte

Una entidad Oferta tendría sentido si apareciesen campañas, fechas de vigencia, cupones, promociones compartidas o historial de ofertas, pero actualmente supondría complejidad prematura. NULL expresa de forma más clara la ausencia de oferta que un valor 0. El descuento del 100 % implicaría reglas de promociones o productos gratuitos que quedan fuera del alcance actual.

DT-023 — Precio final calculado y reutilizable en Python y SQL

Decisión

No almacenar precio_final como columna persistida. Definirlo como una hybrid_property de SQLAlchemy calculada a partir de precio y descuento, con una implementación para objetos Python y una expresión SQL equivalente para consultas.

Motivo

El precio final es un dato derivado. Persistirlo duplicaría información y obligaría a mantenerlo sincronizado cada vez que cambiasen el precio base o el descuento.

La hybrid_property permite mantener una única abstracción de dominio: sobre una instancia devuelve el precio efectivo redondeado a dos decimales y, dentro de una consulta SQLAlchemy, se traduce a una expresión CASE y ROUND que PostgreSQL puede utilizar en filtros y ordenaciones.

Alternativas consideradas

Almacenar precio_final en la tabla Perfume o repetir manualmente la fórmula del descuento en cada repositorio que la necesite.

Motivo del descarte

Persistir un valor derivado aumenta el riesgo de inconsistencias. Duplicar la fórmula en distintos repositorios dispersaría una misma regla del dominio y dificultaría mantener un comportamiento coherente entre Python y las consultas SQL.

DT-024 — Filtros y ordenación del catálogo basados en el precio efectivo

Decisión

Interpretar los filtros precio_min y precio_max y la ordenación por precio utilizando precio_final, es decir, el importe que realmente pagaría el cliente después de aplicar un posible descuento.

Motivo

Una vez incorporadas las ofertas, utilizar el precio base produciría resultados incoherentes para el usuario. Un perfume con precio base de 100 y un descuento del 50 % debe comportarse como un producto de 50 al filtrar u ordenar el catálogo por precio.

La expresión SQL de la hybrid_property permite realizar estas operaciones directamente en PostgreSQL sin cargar primero todo el catálogo en memoria ni almacenar una columna adicional.

Alternativas consideradas

Mantener filtros y ordenación sobre el precio base o realizar el cálculo y filtrado posteriormente en Python.

Motivo del descarte

Utilizar el precio base no representa el coste real mostrado al cliente cuando existe una oferta. Filtrar u ordenar en Python requeriría recuperar más datos de los necesarios y trasladaría a la aplicación una operación que la base de datos puede resolver de forma eficiente.


DT-025 — Protección de recursos mediante ownership para prevenir BOLA

Decisión

Comprobar en los casos de uso que los recursos privados pertenecen al usuario autenticado, utilizando su identidad obtenida de la autenticación y aplicando filtros por propietario en las consultas correspondientes.

Motivo

La autenticación demuestra quién realiza la petición, pero no autoriza por sí sola el acceso a cualquier recurso. Los pedidos y carritos deben quedar limitados a su propietario. Las consultas del carrito filtran por usuario_id y las líneas por carrito_id y perfume_id. La recuperación de pedidos comprueba el propietario y evita revelar pedidos ajenos.

Alternativas consideradas

Confiar en los identificadores enviados por el cliente o comprobar únicamente que existe un usuario autenticado.

Motivo del descarte

Ambas opciones permitirían intentar acceder a recursos de otros usuarios cambiando identificadores, introduciendo vulnerabilidades de autorización a nivel de objeto (BOLA).

DT-026 — Gestión restringida del rol SUPERADMIN

Decisión

Reservar la modificación de roles a usuarios SUPERADMIN, impidiendo mediante la API la auto-modificación del rol, la modificación de otros SUPERADMIN y la asignación del rol SUPERADMIN.

Motivo

La administración de privilegios requiere límites adicionales para evitar escaladas de permisos y cambios accidentales en cuentas con privilegios máximos. Las comprobaciones se centralizan en las dependencias y reglas del caso de uso, y se verifican con tests.

Alternativas consideradas

Permitir que cualquier ADMIN modifique roles o que SUPERADMIN conceda ese mismo rol libremente mediante el endpoint público.

Motivo del descarte

Estas alternativas ampliarían innecesariamente la capacidad de conceder privilegios elevados y aumentarían el riesgo de escalada o pérdida de control sobre las cuentas administrativas.

DT-027 — JWT con identidad y autorización basada en el rol vigente

Decisión

Incluir en el JWT el identificador del usuario mediante el claim sub y su expiración mediante exp, sin almacenar el rol. Recuperar el usuario y su rol actual desde la base de datos al autorizar cada petición protegida.

Motivo

Los permisos pueden cambiar durante la vigencia de un token. Consultar el rol actual evita que un JWT emitido antes de un cambio de privilegios conserve autorizaciones obsoletas. El token se utiliza para identificar al usuario y la base de datos actúa como fuente de verdad para sus permisos.

Alternativas consideradas

Incluir el rol en los claims del JWT y confiar en él hasta la expiración del token.

Motivo del descarte

Los cambios de rol no se reflejarían inmediatamente en tokens ya emitidos, lo que podría mantener permisos revocados durante su periodo de validez.


DT-028 — Contenerización de la aplicación y sus dependencias

Decisión

Utilizar Docker y Docker Compose para definir y ejecutar los servicios de la API y PostgreSQL, manteniendo configuraciones diferenciadas cuando lo requiere el entorno.

Motivo

La contenerización permite reproducir las dependencias y la configuración de los servicios, reducir diferencias entre entornos y preparar el proyecto para futuras etapas de integración continua y despliegue.

Alternativas consideradas

Instalar y ejecutar todos los componentes directamente en el sistema anfitrión.

Motivo del descarte

La instalación manual aumenta la dependencia de la configuración local y dificulta reproducir el entorno en otros equipos.

DT-029 — Mantener build local en los servicios de Docker Compose

Decisión

Mantener build: . en los servicios que necesitan construir la imagen de la aplicación, sin introducir todavía una imagen preconstruida compartida como requisito.

Motivo

La configuración actual es suficiente para el alcance del proyecto. Se prioriza la simplicidad y se evita añadir pasos de publicación y distribución de imágenes antes de que exista una necesidad concreta.

Alternativas consideradas

Construir una única imagen por separado y referenciarla desde todos los servicios.

Motivo del descarte

Aunque puede reducir trabajo repetido en determinados escenarios, introduce gestión adicional de imágenes y versiones. Se reconsiderará si aparecen problemas medibles de tiempo de construcción, duplicación o complejidad.

DT-030 — Backups PostgreSQL mediante herramientas nativas y verificación previa

Decisión

Generar copias de seguridad de PostgreSQL con pg_dump en formato personalizado (-Fc), copiarlas inicialmente como archivos temporales y comprobar su legibilidad mediante pg_restore --list antes de conservarlas como copias definitivas.

Motivo

Las herramientas nativas de PostgreSQL permiten generar copias lógicas portables. La verificación y el uso de archivos temporales reducen el riesgo de presentar una copia incompleta como válida.

Alternativas consideradas

Copiar directamente los archivos físicos de la base de datos o guardar el resultado de pg_dump sin verificación.

Motivo del descarte

Una copia directa de archivos físicos requiere procedimientos específicos para garantizar su consistencia. Omitir la verificación deja sin detectar ciertos errores de generación o transferencia. La comprobación con pg_restore --list valida la lectura del archivo, pero no sustituye una prueba real de restauración.

DT-031 — Retención de backups diarios, semanales y mensuales

Decisión

Conservar backups diarios de los últimos siete días, los cuatro backups semanales más recientes y los tres backups mensuales más recientes. Proteger el backup diario más reciente frente a la eliminación por antigüedad.

Motivo

La política proporciona varios puntos de recuperación con un consumo de almacenamiento acotado y evita que la limpieza por antigüedad elimine el último backup diario disponible.

Alternativas consideradas

Conservar indefinidamente todas las copias o mantener únicamente una copia diaria.

Motivo del descarte

La retención indefinida consume espacio sin límite; conservar una única copia ofrece poca capacidad de recuperación ante fallos detectados tardíamente.

DT-032 — Automatización local de backups y prevención de solapamientos

Decisión

Ejecutar el backup mediante un script PowerShell programado diariamente a las 03:00 con el Programador de tareas de Windows y utilizar un bloqueo exclusivo de archivo para impedir ejecuciones simultáneas.

Motivo

El proyecto se ejecuta actualmente en un entorno Windows con Docker Desktop. PowerShell y el Programador de tareas permiten automatizar el proceso sin introducir un orquestador adicional. El bloqueo evita que dos ejecuciones manipulen al mismo tiempo los archivos de backup y su retención.

Alternativas consideradas

Ejecutar los backups manualmente, permitir ejecuciones concurrentes o incorporar desde ahora un servicio de planificación externo.

Motivo del descarte

La ejecución manual es fácil de olvidar, la concurrencia puede generar conflictos y un planificador externo añadiría complejidad innecesaria en el entorno actual. Esta decisión deberá revisarse al desplegar en infraestructura cloud.

DT-033 — Registro de incidencias y alertas de fallo por correo

Decisión

Registrar las ejecuciones y errores en backups/logs/backup.log y, cuando el proceso principal de backup falla, intentar enviar una alerta descriptiva mediante un script Python con smtplib y Gmail SMTP. El fallo del correo se gestiona de forma independiente y no reemplaza el error original del backup.

Motivo

Los logs permiten investigar el historial y las alertas notifican fallos sin necesidad de consultar manualmente el archivo. Reutilizar el mensaje capturado por PowerShell mantiene la coherencia entre ambos canales. El proceso Python devuelve un código de salida que PowerShell comprueba explícitamente.

Alternativas consideradas

Depender únicamente de los logs, analizar las últimas líneas del log para reconstruir la alerta o integrar desde el inicio un sistema externo de observabilidad.

Motivo del descarte

Los logs por sí solos no notifican incidencias. Reconstruir el error a partir del archivo añade ambigüedad y acoplamiento. Una plataforma de observabilidad completa sería prematura para el alcance actual.

DT-034 — Protección local de credenciales de Gmail para tareas automáticas

Decisión

Guardar la contraseña de aplicación de Gmail cifrada mediante DPAPI para el usuario de Windows que ejecuta el backup, almacenar la dirección de correo en un archivo de configuración separado y transmitir las credenciales a Python mediante la entrada estándar, sin imprimirlas en consola ni registrarlas en logs.

Motivo

La tarea programada debe funcionar sin interacción y no debe incluir la contraseña en texto plano dentro del repositorio o en los argumentos del proceso. DPAPI proporciona protección vinculada al contexto del usuario de Windows.

Alternativas consideradas

Escribir la contraseña directamente en el script, solicitarla interactivamente en cada ejecución o pasarla como argumento de línea de comandos.

Motivo del descarte

Incluir secretos en código o argumentos aumenta su exposición; la entrada interactiva impide la ejecución desatendida. Esta solución es local y deberá revisarse cuando se migre a CI/CD o cloud, donde corresponderá utilizar mecanismos de gestión de secretos adecuados al entorno.

Estado de validación

La autenticación y el envío de correos se han probado correctamente. También se ha validado manualmente una alerta mediante un fallo controlado del backup. Queda pendiente verificar el envío de alertas bajo el contexto real del Programador de tareas y realizar una prueba completa de restauración de una copia.
