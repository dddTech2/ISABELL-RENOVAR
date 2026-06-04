# SOP - WebPhone Hold & Transfer Features

## Objetivo
1. Permitir al agente poner una llamada activa en espera (Hold) para silenciar la música/timbrado local/remoto y liberar la interfaz de marcación.
2. Permitir al agente realizar una segunda marcación (doble llamada) mientras la primera llamada está en espera.
3. Permitir transferencias de llamadas:
   - **Transferencia Ciega (Blind Transfer):** Enviar la llamada activa directamente a otra extensión o número externo.
   - **Transferencia Atendida (Attended Transfer):** Conectar la llamada retenida con la llamada activa y retirar al agente de la conversación.
4. Mantener la llamada retenida en espera (Hold) si la llamada activa secundaria finaliza, hasta que el agente decida recuperarla manualmente.

## Entradas y Salidas
- **Entradas:** 
  - Interacciones del usuario con los botones de Hold/Resume y Transfer.
  - Entradas de texto en el campo de transferencia.
  - Eventos de fin de llamada (`Terminated`) de los canales SIP.js.
- **Salidas:**
  - Mensajes de señalización SIP (re-INVITE de hold/unhold, REFER para transferencias).
  - Actualización dinámica de botones de acción y visualización de la llamada en espera en la consola del agente.

## Lógica y Pasos

### 1. Control de Retención (Hold & Resume)
- **Acción Hold:**
  - Configurar las opciones de re-INVITE con `hold: true` en la sesión activa (`currentSession`).
  - Guardar la referencia en la variable `heldSession`.
  - Colocar `currentSession = null` y establecer el estado de marcación de la consola en `idle`.
  - Mostrar la sección de llamada retenida con los datos del número de la sesión en espera.
- **Acción Resume:**
  - Si hay otra llamada activa (`currentSession`), primero ponerla en espera (Hold) y guardarla como la nueva `heldSession`.
  - Configurar las opciones de re-INVITE con `hold: false` en la sesión que estaba en espera.
  - Restablecer la sesión reanudada como `currentSession` y actualizar el estado a `connected`.
- **Desactivación de Auto-recuperación (Keep Hold):**
  - Si el agente finaliza la llamada activa secundaria (o la contraparte cuelga), la llamada en espera (`heldSession`) no se reanudará automáticamente.
  - El sistema cambiará el estado de la llamada activa a `idle`, pero mantendrá visible el cuadro de llamada retenida (`#webphone-held-info`) con las opciones de "Recuperar" y "Colgar", permitiendo al agente retomar al cliente cuando él lo decida.

### 2. Control de Transferencias
- **Transferencia Ciega (Blind Transfer):**
  - Mostrar un campo de entrada para ingresar el número de destino.
  - Al confirmar, generar el URI SIP y ejecutar `currentSession.refer(targetURI)`.
  - Al procesarse correctamente, limpiar la sesión local (`currentSession = null`, estado `idle`).
- **Transferencia Atendida (Attended Transfer):**
  - Si existen tanto `heldSession` como `currentSession`, habilitar la opción de transferencia atendida.
  - Al ejecutarla, invocar `heldSession.refer(currentSession)`.
  - Tras enviar el REFER, colgar ambas llamadas de forma local enviando `.bye()` a ambas sesiones.

## Restricciones y Trampas Conocidas
- **Separación de Eventos en StateChange:** Es crucial que cada sesión administre sus propios eventos y que el callback no asuma siempre que la sesión que finaliza es la activa (`currentSession`). De lo contrario, colgar la llamada retenida limpiará incorrectamente la sesión activa del usuario.
- **Autoplay y Early Media:** Las renegociaciones de SDP de Hold/Resume pueden disparar el evento `track` del `RTCPeerConnection` nuevamente. Asegurarse de que el timbre artificial local solo se vea afectado en el timbrado inicial y no durante transiciones de Hold/Resume.
