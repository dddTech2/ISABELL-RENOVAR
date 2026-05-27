# SOP - Botón de Descanso Rápido de Gestión en WebPhone

## Objetivo
1. Proporcionar un control rápido en la interfaz del WebPhone (tanto integrada como flotante/PiP) que permita al agente pausarse en el descanso "GESTION" (o reanudar) sin tener que cambiar de pestaña o volver a la ventana principal de Issabel.
2. Sincronizar dinámicamente el estado del botón ("Gestión" vs "Fin Gestión") en tiempo real con el estado de pausa del agente.

## Entradas y Salidas
- **Entradas:**
  - Clic en el botón `#webphone-btn-gestion` en el WebPhone.
  - Eventos de pausa en el agente (`breakenter`, `breakexit`, `initialize_client_state`).
- **Salidas:**
  - Envío de peticiones AJAX para pausar (`do_break`) o reanudar (`do_unbreak`).
  - Actualización de los estilos y textos del botón `#webphone-btn-gestion` en todos los contextos activos del WebPhone (principal y PiP).

## Lógica y Pasos

### 1. Interfaz de Usuario (HTML)
En `agent_console.tpl`:
- Agregar el botón `<button id="webphone-btn-gestion" class="webphone-btn webphone-btn-gestion" style="display:none;">Gestión</button>` dentro de `.webphone-buttons`.

### 2. Estilos (CSS)
En `webphone.css`:
- Agregar las clases:
  - `.webphone-btn-gestion`: color de fondo `#ff7675`, texto blanco.
  - `.webphone-btn-gestion:hover`: color de fondo `#ee5253`.
  - `.webphone-btn-gestion.active`: color de fondo `#d63031` y animación `break-pulse`.

### 3. Lógica de Interacción (JavaScript en agent_console.tpl)
En la sección literal de JS de `agent_console.tpl`:
- Asociar el evento click al botón `#webphone-btn-gestion`:
  - Buscar en la ventana principal el botón `.btn-quickbreak` que contenga el texto "GESTION" (usando `window.jQuery`).
  - Si no existe, mostrar un warning en la consola.
  - Si existe y ya estamos en un break, llamar a `do_unbreak()`.
  - Si existe y no estamos en break, cambiar el dropdown `#break_select` al ID de gestión y llamar a `do_break()`.

### 4. Sincronización en Tiempo Real (JavaScript en javascript.js y sip-phone.js)
- En `sip-phone.js` en `updateUI()`:
  - Si el WebPhone está registrado, mostrar el botón y evaluar si el `estadoCliente.break_id` corresponde al ID de descanso de gestión. Si es así, añadir la clase `.active` y cambiar el texto a "Fin Gestión"; de lo contrario, remover la clase y restablecer a "Gestión".
- En `javascript.js` en `initialize_client_state()`, `breakenter` y `breakexit` event cases:
  - Buscar el botón `#webphone-btn-gestion` en el contexto activo (principal o PiP) y actualizar su texto y clase activa según el evento recibido.

### 5. Automatización mediante Script de Python
- Crear el script `scripts/add_webphone_gestion_break.py` para aplicar estos cambios de manera limpia e idempotente.

## Restricciones y Trampas Conocidas
- **Detección Dinámica de ID de Gestión:** Dado que el ID numérico del descanso rápido "GESTION" puede variar en base de datos, siempre se debe buscar de forma dinámica por cadena de caracteres ("GESTION") en el DOM de la ventana principal para obtener el ID correcto.
- **Contexto del PiP Window:** Para buscar el botón de gestión en el JS de eventos SSE, utilizar el selector contextualizado:
  ```javascript
  var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
  var $gestionBtn = $('#webphone-btn-gestion', context);
  ```
