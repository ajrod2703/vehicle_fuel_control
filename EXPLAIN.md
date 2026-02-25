# EXPLAIN.md - Módulo Vehicle Fuel Control

## Descripción General del Diseño

El módulo se construye alrededor de tres modelos principales:

- `vehicle.fuel.vehicle`: Almacena información básica del vehículo (nombre, placa, modelo, conductor opcional). Este modelo sirve como referencia tanto para las solicitudes como para los asientos del libro mayor.
- `vehicle.fuel.request`: Representa una solicitud de combustible realizada por un usuario. Incluye campos como vehículo, solicitante, fecha, litros, odómetro y un campo de estado para seguir el flujo de trabajo (borrador → aprobado → hecho → cancelado). El modelo hereda de `mail.thread` y `mail.activity.mixin` para permitir seguimiento y actividades.
- `vehicle.fuel.ledger`: Actúa como un registro de auditoría inmutable de las entregas reales de combustible. Cada asiento del libro mayor se crea automáticamente cuando una solicitud se marca como hecha, y almacena una instantánea de los datos relevantes (vehículo, fecha, litros, odómetro, costo, usuario que procesó la entrega y un enlace a la solicitud de origen). Esta separación asegura que el libro mayor no pueda ser alterado, proporcionando un historial fiable para auditorías e informes.

## Decisiones Clave de Diseño

### 1. Separación de Solicitudes y Libro Mayor
La razón principal para separar la solicitud y el libro mayor es la **auditabilidad**. Una solicitud de combustible representa una intención o aprobación, mientras que el libro mayor registra el evento real de la entrega de combustible. Al mantenerlos separados, podemos:
- Seguir todo el ciclo de vida de una solicitud (quién solicitó, quién aprobó, etc.).
- Asegurar que una vez que se registra una entrega, no pueda ser modificada ni eliminada (el libro mayor es de solo escritura a través del método `action_done`).
- Facilitar futuras mejoras como el seguimiento de costos, integración con tarjetas de combustible externas o conciliación sin afectar el historial de solicitudes.

### 2. Creación Automática del Libro Mayor
El asiento del libro mayor se crea programáticamente en el método `action_done` del modelo de solicitud. Esto garantiza que cada solicitud completada tenga un asiento correspondiente en el libro mayor, y captura los datos exactos en el momento de la finalización (incluyendo el usuario que la marcó como hecha). El asiento del libro mayor está vinculado a la solicitud mediante un campo Many2one (`request_id`), permitiendo la trazabilidad en ambos sentidos.

### 3. Gestión de Estados
El modelo de solicitud utiliza una máquina de estados simple con cuatro estados: `borrador`, `aprobado`, `hecho` y `cancelado`. Los botones en la vista de formulario se muestran condicionalmente según el estado actual usando el atributo `invisible` con expresiones Python (por ejemplo, `invisible="state != 'draft'"`), que es la forma de Odoo 18 (reemplazando el atributo `states` obsoleto). Esto proporciona un flujo de trabajo claro e intuitivo para los usuarios.

### 4. Seguridad y Control de Acceso
Se definen dos grupos de seguridad:
- **Usuario de Combustible**: Puede crear y gestionar sus propias solicitudes (solo pueden ver y editar las solicitudes donde ellos son el solicitante, aplicado mediante una regla de registro). Tienen acceso de solo lectura a los vehículos y al libro mayor.
- **Administrador de Combustible**: Tiene acceso completo de creación, lectura, actualización y eliminación sobre todos los vehículos, solicitudes y asientos del libro mayor.

La regla de registro para Usuarios de Combustible (`fuel_request_user_rule`) restringe el acceso a las solicitudes donde `requester_id = user.id`. Esto asegura el aislamiento de datos mientras permite a los usuarios trabajar de forma independiente. Los administradores no tienen tal restricción, dándoles una supervisión completa.

Los derechos de acceso se definen en `ir.model.access.csv` con los permisos apropiados por grupo. El modelo del libro mayor se configura deliberadamente como de solo lectura para los Usuarios de Combustible (`perm_write=0, perm_create=0, perm_unlink=0`) para mantener la integridad de la auditoría.

### 5. Vistas e Interfaz de Usuario
- **Vistas de Lista**: Utilizan la etiqueta `<list>` (Odoo 18 reemplaza `<tree>` por `<list>`) con decoraciones de color basadas en el estado para una identificación visual rápida.
- **Vistas de Formulario**: Incluyen un `<header>` con botones de estado y una barra de estado, y un `<sheet>` para el contenido principal. La disposición usa etiquetas `<group>` para organizar los campos en dos columnas, mejorando la legibilidad.
- **Vistas de Búsqueda**: Proporcionan filtros para estados comunes, "Mis Solicitudes" y opciones de agrupación por vehículo, estado y fecha.

### 6. Nombrado Automático con Secuencias
Tanto las solicitudes como los asientos del libro mayor obtienen un número de referencia único utilizando `ir.sequence` de Odoo. Los prefijos de secuencia son `REQ` para solicitudes y `LED` para asientos del libro mayor, con un relleno de 5 dígitos (ej. `REQ00001`). Esto se implementa sobrescribiendo el método `create` y asignando el siguiente código si el nombre está establecido como "New".

### 7. Datos de Demostración
Se proporciona un archivo de datos de demostración (`demo/vehicle_demo.xml`) para precargar el sistema con vehículos de ejemplo al instalar con datos de demostración. Esto ayuda a los evaluadores a empezar rápidamente.

## Desafíos y Soluciones

### Desafío 1: Compatibilidad con Odoo 18
Durante el desarrollo, nos encontramos con problemas debido a elementos obsoletos (vistas `<tree>`, atributo `states`, `attrs`). La solución fue actualizar todas las vistas para usar `<list>`, reemplazar `states` con condiciones `invisible` y eliminar cualquier uso de `attrs` en favor de expresiones Python directas. Además, el `view_mode` en las acciones se cambió de `tree,form` a `list,form`.

### Desafío 2: Visibilidad de los Menús
Después de la instalación, los menús no eran visibles aunque aparecían en los menús técnicos. La causa era que el usuario (administrador) no estaba asignado explícitamente a los grupos de seguridad del módulo. La solución fue asignar al usuario a los grupos "Usuario de Combustible" y "Administrador de Combustible". Alternativamente, los menús podrían hacerse públicos, pero para un control de acceso adecuado, la asignación de grupos es el enfoque correcto.

### Desafío 3: Errores de Validación XML
Errores como "Document does not comply with schema" se rastrearon hasta XML mal formado, a menudo debido a etiquetas `<header>` sobrantes dentro de vistas de lista o anidamiento incorrecto. Una revisión cuidadosa y la adhesión al esquema esperado de Odoo resolvieron estos problemas.

### Desafío 4: Creación Automática del Libro Mayor
Asegurar que el asiento del libro mayor se cree de forma atómica cuando una solicitud se marca como hecha requirió sobrescribir el método `action_done`. El método verifica que la solicitud esté en estado `aprobado`, crea el asiento del libro mayor y luego actualiza el estado de la solicitud y enlaza el libro mayor. Esto se hace en una sola transacción para mantener la consistencia.

## Mejoras Futuras
- **Informe de Consumo de Combustible**: Un informe QWeb que se pueda imprimir o exportar, mostrando el consumo por vehículo en un rango de fechas.
- **Asistente de Aprobación Masiva**: Un modelo transitorio para permitir a los administradores aprobar, marcar como hechas o cancelar múltiples solicitudes a la vez.
- **Integración con el Módulo Fleet**: Si la empresa utiliza el módulo `fleet` de Odoo, podríamos heredar de `fleet.vehicle` en lugar de crear un modelo de vehículo separado.
- **Seguimiento de Costos**: Añadir campos de costo al libro mayor y calcular gastos totales por vehículo.

## Conclusión
El módulo `vehicle_fuel_control` cumple con todos los requisitos de la prueba técnica: proporciona un flujo de trabajo completo para solicitudes de combustible, mantiene un libro mayor auditable, implementa control de acceso basado en roles y ofrece una interfaz de usuario limpia e intuitiva. El diseño enfatiza la separación de responsabilidades, la integridad de los datos y la facilidad de uso.