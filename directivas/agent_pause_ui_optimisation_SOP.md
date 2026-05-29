# SOP - Optimización de Fluidez en Pausas y Descansos de Agente

## Objetivo
1. Mejorar la experiencia del usuario al activar o desactivar pausas/descansos (como "Gestión"), eliminando la sensación de retraso o bloqueo en la interfaz web de la consola del agente.
2. Implementar una actualización visual inmediata (Optimistic UI Update) al hacer clic en los botones de descanso, mostrando un estado de carga y bloqueando interacciones redundantes.
3. Restaurar correctamente los controles a sus estados normales si la petición al servidor falla.
4. Asegurar que cuando el bucle de eventos (Long Polling/SSE) confirme el cambio de estado, los botones se habiliten en su estado final definitivo.

## Entradas y Salidas
- **Entradas:** 
  - Clic en `.btn-quickbreak` (botones rápidos).
  - Clic en `#btn_togglebreak` (botón de descanso principal).
  - Clic en `#webphone-btn-gestion` (botón de gestión del WebPhone).
- **Salidas:**
  - Deshabilitación inmediata de todos los botones relacionados.
  - Actualización inmediata del texto a estados transitorios ("Pausando...", "Quitando...", "Procesando...").
  - Clases CSS añadidas al elemento en proceso (`state-loading`).
  - Habilitación del estado final cuando llega la respuesta exitosa o restauración de estado original ante fallos.

## Lógica y Pasos

### 1. Modificación de `javascript.js`

#### A. Función `do_break()`
- Antes de realizar la petición POST AJAX:
  - Deshabilitar todos los botones rápidos `.btn-quickbreak`.
  - Deshabilitar el botón principal `#btn_togglebreak` usando jQuery UI: `$('#btn_togglebreak').button('disable').children('span').text('Pausando...');`.
  - Si el descanso es de tipo "GESTION", identificar el botón de gestión del WebPhone `#webphone-btn-gestion` en el contexto activo (principal o PiP) y establecerlo en texto "Procesando..." y deshabilitarlo. Mark the corresponding `.btn-quickbreak` with the class `state-loading`.
- En caso de error de API (`respuesta.action == 'error'`) o de fallo de conexión (`.fail()`):
  - Habilitar nuevamente todos los `.btn-quickbreak` y remover clases temporales (`state-loading`).
  - Habilitar `#btn_togglebreak` con texto original "Descanso".
  - Habilitar `#webphone-btn-gestion` con texto original "Gestión".

#### B. Función `do_unbreak()`
- Antes de realizar la petición POST AJAX:
  - Deshabilitar el botón principal `#btn_togglebreak` y cambiar su texto a "Quitando...".
  - Identificar el botón de gestión del WebPhone `#webphone-btn-gestion` en el contexto activo y establecerlo en "Procesando..." y deshabilitarlo.
- En caso de error de API o de fallo de conexión:
  - Habilitar `#btn_togglebreak` con texto original "Fin Descanso".
  - Habilitar `#webphone-btn-gestion` con texto original "Fin Gestión".

#### C. Controladores de Eventos de Monitoreo (`breakenter` y `breakexit`)
- En el switch de eventos `manejarRespuestaStatus()`:
  - Caso `breakenter`: Asegurarse de re-habilitar el botón `#btn_togglebreak` con `$('#btn_togglebreak').button('enable');`. Re-habilitar también `#webphone-btn-gestion` (si aplica) con su texto final "Fin Gestión".
  - Caso `breakexit`: Asegurarse de re-habilitar el botón `#btn_togglebreak` con `$('#btn_togglebreak').button('enable');` y habilitar `#webphone-btn-gestion` con su texto final "Gestión".

### 2. Estilos CSS (`webphone.css`)
- Añadir la clase `.btn-quickbreak.state-loading`:
  - Fondo amarillo/naranja suave (`#ffc107`).
  - Cursor de espera (`wait`).
  - Transición suave.

## Restricciones y Trampas Conocidas
- **Interferencia de jQuery UI en botones:** El botón `#btn_togglebreak` es un widget jQuery UI Button. Para deshabilitarlo o cambiar su etiqueta, es crucial usar el framework correctamente (`.button('disable')` / `.button('enable')`), además de actualizar el `span` interno para el texto.
- **Acceso a elementos del PiP:** Los botones de WebPhone (`#webphone-btn-gestion`) pueden estar renderizados en el contexto principal del navegador o dentro del contexto de la ventana flotante (PiP). Siempre resolver el contexto activo usando:
  ```javascript
  var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
  ```
