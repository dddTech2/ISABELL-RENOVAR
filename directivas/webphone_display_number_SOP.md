# SOP - Visualización de Número Activo en WebPhone

## Objetivo
1. Mostrar de forma clara y visible el número de teléfono (o identificador de llamada) de la llamada entrante o saliente en el WebPhone.
2. Garantizar que esta visualización funcione tanto cuando el agente está logueado en la consola (`agent_console.tpl`) como cuando se encuentra en la pantalla de login (`login_agent.tpl`).

## Entradas y Salidas
- **Entrada:** Recepción de una llamada entrante (SIP invite con remote identity) o marcación de llamada saliente (número ingresado).
- **Salida:** Renderizado de un cuadro informativo (`#webphone-call-info`) en el panel del WebPhone que muestra el número correspondiente y el estado de la llamada.
- **Restablecimiento:** Ocultación del cuadro informativo al finalizar la llamada (estado `idle`).

## Lógica y Pasos

### 1. Interfaz de Usuario (HTML/TPL)
- En `agent_console.tpl` y `login_agent.tpl`, agregar el elemento contenedor para la información de llamada dentro del panel del WebPhone:
  ```html
  <div id="webphone-call-info" class="webphone-call-info" style="display: none;">
      <div class="caller-id"></div>
      <div class="call-timer" style="font-size: 1.1em; font-weight: bold; margin-top: 5px; display: none;">00:00</div>
  </div>
  ```
  Este contenedor debe ubicarse justo debajo de `#webphone-status` y antes de la fila de auto-respuesta o de la llamada retenida.

### 2. Estilos Visuales (CSS)
- Las clases `.webphone-call-info`, `.webphone-call-info.active` y `.webphone-call-info .caller-id` ya están definidas en `webphone.css`.
- Opcionalmente, agregar una regla de centrado de texto a `.webphone-call-info` en `webphone.css` para alinearlo estéticamente con el estado del WebPhone:
  ```css
  .webphone-call-info {
      text-align: center;
  }
  ```

### 3. Lógica en JavaScript (`sip-phone.js`)
- En el objeto `state`, agregar la variable `activeNumber` inicializada en una cadena vacía `''` y `callStartTime` inicializada en `null`.
- Mantener una variable global `callTimerInterval` para el setInterval del temporizador.
- En la función `updateUI()`:
  - Cachear el elemento `$callInfo = $('#webphone-call-info')` y `$callTimer = $callInfo.find('.call-timer')`.
  - En el caso `idle` del switch de estados de llamada, limpiar el número activo (`state.activeNumber = '';`). Detener y limpiar el temporizador (`clearInterval(callTimerInterval)` y ocultar `$callTimer`).
  - Fuera del switch, si `state.callState !== 'idle' && state.activeNumber` es verdadero, mostrar el elemento `$callInfo` agregando la clase `active` y actualizar el texto de `.caller-id` con el prefijo según el estado actual (ej: "Llamando a: {número}" para `calling`, "Llamada de: {número}" para `ringing`, y "En llamada con: {número}" para `connected`).
  - Específicamente, si `state.callState === 'connected'`, iniciar el contador de segundos/minutos. Calcular la diferencia entre `Date.now()` y `state.callStartTime` y actualizar `$callTimer` cada segundo.
  - Si es falso (por ejemplo, `idle`), ocultar el elemento `$callInfo`, limpiar su contenido, y detener el temporizador.
- En la función `call(number)`:
  - Asignar `state.activeNumber = number;` antes de iniciar la llamada.
- En la función `handleIncomingCall(session)`:
  - Obtener el número del llamante desde `session.remoteIdentity.uri.user`.
  - Si existe un `session.remoteIdentity.displayName` diferente al usuario, combinar ambos (ej: `Nombre (Número)`).
  - Guardar este valor en `state.activeNumber`.
- Donde el estado de la llamada cambie a `connected` (a través de `updateCallState('connected')` o interceptando el cambio), establecer `state.callStartTime = Date.now();` para iniciar el contador.
- En la función `resume()`:
  - Extraer la identidad de `sessionToResume` (número y display name) de la misma forma que en `handleIncomingCall`.
  - Asignar este valor a `state.activeNumber` antes de llamar a `updateCallState('connected')` para garantizar que la pantalla muestre el número real con el que se está conversando.
- **Actualización de identidad al recibir transferencia (Connected Line Update):**
  - Durante una transferencia atendida completada por Asterisk, el canal de audio existente se une con el del Cliente. Asterisk envía un re-INVITE con la cabecera `P-Asserted-Identity` o `Remote-Party-ID` actualizada con la información del Cliente.
  - Para capturar esto, en `bindSessionEvents()`, definir `onInvite` en `session.delegate` (que responde a re-INVITEs).
  - Analizar las cabeceras `P-Asserted-Identity` o `Remote-Party-ID` del mensaje, extraer display name y número, asignar a `state.activeNumber` y refrescar el panel con `updateUI()`.

## Restricciones y Trampas Conocidas
- **Consistencia en Plantillas:** Las plantillas de la consola de agente (`agent_console.tpl` y `login_agent.tpl`) comparten la misma estructura HTML del WebPhone. Toda modificación en la estructura del panel de WebPhone debe aplicarse en ambos archivos.
- **Limpieza de Estado:** Asegurar que `state.activeNumber` se limpie completamente al regresar al estado `idle` para evitar que el número de una llamada previa permanezca en pantalla. También detener y reiniciar el temporizador visual y lógico.
- **Manipulación del DOM al Reemplazar Texto:** Cuidado al ejecutar reemplazos en las plantillas (vía scripts). Si el bloque objetivo (`tpl_target`) sigue coincidiendo después de haber hecho la modificación previa (por ejemplo, si se toma un sub-bloque genérico), la modificación se puede duplicar creando elementos `id="..."` repetidos que rompen el DOM y jQuery. Siempre asegúrate de hacer reemplazos idempotentes (verificando primero si el código a agregar ya existe).
- **Doble clic en Contestar (Doble accept en SIP.js):** Si el agente hace doble clic en el botón de contestar (o se llama `answer()` dos veces seguidas mientras la sesión está en estado `Establishing`), la segunda llamada a `accept()` fallará en SIP.js con un error `Invalid session state Establishing`. Si no se controla, el bloque `.catch()` de la segunda llamada restablecerá incorrectamente el estado del WebPhone a `idle` (limpiando `state.activeNumber`), lo que hace que cuando el primer `accept()` termine con éxito, el panel informativo `#webphone-call-info` no se muestre por estar el número vacío.
  * **Solución:**
    1. En `answer()`, validar si el estado de `currentSession.state` ya es `'Establishing'` o `'Established'`, en cuyo caso ignorar la llamada duplicada.
    2. En el bloque `.catch()` de `answer()`, solo cambiar el estado a `'idle'` si el estado de `currentSession` no es `'Establishing'` ni `'Established'`.
