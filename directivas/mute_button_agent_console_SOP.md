# SOP - Botón de Silenciar (Mute) en la Consola de Agente

## Objetivo
1. Añadir un botón de Silenciar (Mute) en la interfaz del WebPhone dentro de la consola de agente (`agent_console`).
2. Permitir que el agente silencie y desactive el silencio de su micrófono durante una llamada activa.
3. Actualizar la interfaz visual del botón para indicar claramente el estado actual de silencio (Mute activo vs Mute inactivo).

## Entradas y Salidas
- **Entrada:** Interacción del usuario (clic en el botón de silenciar) durante el estado conectado de la llamada.
- **Salida:** 
  - Habilitación o deshabilitación del track de audio local (micrófono) a través del PeerConnection de WebRTC.
  - Modificación del estilo visual del botón en la interfaz (color y texto).
  - Restablecimiento automático al estado no silenciado cuando finalice la llamada.

## Lógica y Pasos

### 1. Interfaz de Usuario (HTML/TPL)
- Añadir un elemento `<button>` con ID `webphone-btn-mute` dentro del contenedor de botones del WebPhone (`webphone-buttons`) en el archivo de plantilla `agent_console.tpl`.
- El botón debe iniciar oculto (`style="display:none;"`) y tener la clase `webphone-btn webphone-btn-mute`.

### 2. Estilos Visuales (CSS)
- En `webphone.css`, definir los estilos para la clase `.webphone-btn-mute` (normal, hover, disabled).
- Definir estilos específicos para la clase activa `.webphone-btn-mute.muted` (por ejemplo, fondo amarillo/alerta para indicar que está silenciado).

### 3. Lógica de Negocio (JavaScript)
- En `sip-phone.js`, añadir una variable `muted` en el objeto `state` iniciada en `false`.
- En la función `updateUI()`, obtener la referencia al botón de mute (`$muteBtn`).
- Actualizar el estado visual del botón según el estado de la llamada:
  - En estado `connected`: mostrar el botón de mute y habilitarlo.
  - En estados `idle`, `calling`, `ringing`: ocultar el botón de mute y restablecer el estado de mute a `false` invocando `setMute(false)`.
- Implementar la función `setMute(muteVal)`:
  - Guardar el valor en `state.muted`.
  - Si hay una sesión activa (`currentSession`), acceder al `peerConnection` del `sessionDescriptionHandler`.
  - Recorrer los transmisores (`getSenders()`) y para aquellos tracks que sean de tipo `audio`, establecer su propiedad `enabled` en `!muteVal`.
  - Actualizar las clases CSS y el texto del botón (ej: texto "Silenciado" y clase `muted` si está silenciado; "Silenciar" y remover clase si no lo está).
- Implementar la función `toggleMute()` que alterna el valor de `state.muted` y llama a `setMute()`.
- Exponer los métodos `toggleMute` y `setMute` en el API público retornado por `WebPhone`.
- En `agent_console.tpl`, registrar el listener de clic para el botón de mute: `$('#webphone-btn-mute').on('click', function() { WebPhone.toggleMute(); });`.

## Restricciones y Trampas Conocidas
- **Reiniciar Estado:** Al terminar una llamada (`idle`), se debe asegurar que el mute se desactive (`setMute(false)`) para evitar que el agente inicie la siguiente llamada silenciado sin darse cuenta.
- **Acceso a PeerConnection:** Validar que `currentSession`, `sessionDescriptionHandler` y `peerConnection` no sean nulos antes de intentar manipular los tracks de audio locales para evitar errores de excepción JavaScript.
- **getSenders:** Utilizar `pc.getSenders()` que es compatible con navegadores modernos para silenciar solo el track de envío local, dejando intacto el audio entrante.
