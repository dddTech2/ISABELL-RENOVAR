# SOP - Teclado DTMF en WebPhone de Consola de Agente

## Objetivo
1. Añadir un teclado numérico visual (dialpad) de 3x4 (dígitos 0-9, * y #) al WebPhone de la consola del agente para el envío de tonos DTMF durante una llamada conectada.
2. Permitir que el teclado esté disponible tanto en la pantalla de inicio de sesión (`login_agent.tpl`, antes de ingresar) como en la interfaz principal de la consola (`agent_console.tpl`, después de ingresar).
3. Habilitar el envío de tonos DTMF de manera auditiva/SIP a través del método `sendDTMF` de SIP.js cuando el agente hace clic en los botones visuales.
4. Soporte para el envío de tonos mediante el teclado físico del computador (teclas 0-9, * y #) cuando la llamada esté en estado conectado y el agente no esté enfocado en otros campos de entrada de texto del formulario de login o de la consola.

## Entradas y Salidas
- **Entrada:** Clic del usuario en los botones del teclado DTMF o pulsación de teclas físicas en el computador durante una llamada conectada.
- **Salida:**
  - Envío del tono DTMF a través del PeerConnection de la sesión SIP de SIP.js.
  - Efecto visual (destello activo) en los botones del dialpad para retroalimentación al usuario.

## Lógica y Pasos

### 1. Interfaz de Usuario (HTML/TPL)
- En `agent_console.tpl` y `login_agent.tpl`, añadir el bloque HTML para `#webphone-dialpad` con clase `webphone-dialpad`.
- El teclado debe contener 4 filas (`.dialpad-row`), cada una con 3 botones `<button type="button" class="dialpad-btn" data-tone="...">` correspondientes al diseño estándar de telefonía (1-3, 4-6, 7-9, \*, 0, #).
- El uso de `type="button"` es crítico para evitar el envío accidental de formularios.
- El dialpad debe inicializarse oculto (`style="display:none;"`).

### 2. Estilos Visuales (CSS)
- En `webphone.css`, agregar estilos para `.webphone-dialpad`, `.dialpad-row`, `.dialpad-btn` y la clase de estado activo `.dialpad-btn.active`.
- Usar un diseño en rejilla o filas flexibles que se ajusten al ancho de 280px del WebPhone.
- Asegurar transiciones suaves en hover y click.

### 3. Lógica en JavaScript/SIP (JavaScript)
- En `sip-phone.js`, implementar la función `sendDTMF(tone)`:
  - Validar si hay una sesión activa (`currentSession`).
  - Invocar el método correspondiente de envío de tono.
  - Reproducir el sonido local del tono DTMF mediante `playDTMFTone(tone)` usando el Web Audio API (AudioContext) con las frecuencias estándar DTMF (baja/alta) durante 150ms con rampa exponencial de volumen para evitar chasquidos.
  - Concatenar el dígito del tono DTMF al campo de texto `#webphone-number` para dar retroalimentación visual al usuario en pantalla de lo que está marcando.
- En `updateUI()`, obtener la referencia al elemento `#webphone-dialpad`:
  - Mostrar el dialpad (`show()`) únicamente cuando el estado de la llamada (`state.callState`) sea `connected`.
  - Ocultar el dialpad (`hide()`) en cualquier otro estado (`idle`, `calling`, `ringing`).
- Exponer el método `sendDTMF` en el retorno público de `WebPhone`.
- En los scripts de inicialización de jQuery en `agent_console.tpl` y `login_agent.tpl`:
  - Registrar el listener para los clics en `.dialpad-btn`: llamar a `WebPhone.sendDTMF(tone)`.
  - Registrar el listener de `keydown` en el document para interceptar teclas 0-9, * y #. Si la llamada está conectada y el usuario no está enfocado en otros inputs de texto (ej. contraseña de login), enviar el tono DTMF y activar visualmente el botón agregando/removiendo la clase `.active`.

## Restricciones y Trampas Conocidas
- **type="button":** Los botones del dialpad deben tener explícitamente `type="button"`. Si se omite, los navegadores los interpretan como `type="submit"` y al hacer clic en el dialpad en la pantalla de login, se enviará el formulario de inicio de sesión cortando la llamada.
- **Interferencia de Teclado:** Evitar interceptar pulsaciones del teclado físico si el agente está escribiendo en campos de búsqueda, entradas de chat, campos de usuario/contraseña, etc. Validar siempre `document.activeElement` antes de disparar `sendDTMF` desde el teclado físico.
- **SIP.js sendDTMF support:** En SIP.js (especialmente v0.20.0 y superiores), el objeto de sesión no cuenta con el método `.sendDTMF`. Se debe utilizar `session.sessionDescriptionHandler.sendDtmf(tone)` (con 'f' minúscula para RTP) o, como alternativa de respaldo, enviar un SIP INFO mediante `session.info()`.
- **Actualización idempotente del Script:** Si ya existe una versión antigua/incorrecta de `sendDTMF` en `sip-phone.js`, el script de Python debe buscarla y reemplazarla con la versión robusta utilizando expresiones regulares en lugar de solo saltarse la inserción.

