# SOP - Escucha de Llamadas en Tiempo Real (Call Spy / ChanSpy) y Detección de Llamadas Activas

## Objetivo
1. Permitir a los coordinadores y supervisores escuchar en tiempo real las llamadas activas de los agentes que se encuentren en estado ocupado ("Busy", "Ocupado", "On Call" o similar).
2. Extraer la extensión del supervisor automáticamente desde su sesión de usuario activa en Issabel usando las clases de ACL, evitando que tenga que introducirla manualmente.
3. Detectar llamadas activas (manuales o entrantes directas) para todos los agentes, incluso si se encuentran en descanso (`paused` / En descanso) u offline (`offline` / No logon).
4. Conservar y mostrar el estado de pausa o desconexión original del agente mientras está en llamada (ej. `"Ocupado (En descanso: LUNCH)"`).
5. Asegurar que el color amarillo (en llamada / ocupado) tenga prioridad visual en la tabla de monitoreo sobre el naranja (en descanso) y el rojo (desconectado), y que el menú contextual ofrezca todas las opciones aplicables al mismo tiempo.
6. **Diferenciación de Números Dialados en Llamadas de Offline Agents:** [NUEVO] Si la llamada es saliente (CallerID coincide con la extensión del agente), extraer el número marcado de los datos de la aplicación `Dial` de Asterisk. Si es entrante, mostrar el CallerID de la llamada, evitando mostrar la propia extensión del agente en la columna de número telefónico.

## Entradas y Salidas
- **Entradas:**
  - Canal/Identificador del agente seleccionado (ej. `Agent/9002` o `PJSIP/2002`).
  - Extensión telefónica del supervisor (extraída en el backend a través del objeto `paloACL`).
- **Salidas:**
  - Petición AJAX POST a `index.php` con acción `spyAgent`.
  - Conexión AMI originando llamada de la extensión del supervisor a la función ChanSpy del agente (`<chanspy_code><agent_ext>`).

## Lógica y Pasos

### 1. Detección de Llamadas en el Backend (`paloSantoConsola.class.php`)
- En `modules/agent_console/libs/paloSantoConsola.class.php`:
  - En la función `leerEstadoCampania`:
    - Condición de escaneo: `if ($agent['status'] == 'online' || $agent['status'] == 'paused' || $agent['status'] == 'offline')`.
    - Antes de cambiar `$agent['status'] = 'oncall'`, guardar el estado anterior en `$agent['original_status'] = $agent['status']`.
  - En la función `_obtenerCanalesActivosAsterisk`:
    - Usar la invariante de índices invertidos de Asterisk para soportar de manera robusta todas las versiones (11, 12, 13, 14 o más campos en `core show channels concise`):
      - `duration` en el índice `count($fields) - 3`.
      - `peerchannel` (ID de bridge / linkedid) en el índice `count($fields) - 2`.
      - `uniqueid` en el índice `count($fields) - 1`.
  - En la función `_detectarLlamadaActivaAgente`:
    - Identificar el canal activo del agente comparando su canal contra los identificadores (ej. `PJSIP/1005`).
    - Trazar todo el grafo de canales vinculados (compartiendo el ID de bridge o cruzando las dos mitades de canales `Local`) para obtener todos los canales de la llamada.
    - Extraer el número telefónico externo descartando la extensión del propio agente y los números cortos/colas internos de la lista de candidatos (de `callerid`, `exten`, nombre de canal, y parámetros de marcado en `data`).
    - Trazar el canal de troncal (`SIP/Best` o similar) del mismo grafo de canales para evitar que se muestre el ID de bridge en la columna de troncal.

### 2. Formateo de Estados Combinados en el Backend (`index.php`)
- En `modules/campaign_monitoring/index.php`:
  - En la función `formatoAgente($agent)`:
    - En el switch para el caso `'oncall'`:
      - Si existe `$agent['original_status']`:
        - Si es `'paused'`: Formatear `$sEtiquetaStatus` como `_tr('oncall') . ' (' . _tr('paused') . ': ' . $agent['pauseinfo']['pausename'] . ')'` (ej. `Ocupado (En descanso: GESTION)`).
        - Si es `'offline'`: Formatear `$sEtiquetaStatus` como `_tr('oncall') . ' (' . _tr('No logon') . ')'` (ej. `Ocupado (No logon)`).
      - De lo contrario, mantener la traducción estándar de `'oncall'`.

### 3. Prioridad de Colores e Iconos (`javascript.js`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`:
  - En `agentColor(status, canal)` y `agentUpdateColor(status, canal)`:
    - Mover el chequeo de "ocupado" (`status.includes('Ocupado')` o similar) al inicio de la estructura condicional.

### 4. Menú Contextual Concurrente (`javascript.js`)
- En el manejador de clic sobre las filas de agentes:
  - Evaluar de forma independiente si el agente tiene el estado de pausa, logout u ocupado.
  - Mostrar u ocultar los botones correspondientes de manera concurrente.
