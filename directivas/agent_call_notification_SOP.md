# SOP - Notificaciones de Escritorio y Visuales para Llamadas Entrantes en Consola de Agente

## Objetivo
1. Implementar notificaciones de escritorio nativas del navegador (Web Notifications API) cuando entra una llamada en `?menu=agent_console`, aplicando tanto en la pantalla de login (`login_agent.tpl`) como en la consola de agente con sesión activa (`agent_console.tpl`).
2. Solicitar de forma limpia los permisos del navegador (`Notification.requestPermission()`) al interactuar o conectar el WebPhone.
3. Notificar llamadas recibidas a través de dos canales:
   - **Vía WebPhone (SIP WebRTC):** Al entrar en estado `ringing` (en login o consola activa).
   - **Vía Consola de Call Center (SSE / EventSource):** Al dispararse el evento `agentlinked` en la consola activa.
4. Al hacer clic en la notificación de escritorio, la ventana/pestaña del navegador se enfoca automáticamente (`window.focus()`).
5. Alterar temporalmente el título del documento (`document.title`) con un indicador visual (ej: `🔔 ¡LLAMADA ENTRANTE! - Issabel`) mientras la llamada esté sonando o activa.
6. Cerrar automáticamente la notificación de escritorio cuando la llamada se responda, finalice o se desconecte.

## Entradas y Salidas
- **Entrada:** Evento de llamada entrante SIP (`updateCallState('ringing')`) o evento SSE de enlace de agente (`agentlinked`).
- **Salida:**
  - Solicitud de permiso de notificaciones en el navegador si aún no ha sido concedido.
  - Notificación flotante de escritorio nativa de Windows/OS con el número de teléfono o CallerID del contacto.
  - Cambio del título del documento `document.title` con ícono de campana `🔔`.
  - Cierre automático de la notificación al cambiar de estado.

## Lógica y Pasos

### 1. Gestión de Permisos y Notificaciones de Escritorio en WebPhone (`sip-phone.js`)
- Definir las funciones globales o auxiliares en `WebPhone`:
  - `requestNotificationPermission()`: Solicita permisos si `window.Notification` existe y `Notification.permission === 'default'`.
  - `showDesktopNotification(title, body, icon)`: Muestra la notificación nativa si `Notification.permission === 'granted'`.
  - Configurar `notification.onclick` para llamar a `window.focus()` y cerrar la notificación.
  - Guardar referencia activa a `currentDesktopNotification` para poder cerrarla programáticamente con `.close()`.
- En la función `updateCallState(state, data)`:
  - Cuando `state === 'ringing'`, llamar a `showDesktopNotification()` con el título *"Llamada Entrante"* y el número/Caller ID del contacto.
  - Cuando `state === 'connected'`, `'ended'`, `'rejected'`, o `'idle'`, cerrar `currentDesktopNotification` y restaurar `document.title`.

### 2. Notificaciones en Consola de Call Center (`javascript.js`)
- En el manejador SSE del evento `'agentlinked'`:
  - Si el documento está oculto o desenfocado (`document.hidden`), mostrar la notificación de escritorio con el teléfono y datos del contacto/campaña.
  - Iniciar alerta visual en `document.title` (`🔔 ¡LLAMADA ENTRANTE! - Consola de Agente`).
- En los eventos de desconexión o finalización (`agentunlinked`, colgar), restaurar el título original de la página.

### 3. Solicitud de Permiso Temprano (`login_agent.tpl` y `agent_console.tpl`)
- Al cargar el script o al hacer clic en cualquier parte de la consola/formulario de login, intentar solicitar `Notification.requestPermission()` si está en estado `'default'`.

## Restricciones y Trampas Conocidas
- **Gestión de Permisos por Contexto Seguro (HTTPS):** La Web Notification API sólo funciona en contextos seguros (`https://`) o en `localhost`. En conexiones HTTP no seguras, `window.Notification` puede ser `undefined`. Es necesario validar `if ('Notification' in window)` para prevenir errores en consola en entornos de prueba HTTP.
- **Interacción Inicial Requerida (User Gesture):** Algunos navegadores (Chrome/Edge) bloquean `Notification.requestPermission()` si se ejecuta sin una interacción previa del usuario. Debe solicitarse tras el primer clic en la pantalla de login o al interactuar con la consola.
- **Asistente de Concentración (Focus Assist / No Molestar) en Windows 10/11:** Si Windows tiene activo el modo *"No Molestar"* o *"Asistente de concentración"*, el sistema operativo no muestra el banner flotante (toast popup) de Chrome en pantalla, sino que envía la notificación silenciosamente al Centro de Notificaciones de Windows (icono en la barra de tareas junto al reloj). Es fundamental verificar que el modo "No Molestar" esté desactivado en Windows para visualizar el banner emergente.
- **Ciclo de vida con Auto-Respuesta (Auto-Answer):** Si el WebPhone contesta la llamada automáticamente a los 1000 ms, la notificación se muestra durante el segundo de timbrado y se cierra al pasar a estado `connected`. Si el agente tiene la pestaña activa y enfocado el navegador, la alerta visual en `document.title` (`🔔 ¡LLAMADA ENTRANTE!`) servirá como señalización principal.
- **Cierre de Notificaciones:** Siempre cerrar la notificación activa al contestar o colgar, evitando acumular popups en el centro de notificaciones del sistema operativo.
