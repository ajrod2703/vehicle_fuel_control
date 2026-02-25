# Módulo Vehicle Fuel Control para Odoo 18

Este módulo permite a las empresas gestionar solicitudes de combustible para su flota de vehículos, manteniendo un libro mayor (ledger) auditable de las entregas reales de combustible. Proporciona un flujo de trabajo completo desde la solicitud hasta la aprobación y entrega, con control de acceso basado en roles.

## Características

- **Gestión de Vehículos**: Registrar vehículos con placa, modelo y conductor/propietario opcional.
- **Solicitudes de Combustible**: Crear y gestionar solicitudes con estados: Borrador → Aprobado → Hecho → Cancelado.
- **Libro Mayor Automático**: Cuando una solicitud se marca como Hecho, se crea automáticamente un asiento en el libro mayor de combustible (Fuel Ledger), garantizando una pista de auditoría.
- **Grupos de Seguridad**: Dos grupos de usuarios – Usuario de Combustible (puede crear y gestionar sus propias solicitudes) y Administrador de Combustible (acceso completo a todas las solicitudes y al libro mayor).
- **Interfaz Amigable**: Vistas de lista, formulario y búsqueda para todos los modelos, con insignias de estado y listas con código de colores.
- **Asistente de Aprobación Masiva** (opcional, fase 3): Aprobar, marcar como hechas o cancelar múltiples solicitudes a la vez.
- **Informe de Consumo de Combustible** (opcional, fase 3): Informe imprimible que muestra el consumo por vehículo en un período seleccionado.

## Instalación

1. Copia la carpeta `vehicle_fuel_control` a tu directorio de addons de Odoo (por ejemplo, `custom-addons`).
2. Actualiza la lista de aplicaciones en Odoo (Aplicaciones → Actualizar Lista de Aplicaciones).
3. Busca "Vehicle Fuel Control" e instálalo.
4. Asigna los grupos correspondientes a los usuarios (Usuario de Combustible o Administrador de Combustible) en Ajustes → Usuarios y Compañías → Usuarios.

## Uso

### Crear un Vehículo
- Ve a **Vehicle Fuel → Vehículos** y haz clic en **Nuevo**.
- Completa los datos del vehículo (nombre, placa, modelo, conductor) y guarda.

### Crear una Solicitud de Combustible
- Ve a **Vehicle Fuel → Solicitudes de Combustible** y haz clic en **Nuevo**.
- Selecciona el vehículo, el solicitante (se asigna automáticamente al usuario actual), fecha, litros y lectura del odómetro.
- Guarda la solicitud (estado será **Borrador**).

### Aprobar y Completar una Solicitud
- En el formulario de la solicitud, haz clic en **Aprobar** (solo visible en estado Borrador) para pasar a **Aprobado**.
- Cuando el combustible se haya entregado realmente, haz clic en **Hecho** (solo visible en estado Aprobado). Esto crea automáticamente un asiento correspondiente en el Libro Mayor de Combustible.
- Si es necesario, una solicitud puede ser **Cancelada** desde los estados Borrador o Aprobado.

### Ver el Libro Mayor
- Ve a **Vehicle Fuel → Libro Mayor de Combustible** para ver todas las entregas reales de combustible. Cada asiento está vinculado a su solicitud de origen y no puede editarse directamente, preservando la integridad de la auditoría.

### Aprobaciones Masivas (si se implementa el asistente)
- Desde la vista de lista de Solicitudes de Combustible, selecciona varias solicitudes y usa el menú **Acción** para lanzar el asistente de aprobación masiva.

## Dependencias
- `base` (núcleo de Odoo)
- `mail` (para el chatter y seguimiento)

## Licencia
LGPL-3

## Autor
Alfredo - Mastercore Test