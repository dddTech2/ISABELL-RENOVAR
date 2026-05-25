# SOP - Detección de Llamadas Manuales y Externas en Monitoreo de Campañas

## Objetivo
Permitir que la consola de monitoreo de campañas (`campaign_monitoring`) muestre a los agentes como "Ocupado" (en llamada) cuando estén cursando cualquier llamada activa en Asterisk (como llamadas manuales salientes, entrantes directas, o entre extensiones), incluso si la llamada no fue generada por el marcador predictivo del Call Center. Esto permite usar la pantalla de monitoreo como un panel de control general para supervisar a todos los gestores.

## Entradas y Salidas
- **Entradas:**
  - El listado de agentes del Call Center devuelto por ECCP (Elastix Call Center Protocol).
  - El estado de los canales activos de Asterisk obtenidos a través del comando `core show channels concise`.
- **Salidas:**
  - Modificación del estado del agente en el array `$reporte['agents']` dentro de `leerEstadoCampania` de `paloSantoConsola.class.php`.
  - Configuración de la estructura `callinfo` con el número telefónico, canal, y tiempo de inicio de la llamada para que el frontend de monitoreo de campaña lo muestre de forma nativa.
  - Corrección de la plantilla del frontend para alinear las columnas del panel de agentes.

## Lógica y Pasos

### 1. Obtención de Canales Activos de Asterisk
- Ejecutar el comando `asterisk -rx 'core show channels concise'` mediante `shell_exec`.
- Parsear las líneas divididas por el carácter `!` para extraer:
  - `channel` (Canal de origen, ej. `PJSIP/1005-0000002b`).
  - `exten` (Extensión o número marcado, ej. `3059117385`).
  - `callerid` (Identificador de llamadas, ej. `1005`).
  - `duration` (Duración de la llamada en segundos, ej. `45`).
  - `peerchannel` (Canal del par enlazado, ej. `PJSIP/outbound-trunk-0000002c`).

### 2. Detección de Coincidencia de Agente / Extensión
- Para cada agente en la lista de la campaña, construir una lista de identificadores posibles para buscar coincidencias:
  - `extension` (ej. `1005` o `PJSIP/1005`).
  - `channel` (ej. `PJSIP/1005`).
  - `agentchannel` (ej. `Agent/1005` o `PJSIP/1005`).
- Buscar en los canales activos de Asterisk si el nombre del canal o el canal par (`peerchannel`) coincide con el identificador del agente mediante expresiones regulares (ej. `/^(PJSIP|SIP|IAX2|Local)\/1005(-|@|\/|$)/i`).
- Si se detecta coincidencia:
  - Cambiar el estado del agente (`status`) a `'oncall'`.
  - Crear la estructura `callinfo` conteniendo:
    - `callnumber`: El número marcado o caller ID de la llamada.
    - `trunk`: La tecnología o troncal utilizada (ej. `PJSIP/outbound-trunk`).
    - `linkstart` / `dialstart`: Fecha y hora exactas del inicio de la llamada (calculado restando `duration` a la hora actual).

### 3. Integración en `PaloSantoConsola`
- Modificar la función `leerEstadoCampania` en `modules/agent_console/libs/paloSantoConsola.class.php`.
- Al final de la función, antes de retornar el `$reporte`, recorrer `$reporte['agents']` y aplicar la lógica de detección si el agente está en estado `'online'` o `'paused'`.
- Añadir las funciones auxiliares `_obtenerCanalesActivosAsterisk` y `_detectarLlamadaActivaAgente` con visibilidad `public` en `PaloSantoConsola`.

### 4. Ciclo de Espera Corta (Polling Activo) en `checkStatus`
- Modificar `esperarEventoSesionActiva($timeout = 30)` en `PaloSantoConsola` para recibir el tiempo de espera máximo.
- En `index.php` -> `manejarMonitoreo_checkStatus()`, limitar la espera de eventos en el bucle `while` a un máximo de 3 segundos (`min($restante, 3)`).
- En cada iteración del bucle, re-evaluar el estado con `leerEstadoCampania()` y compararlo con el estado previo del cliente. Si hay diferencias en el estado de algún agente (debido al inicio o fin de una llamada manual), salir del bucle inmediatamente para retornar la actualización en tiempo real al navegador.

### 5. Corrección de la Maquetación HTML de la Tabla de Agentes
- En `modules/campaign_monitoring/themes/default/informacion_campania.tpl`, no aplicar la clase `trAgent` (la cual usa `display: flex;`) directamente a la etiqueta `<td>`.
- Cambiar la etiqueta a `<td width="20%" nowrap="nowrap">` y envolver su contenido en un `<div class="trAgent">...</div>` para corregir la alineación de todas las columnas.

## Restricciones y Trampas Conocidas
- **Desfase de Columnas por Flexbox:** En tablas HTML estándar, establecer `display: flex` en un elemento `<td>` destruye el comportamiento del motor de renderizado del navegador (`display: table-cell`). Esto desalinea las celdas y desborda los encabezados. La solución es mantener el `<td>` con su visualización por defecto y usar un `<div>` flexbox interno.
- **Espera Larga Bloqueante:** Por defecto, la consola de monitoreo utiliza Comet con esperas de hasta 30 segundos en la cola de sockets de ECCP. Dado que las llamadas manuales ocurren fuera de los eventos de la campaña y no despiertan a ECCP, el servidor puede demorar hasta 30 segundos (o más si no hay pings) en notificar el cambio de estado. Utilizar esperas cortas de 3 segundos en el backend soluciona la reactividad sin generar sobrecarga.
