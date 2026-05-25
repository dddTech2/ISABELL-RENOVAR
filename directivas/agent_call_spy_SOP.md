# SOP - Escucha de Llamadas en Tiempo Real (Call Spy / ChanSpy) y Detección de Llamadas Activas

## Objetivo
1. Permitir a los coordinadores y supervisores escuchar en tiempo real las llamadas activas de los agentes que se encuentren en estado ocupado ("Busy", "Ocupado", "On Call" o similar).
2. Extraer la extensión del supervisor automáticamente desde su sesión de usuario activa en Issabel usando las clases de ACL, evitando que tenga que introducirla manualmente.
3. Detectar llamadas activas (manuales o entrantes directas) para todos los agentes, incluso si se encuentran en descanso (`paused` / En descanso) u offline (`offline` / No logon).
4. Conservar y mostrar el estado de pausa o desconexión original del agente mientras está en llamada (ej. `"Ocupado (En descanso: LUNCH)"`).
5. Asegurar que el color amarillo (en llamada / ocupado) tenga prioridad visual en la tabla de monitoreo sobre el naranja (en descanso) y el rojo (desconectado), y que el menú contextual ofrezca todas las opciones aplicables al mismo tiempo.

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
    - Cambiar la condición de escaneo de canales activos en Asterisk para incluir agentes en estado `offline`.
    - Condición final: `if ($agent['status'] == 'online' || $agent['status'] == 'paused' || $agent['status'] == 'offline')`.
    - Antes de cambiar `$agent['status'] = 'oncall'`, guardar el estado anterior en `$agent['original_status'] = $agent['status']`.

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
    - Si el estado contiene "Busy", "Ocupado", "Occupé", "Meşgul" o "Занят":
      - Pintar la fila de amarillo.
      - En `agentUpdateColor`, asignar la imagen del icono de ocupado (`agent-busy.png`).
    - Si no, proceder con el chequeo de "En descanso" y asignar naranja y el icono de break.

### 4. Menú Contextual Concurrente (`javascript.js`)
- En el manejador de clic sobre las filas de agentes:
  - En lugar de usar `if/else` excluyentes, evaluar las banderas de estado de manera independiente:
    - `hasPaused`: `statusLower` contiene break, descanso o pause.
    - `hasLoggedOut`: `statusLower` contiene no logon, logged out o no logoneado.
    - `hasBusy`: `statusLower` contiene busy, ocupado, oncall, on call u occupé.
  - Mostrar u ocultar los botones `#btnUnbreakAgent`, `#btnForceLoginAgent` y `#btnSpyAgent` según corresponda a las banderas.
  - Si al menos uno de los tres es verdadero, desplegar el menú contextual.

## Restricciones y Trampas Conocidas
- **Coexistencia de Estados:** Es posible que un agente esté en descanso y en llamada. Al dar prioridad al color amarillo, la fila se verá amarilla pero el texto del estado ("Ocupado (En descanso: LUNCH)") le indicará claramente al supervisor ambas realidades.
- **Chequeo Concurrente del Menú Contextual:** Asegurar que los selectores de jQuery para mostrar y ocultar las opciones no colisionen y dejen visible el botón adecuado según el estado real.
