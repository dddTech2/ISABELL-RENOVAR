# SOP - WebPhone Audio Fix (Voicemail/Buzón)

## Objetivo
Resolver el problema de silencio en el WebPhone cuando una llamada saliente no es contestada y es redirigida al buzón de voz (voicemail) de Asterisk.

## Entradas y Salidas
- **Entrada:** Evento de estado `Established` en SIP.js para llamadas salientes.
- **Salida:** Reproducción automática del audio del buzón de voz en el elemento `<audio>` remoto del navegador.

## Lógica y Pasos
1. **Acceder a la conexión WebRTC:** Obtener el objeto `RTCPeerConnection` desde el `sessionDescriptionHandler` de SIP.js.
2. **Prevenir Duplicación de Listeners:** Antes de agregar listeners, verificar si ya se han configurado en la conexión actual usando una bandera personalizada (ej. `pc._mediaAttached`).
3. **Escuchar Eventos de Pistas de Audio:** Agregar un event listener para el evento `track` del `RTCPeerConnection` (`pc.addEventListener('track', ...)`).
4. **Asignación Dinámica del Stream:** Cuando se reciba una pista:
   - Si el evento proporciona un Stream (`event.streams[0]`), asignarlo al `srcObject` del elemento `<audio>` remoto.
   - Si no proporciona un Stream, crear uno nuevo, agregar el track del evento, y asignarlo.
5. **Verificación de Receivers Existentes:** Mantener una búsqueda inicial en `pc.getReceivers()` para reproducir cualquier track que ya esté establecido en el momento de invocar la conexión.
6. **Llamar a Play:** Ejecutar `.play()` en el elemento de audio capturando cualquier excepción para evitar errores silenciosos en la consola.

## Restricciones y Trampas Conocidas
- **Políticas de Autoplay:** Los navegadores restringen la reproducción automática de audio si no hay interacción previa del usuario. La consola del agente requiere que el usuario haga clic para entrar, lo que cumple esta interacción.
- **Múltiples Llamadas a attachMedia:** El método `attachMedia` se llama en varias transiciones de estado. La bandera personalizada en `RTCPeerConnection` evita duplicar los manejadores de eventos.
