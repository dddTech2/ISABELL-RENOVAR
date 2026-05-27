# SOP - Redirección de Contexto WebRTC y Mitigación de Throttling en PiP

## Objetivo
1. Evitar la latencia y fallos en el establecimiento de llamadas de WebPhone cuando está activo en la ventana flotante (Picture-in-Picture, PiP) y la pestaña principal se encuentra en segundo plano.
2. Redirigir dinámicamente las llamadas WebRTC (`getUserMedia`, `RTCPeerConnection` y `AudioContext`) al contexto del `window.pipWindow` para que el navegador las trate como operaciones del primer plano.
3. Asegurar que las APIs originales se restauren limpiamente al cerrar la ventana PiP.
4. Ajustar el tiempo de espera de recopilación de candidatos ICE (`iceGatheringTimeout`) a 2000 ms en `sip-phone.js` para aumentar la confiabilidad en redes lentas o contextos en segundo plano.

## Entradas y Salidas
- **Entradas:** 
  - Apertura del Picture-in-Picture (`$('#webphone-btn-pip').on('click')`).
  - Cierre del Picture-in-Picture (`pagehide` event listener).
- **Salidas:**
  - Redirección de `navigator.mediaDevices.getUserMedia`, `window.RTCPeerConnection` y `window.AudioContext` / `window.webkitAudioContext` a la ventana PiP mientras dure activa.
  - Restauración de los métodos originales en la pestaña principal al cerrarse.
  - Incremento de `iceGatheringTimeout` a `2000` ms en `sip-phone.js`.

## Lógica y Pasos

### 1. Modificación de sip-phone.js
- Buscar `iceGatheringTimeout: 500` en la configuración del `UserAgent` y reemplazarlo por `iceGatheringTimeout: 2000`.

### 2. Modificación de Templates (agent_console.tpl y login_agent.tpl)
En la función que gestiona el evento click de `#webphone-btn-pip`:
- Justo después de crear `window.pipWindow = pipWindow`, aplicar el monkey patch en el objeto global `window` de la pestaña principal:
  - Guardar referencia original de `navigator.mediaDevices.getUserMedia` en `window.__originalGetUserMedia`.
  - Reemplazar `navigator.mediaDevices.getUserMedia` con una función que invoque `window.pipWindow.navigator.mediaDevices.getUserMedia` si `window.pipWindow` existe y está abierto.
  - Guardar referencia original de `window.RTCPeerConnection` en `window.__originalRTCPeerConnection`.
  - Reemplazar `window.RTCPeerConnection` con un constructor que retorne una instancia de `window.pipWindow.RTCPeerConnection`. Copiar el `.prototype` del constructor original para mantener compatibilidad si es necesario.
  - Si existen `window.AudioContext` o `window.webkitAudioContext`, guardar sus referencias originales y reemplazarlos con constructores que invoquen los constructores equivalentes del `pipWindow`.
- En el listener `pagehide` de la ventana PiP (donde se limpia la referencia al cerrarse):
  - Restaurar `navigator.mediaDevices.getUserMedia` desde `window.__originalGetUserMedia` y eliminar la propiedad temporal.
  - Restaurar `window.RTCPeerConnection` desde `window.__originalRTCPeerConnection` y eliminar la propiedad temporal.
  - Restaurar `window.AudioContext` y `window.webkitAudioContext` desde sus variables originales guardadas.

### 3. Automatización mediante Script de Python
- Crear el script `scripts/patch_webphone_pip_context_v2.py`.
- El script debe modificar de manera idempotente los tres archivos: `sip-phone.js`, `agent_console.tpl`, y `login_agent.tpl`.

## Restricciones y Trampas Conocidas
- **Autoplay y AudioContext:** Al redirigir el `AudioContext` a la ventana PiP, la interacción inicial del usuario con el botón PiP cuenta como interacción válida ("User Activation") permitiendo la reproducción de sonidos y el timbrado en el nuevo contexto del PiP sin restricciones de autoplay.
- **Herencia de Prototipos de RTCPeerConnection:** Al sobreescribir `window.RTCPeerConnection` en la ventana principal, se debe asociar el prototipo original (`window.RTCPeerConnection.prototype = window.__originalRTCPeerConnection.prototype`) para evitar fallos de comprobación de tipo e inconsistencias internas de la biblioteca SIP.js.
- **Escape de Llaves en Plantillas Smarty:** Al modificar plantillas `.tpl`, no incluir llaves literales `{` y `}` dentro de bloques de JS a menos que estén dentro de `{literal}` y `{/literal}`. Todo el script de inicialización está envuelto en `{literal}` por lo que no hay problema con llaves.
