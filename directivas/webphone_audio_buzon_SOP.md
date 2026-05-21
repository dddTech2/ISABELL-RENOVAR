# SOP - WebPhone Audio & Call Errors Fix

## Objetivo
1. Resolver el problema de silencio en el WebPhone cuando una llamada saliente no es contestada y es redirigida al buzón de voz o a un mensaje de error/congestión (early media).
2. Mostrar mensajes legibles y amigables para el usuario (agente) cuando una llamada saliente falle debido a códigos de error SIP (ej. Número no existe 404, Línea ocupada 486, No disponible 480, Congestión 503, Solicitud incorrecta 400).
3. Mostrar en pantalla el estado "BUZÓN DE VOZ" en lugar de "EN LLAMADA" cuando la llamada sea contestada por el buzón de Asterisk.

## Entradas y Salidas
- **Entrada:** Respuesta provisional (1xx con SDP), respuesta de éxito (200 OK con cabeceras customizadas) o de rechazo (3xx-6xx) de la sesión de llamada saliente en SIP.js.
- **Salida:** 
  - Reproducción automática del audio de la llamada desde el primer instante en que se reciba señal del canal (Early Media).
  - Silenciado del tono artificial de timbrado apenas se reciba audio real.
  - Visualización del error amigable en el estado del WebPhone durante 5 segundos antes de retornar al estado "Registrado".
  - Visualización de "BUZÓN DE VOZ" en pantalla cuando se detecte la cabecera correspondiente.

## Lógica y Pasos

### 1. Conexión de Audio (Early Media y Buzón de Voz)
- **Configuración de llamada:** Añadir la opción `earlyMedia: true` en `InviterOptions` al crear la sesión saliente para habilitar el procesamiento inmediato de SDP provisionales en SIP.js.
- **Registro del Delegate del SDH:** Registrar el callback `onSessionDescriptionHandler(sdh, provisional)` en el delegado de la sesión inmediatamente después de crearla.
- **Asignación temprana:** Invocar a `attachMedia(sdh)` dentro de `onSessionDescriptionHandler` para enganchar el listener del evento `track` del `RTCPeerConnection` antes de que la sesión cambie de estado a `Established`.
- **Apagado del timbre artificial:** En `attachMedia()`, si se detecta que se recibe un track de audio remoto, invocar inmediatamente `stopRingtoneSound()` para apagar el pitido de espera simulado y permitir escuchar el audio de la troncal.

### 2. Control y Mapeo de Códigos de Error SIP
- **Callback onReject:** Pasar un objeto `requestDelegate` con el método `onReject(response)` al realizar la llamada (`invite()`).
- **Mapeo de Códigos:**
  - Código `404`: Mostrar "Número no existe (404)".
  - Código `486`: Mostrar "Línea ocupada (486)".
  - Código `480`: Mostrar "No disponible (480)".
  - Código `403`: Mostrar "Sin permisos (403)".
  - Código `400`: Mostrar "Número inválido (400)".
  - Código `503`: Mostrar "Congestión / Canales ocupados (503)".
  - Código `487`: Ignorar (es la cancelación normal cuando el usuario cuelga antes de contestar).
  - Otros códigos: Mostrar "Error [Código]: [Razón]".
- **Visualización:**
  - Guardar el error mapeado en una variable de estado temporal (`state.lastCallError`).
  - Actualizar la interfaz de usuario (`updateUI()`) para mostrar este texto sobre el estado.
  - Ejecutar un temporizador (`setTimeout`) de 5000 ms (5 segundos) para borrar `state.lastCallError` y retornar la pantalla a "Registrado".

### 3. Detección de Buzón de Voz en Pantalla
- **Callback onAccept:** Pasar un objeto `requestDelegate` con el método `onAccept(response)` al realizar la llamada (`invite()`).
- **Lectura de Cabeceras Custom:** En `onAccept(response)`, comprobar si la respuesta de éxito (200 OK) de la llamada contiene cabeceras personalizadas de Asterisk como `X-Voicemail` o `X-Asterisk-Voicemail`.
- **Lógica de Estado:**
  - Si el valor de dicha cabecera es `'yes'` o `'true'`, establecer `state.isVoicemail = true` en el estado del WebPhone y actualizar la interfaz (`updateUI()`).
  - En `updateUI()`, si el estado es `'connected'` e `isVoicemail` es `true`, mostrar `"BUZÓN DE VOZ"` en el texto de estado en lugar de `"EN LLAMADA"`.

## Restricciones y Trampas Conocidas
- **Código 487 (Request Terminated):** Siempre se genera cuando el emisor cancela la llamada. Debe ignorarse para que no aparezca como un error.
- **Interrupción de Temporizador:** Al realizar una nueva llamada, se debe limpiar `state.lastCallError` inmediatamente para borrar cualquier mensaje de error previo de la pantalla, así como reiniciar `state.isVoicemail = false`.
- **Configuración de Asterisk Requerida:** Para que esta detección en pantalla funcione, el dialplan de Asterisk debe estar configurado para inyectar la cabecera en el canal SIP antes de enviar la llamada al Buzón (ej: `PJSIP_HEADER(add,X-Voicemail)=yes`).
