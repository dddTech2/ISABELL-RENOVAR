# SOP - Autorrespuesta Forzada y Timbrado en WebPhone

## Objetivo
1. Configurar el WebPhone de la consola del agente para que la función de "Auto-Respuesta" esté siempre habilitada de manera predeterminada al iniciar sesión.
2. Deshabilitar la interacción del usuario con el control de Auto-Respuesta en la interfaz, impidiendo que el agente pueda desactivar la autorrespuesta.
3. Incrementar el tiempo de espera antes de la auto-respuesta de 500 milisegundos a 1000 milisegundos (1 segundo).
4. Asegurar que el tono de timbrado suene durante ese segundo de espera cuando ingrese una llamada para notificar auditivamente al agente.

## Entradas y Salidas
- **Entrada:** Carga e inicialización del WebPhone al ingresar el agente a la consola; recepción de llamada entrante.
- **Salida:**
  - Checkbox de Auto-Respuesta marcado e inicializado en `true` y deshabilitado (`disabled="disabled"`) al cargar la interfaz.
  - Temporizador de auto-respuesta establecido en 1000 ms.
  - Reproducción auditiva del ringtone durante 1 segundo antes de la contestación automática de la llamada.

## Lógica y Pasos

### 1. Forzar Autorrespuesta Activa al Cargar y Deshabilitar Edición (HTML/JavaScript)
- En `agent_console.tpl`, marcar el input checkbox `#webphone-autoanswer` como deshabilitado por defecto agregando el atributo `disabled="disabled"`.
- En `sip-phone.js`, modificar la función `loadAutoAnswerPreference()` para que fuerce siempre la auto-respuesta llamando a `setAutoAnswer(true)` y asegurando que el checkbox `#webphone-autoanswer` esté marcado (`prop('checked', true)`).
- En `webphone.css`, añadir estilos para reflejar que el interruptor está inactivo/bloqueado (ej: `cursor: not-allowed` y opacidad levemente reducida en `.webphone-toggle` cuando el input esté disabled).

### 2. Ajustar el Tiempo de Espera (JavaScript)
- En `sip-phone.js`, en el objeto de configuración inicial `config`, actualizar el valor de `autoAnswerDelay` a `1000` (1000 milisegundos).

### 3. Asegurar el Timbrado de Llamada Entrante (JavaScript)
- El sistema de llamadas entrantes ya invoca a `updateCallState('ringing')` el cual llama a `playRingtoneSound('incoming')`. Al incrementar el tiempo de autorrespuesta a 1000 ms, se asegura que el timbre sea claramente audible por un segundo antes de que la llamada sea contestada automáticamente por `answer()`.

## Restricciones y Trampas Conocidas
- **Deshabilitación visual y de interacción:** Asegurar que tanto el checkbox como el contenedor label impidan la interacción visual (usando `pointer-events: none` o `cursor: not-allowed`) para evitar confusión en el agente.
- **Políticas de Autoplay de los Navegadores:** El agente debe haber interactuado previamente con la consola (por ejemplo, al iniciar sesión) para que el `AudioContext` funcione y reproduzca el sonido de llamada entrante.
