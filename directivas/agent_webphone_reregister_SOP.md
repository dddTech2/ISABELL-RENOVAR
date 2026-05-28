# SOP - Forzar Re-registro de WebPhone de Agente desde Monitoreo

## Objetivo
1. Permitir que el coordinador fuerce el re-registro del WebPhone de un agente que se encuentra en estado "Phone Off" (extensión no registrada) directamente desde el menú contextual del panel de Monitoreo de Campañas.
2. Hacer que la consola del agente (`agent_console`) detecte la petición de re-registro en tiempo real a través del polling de estado y ejecute la reconexión/registro del WebPhone (o recargue la página en su defecto).

## Entradas y Salidas
- **Entradas:**
  - El listado de agentes del panel de monitoreo y su estado de registro ("Phone Off").
  - Parámetro `agentchannel` de la fila seleccionada.
- **Salidas:**
  - Petición AJAX (POST) a `index.php` con la acción `reregisterWebphone` para activar la señal de re-registro.
  - Creación del archivo de bandera temporal `/tmp/webphone_register_<extension>.flag` en el servidor.
  - Envío del evento `force-webphone-register` en la respuesta JSON del polling de `checkStatus` de la consola del agente.
  - Ejecución de `WebPhone.reconnect()` o `window.location.reload()` en la interfaz del agente.

## Lógica y Pasos

### 1. Panel de Monitoreo (Backend PHP `index.php` de `campaign_monitoring`)
- Agregar la acción `reregisterWebphone` en el switch principal de peticiones AJAX.
- Implementar la función `manejarMonitoreo_reregisterWebphone(...)`:
  - Obtener el parámetro `agentchannel`.
  - Extraer el número de extensión utilizando una expresión regular (ej. de `PJSIP/3016` obtener `3016`).
  - Crear un archivo indicador temporal: `/tmp/webphone_register_<extension>.flag`.
  - Retornar una respuesta JSON indicando éxito.

### 2. Panel de Monitoreo (Frontend JS `javascript.js` de `campaign_monitoring` y Plantilla TPL)
- En `modules/campaign_monitoring/themes/default/informacion_campania.tpl`:
  - Agregar un elemento `<a>` dentro de `#agentContextMenu` con ID `btnReregisterWebphone` y texto "🔄 Re-registrar WebPhone".
- En `modules/campaign_monitoring/themes/default/js/javascript.js`:
  - Al abrir el menú contextual (`contextmenu` click handler), detectar si el estado del agente es "Phone Off" (usando `hasPhoneOff = statusLower.indexOf('phone off') !== -1`).
  - Si `hasPhoneOff` es verdadero, incluirlo en la condición de visibilidad del menú contextual y mostrar `#btnReregisterWebphone`. En caso contrario, ocultarlo.
  - Implementar el evento `click` para `#btnReregisterWebphone` que realice un POST AJAX a `index.php` con `action: 'reregisterWebphone'` y `agentchannel: agentChannel`.

### 3. Consola del Agente (Backend PHP `index.php` de `agent_console`)
- En `manejarSesionActiva_checkStatus(...)`:
  - Obtener la extensión actual del agente desde la sesión: `$sExtension = $_SESSION['callcenter']['extension']`.
  - Justo al principio del bucle `while` de polling (y opcionalmente antes del bucle), verificar si existe el archivo de bandera `/tmp/webphone_register_<extension>.flag`.
  - Si existe:
    - Borrar el archivo bandera utilizando `@unlink($flagFile)`.
    - Agregar un evento `'event' => 'force-webphone-register'` al arreglo `$respuesta`.
    - Romper el bucle (`break`) para enviar inmediatamente la respuesta al cliente.

### 4. Consola del Agente (Frontend JS `javascript.js` de `agent_console`)
- En `manejarRespuestaStatus(respuesta)`:
  - Dentro del switch `respuesta[i].event`, agregar el caso `force-webphone-register`.
  - En este caso, comprobar si el objeto global `WebPhone` está definido. Si lo está, invocar `WebPhone.reconnect()`. De lo contrario, forzar la recarga de la página con `window.location.reload()`.

## Restricciones y Trampas Conocidas
- **Permisos de Archivo en /tmp:** El archivo bandera debe poder ser escrito y borrado por el usuario del servidor web (ej. `asterisk` o `apache`). Como ambos procesos (supervisor y agente) corren bajo el mismo servidor web, esto no debería causar problemas siempre que se cree en `/tmp`.
- **Limpieza de Banderas Huérfanas:** Al arrancar o limpiar sesiones, no es necesario hacer una limpieza masiva de `/tmp` ya que los nombres de los archivos son específicos por extensión y se eliminan en cuanto son leídos.
