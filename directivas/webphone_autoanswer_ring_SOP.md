# SOP - Autorrespuesta Forzada y Timbrado en WebPhone

## Objetivo
1. Configurar el WebPhone de la consola del agente para que la función de "Auto-Respuesta" esté siempre habilitada de manera predeterminada y forzada en la interfaz principal de la consola (`agent_console.tpl`, después de ingresar).
2. Deshabilitar la interacción del usuario con el control de Auto-Respuesta únicamente en la consola principal (`agent_console.tpl`), impidiendo que el agente pueda desactivar la autorrespuesta después de iniciar sesión.
3. Permitir que el agente configure libremente la auto-respuesta en la pantalla de inicio de sesión (`login_agent.tpl`, antes de ingresar) según su preferencia.
4. Incrementar el tiempo de espera antes de la auto-respuesta de 500 milisegundos a 1000 milisegundos (1 segundo).
5. Asegurar que el tono de timbrado suene durante ese segundo de espera cuando ingrese una llamada para notificar auditivamente al agente.

## Entradas y Salidas
- **Entrada:** Carga e inicialización del WebPhone al ingresar el agente a la consola; recepción de llamada entrante.
- **Salida:**
  - Checkbox de Auto-Respuesta marcado e inicializado en `true` y deshabilitado (`disabled="disabled"`) al cargar la consola principal (`agent_console.tpl`).
  - Checkbox de Auto-Respuesta cargado según preferencia almacenada del usuario en la página de login (`login_agent.tpl`) sin bloquear su edición.
  - Temporizador de auto-respuesta establecido en 1000 ms.
  - Reproducción auditiva del ringtone durante 1 segundo antes de la contestación automática de la llamada.

## Lógica y Pasos

### 1. Forzar Autorrespuesta Activa al Cargar y Deshabilitar Edición (HTML/JavaScript)
- En `agent_console.tpl`, marcar el input checkbox `#webphone-autoanswer` como deshabilitado por defecto agregando el atributo `disabled="disabled"`. Además, en el script de inicialización llamar a `WebPhone.setAutoAnswer(true)` y marcar el checkbox para asegurar que siempre empiece activa.
- En `login_agent.tpl`, dejar el input checkbox editable (sin `disabled`) y permitir que cargue/guarde su preferencia usando localStorage de forma normal.
- En `sip-phone.js`, restaurar la función `loadAutoAnswerPreference()` para que cargue la preferencia de `localStorage` normalmente.
- En `webphone.css`, asegurar que la propiedad `pointer-events: none` y cursor `not-allowed` se apliquen al slider únicamente cuando el input esté deshabilitado (`input:disabled + .webphone-toggle-slider`).

### 2. Ajustar el Tiempo de Espera (JavaScript)
- En `sip-phone.js`, en el objeto de configuración inicial `config`, actualizar el valor de `autoAnswerDelay` a `1000` (1000 milisegundos).

### 3. Asegurar el Timbrado de Llamada Entrante (JavaScript)
- El sistema de llamadas entrantes ya invoca a `updateCallState('ringing')` el cual llama a `playRingtoneSound('incoming')`. Al incrementar el tiempo de autorrespuesta a 1000 ms, se asegura que el timbre sea claramente audible por un segundo antes de que la llamada sea contestada automáticamente por `answer()`.

## Restricciones y Trampas Conocidas
- **Deshabilitación visual y de interacción:** Asegurar que tanto el checkbox como el contenedor label impidan la interacción visual únicamente cuando el input esté deshabilitado, para evitar confusión en el agente.
- **Políticas de Autoplay de los Navegadores:** El agente debe haber interactuado previamente con la consola (por ejemplo, al hacer clic en el formulario de login o ingresar extensión) para que el `AudioContext` funcione y reproduzca el sonido de llamada entrante.

