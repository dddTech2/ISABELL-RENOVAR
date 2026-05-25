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
- Al final de la función, antes de retornar el `$reporte`, recorrer `$reporte['agents']` y aplicar la lógica de detección si el agente está en estado `'online'` (Libre) o `'paused'`.
- Añadir las funciones privadas auxiliares `_obtenerCanalesActivosAsterisk` y `_detectarLlamadaActivaAgente` dentro de la clase `PaloSantoConsola`.

## Restricciones y Trampas Conocidas
- **Eficiencia:** La ejecución de `shell_exec` para obtener los canales activos debe realizarse una única vez por petición de actualización (`checkStatus` o `getCampaignDetail`) y no repetitivamente en cada iteración de agente, para evitar sobrecarga del procesador.
- **Formato del Canal:** Dependiendo de si la tecnología es SIP, PJSIP o IAX2, la nomenclatura del canal varía. La expresión regular de búsqueda debe ser flexible para contemplar cualquier prefijo tecnológico.
- **Traducción de Estado:** El estado `'oncall'` es traducido nativamente en español por los archivos de idioma a `'Ocupado'`. El cliente Ember.js mapea `'Ocupado'` al color amarillo y al ícono de teléfono ocupado, por lo que no requiere modificaciones en el frontend.
