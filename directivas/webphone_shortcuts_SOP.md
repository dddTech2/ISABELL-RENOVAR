# SOP - Atajos de Teclado y Pegado (Paste) en WebPhone

## Objetivo
1. Habilitar la función de pegado global (Ctrl+V) en el campo de número del WebPhone (`#webphone-number`) cuando el agente no esté escribiendo en otros campos de entrada de texto.
2. Permitir colgar o cancelar una llamada activa, saliente o entrante (en estado no ocioso / `!idle`) mediante la tecla `Escape` (Esc).
3. Asegurar que estas funcionalidades se apliquen tanto en la pantalla de inicio de sesión (`login_agent.tpl`) como en la consola de agente principal (`agent_console.tpl`).

## Entradas y Salidas
- **Entrada:**
  - Evento de teclado de pegado (`paste`) global o en el documento.
  - Evento de teclado `keydown` con la tecla `Escape`.
- **Salida:**
  - El texto copiado se asigna y enfoca en `#webphone-number`.
  - La llamada activa se cuelga/cancela/rechaza invocando `WebPhone.hangup()`.

## Lógica y Pasos

### 1. Intercepción de Pegado (Paste)
- Registrar un evento global de pegado en el document: `$(document).on('paste', ...)`.
- Validar si el campo del número del webphone `#webphone-number` existe y no está deshabilitado.
- Validar que el elemento activo (`document.activeElement`) no sea otra entrada de texto, área de texto, elemento seleccionable o editable (salvo `#webphone-number` mismo). Si es otra entrada, permitir el pegado nativo en ella.
- Obtener el texto del portapapeles a través de `e.originalEvent.clipboardData.getData('text')` (o compatible con navegadores).
- Limpiar el texto si es necesario (quitar espacios sobrantes) y asignarlo al valor de `#webphone-number`, luego dar foco a este input y prevenir el comportamiento predeterminado del pegado para evitar duplicaciones si el foco no estaba en el input.

### 2. Intercepción de Tecla Escape (Esc)
- Registrar un evento de `keydown` en el document: `$(document).on('keydown', ...)`.
- Capturar las teclas `Escape` o `Esc` (código de tecla 27).
- Verificar que el estado del WebPhone no sea ocioso (`WebPhone.getState().callState !== 'idle'`).
- Si se presiona `Escape` y hay llamada, llamar a `WebPhone.hangup()` y realizar `preventDefault()` para evitar comportamientos nativos no deseados en la página.

### 3. Modificación Automatizada (Script de Python)
- Crear el script `scripts/add_webphone_shortcuts.py` para automatizar la inserción de estos event listeners en `agent_console.tpl` y `login_agent.tpl`.
- El script debe buscar la sección de código donde se asocian otros eventos del WebPhone (por ejemplo, después de los eventos de clic del WebPhone o cerca del listener de keydown de DTMF) e insertar limpiamente el código JS.
- Ejecutar el script y validar que los archivos finales queden correctamente formados.

### 3. Recuperación del Foco en Estado Ocioso (Idle)
- Cuando el estado de la llamada pasa a no ocioso (ej. `calling`, `connected`), el campo `#webphone-number` se deshabilita, lo que hace que pierda el foco (blur) automáticamente en el navegador.
- Al colgar o cancelarse la llamada (`idle`), el campo se habilita nuevamente, pero no recupera el foco por sí solo, impidiendo que el usuario vuelva a presionar Enter de inmediato para reintentar la llamada.
- En `sip-phone.js` dentro del caso `idle` en `updateUI()`:
  - Verificar que el usuario no esté enfocado escribiendo en otro input o textarea (para no interrumpir su trabajo en otros formularios).
  - Si no está escribiendo en otro lado, aplicar `.focus()` al elemento `#webphone-number` para que pueda presionar Enter y marcar/reintentar la llamada inmediatamente.

## Restricciones y Trampas Conocidas
- **Pérdida de Foco por Input Deshabilitado:** Deshabilitar un input remueve el foco de forma nativa. Al rehabilitarlo en el estado `idle`, se debe restaurar el foco programáticamente a `#webphone-number` sólo si el foco activo actual (`document.activeElement`) no pertenece a otro campo editable o formulario de la consola del agente.
- **Escape de Llaves en Scripts de Python:** Al escribir scripts de Python (`scripts/*.py`) que insertan código JavaScript usando cadenas formateadas (f-strings), se deben duplicar obligatoriamente todas las llaves literales (`{{` y `}}`) de JavaScript (incluso fuera de los bloques de variables) para evitar errores de sintaxis (`SyntaxError: f-string: single '}' is not allowed`).
- **Evitar Colisiones de Pegado:** Si el agente está en medio de llenar un formulario de la consola o el campo de contraseña en el login, el pegado global NO debe robarse el texto ni asignarlo al WebPhone. El chequeo de `document.activeElement` es obligatorio.

- **Evitar Colisiones de Escape:** Si hay elementos modales nativos que se cierran con Escape, verificar que no interfiera negativamente, aunque la llamada tiene prioridad de colgado si no está ociosa.
- **Compatibilidad de Navegadores:** Usar `e.originalEvent.clipboardData` preferiblemente para jQuery, con caída a `e.clipboardData`.

