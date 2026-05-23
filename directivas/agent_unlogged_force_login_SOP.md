# SOP - Filtrar Extensiones y Forzar Inicio de Sesión de Agente

## Objetivo
1. Ocultar del panel de monitoreo a los agentes que no están logueados y cuya extensión física no está registrada/activa en Asterisk, reduciendo ruido visual.
2. Listar únicamente a los agentes activos (sesión iniciada) o inactivos (sesión no iniciada) pero que tengan su extensión registrada/activa en Asterisk.
3. Permitir que el supervisor inicie la sesión del agente (Login) directamente desde el menú contextual haciendo clic izquierdo sobre las filas de agentes en estado "No logon".

## Entradas y Salidas
- **Entradas:**
  - El listado de miembros de campañas/colas recuperados del ECCP.
  - La verificación de registro de la extensión en Asterisk (`extensionEstaRegistrada`).
- **Salidas:**
  - Tabla de agentes filtrada mostrando únicamente agentes logueados o agentes con extensión activa.
  - Petición AJAX (POST) a `index.php` con la acción `forceLoginAgent` para iniciar sesión.

## Lógica y Pasos

### 1. Filtrado de Agentes No Registrados en el Backend PHP (`index.php`)
- En `modules/campaign_monitoring/index.php`:
  - Al cargar los detalles de campaña (`manejarMonitoreo_getCampaignDetail`): Iterar sobre los agentes devueltos por `leerEstadoCampania()` y eliminar (`unset`) a los agentes cuyo estado es `offline` y cuya extensión no está registrada (`!$oPaloConsola->extensionEstaRegistrada(...)`).
  - Al procesar el estado en tiempo real (`manejarMonitoreo_checkStatus`): Realizar la misma depuración sobre `$estadoCampania['agents']` al inicio del ciclo de chequeo.
  - En la recepción del evento `queuemembership` dentro de `checkStatus`: Si el agente nuevo ingresado a la cola está `offline` y su extensión no está registrada, no agregarlo a la lista del cliente.

### 2. Implementación de la Acción AJAX de Login (`index.php`)
- En `modules/campaign_monitoring/index.php`:
  - Añadir la acción `forceLoginAgent` en el switch principal de peticiones AJAX.
  - Implementar la función `manejarMonitoreo_forceLoginAgent($module_name, $smarty, $sDirLocalPlantillas)`:
    - Leer el parámetro `agentchannel`.
    - Instanciar `PaloSantoConsola($agentChannel)` y ejecutar el método `loginAgente($agentChannel)`.
    - Retornar respuesta JSON.

### 3. Actualización de la Plantilla HTML (`informacion_campania.tpl`)
- En `modules/campaign_monitoring/themes/default/informacion_campania.tpl`:
  - Añadir la etiqueta de enlace `#btnForceLoginAgent` dentro del menú contextual `#agentContextMenu`.

### 4. Controlador JavaScript del Cliente (`javascript.js`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`:
  - En el manejador del clic sobre las filas de la tabla de agentes, verificar si el estado corresponde a no logueado ("no logon", "logged out", "no logoneado").
  - Si es así, mostrar el botón de "Iniciar Sesión" (`#btnForceLoginAgent`) y ocultar el botón de descanso.
  - Implementar el evento `click` sobre `#btnForceLoginAgent` que realice el POST a `forceLoginAgent` e inhabilite el botón mientras se procesa.

### 5. Estilos en styles.css
- En `modules/campaign_monitoring/themes/default/css/styles.css`:
  - Configurar las reglas de cursor pointer y hover para las filas cuyo atributo `data-status` contenga palabras clave como "logon" o "logoneado".

## Restricciones y Trampas Conocidas
- **Verificación Ligera de Conexión ECCP:** El método `loginAgente` de `PaloSantoConsola` requiere inicializar una conexión ECCP temporal asociada al agente. Si no se puede autenticar (por ejemplo, contraseña de agente no configurada), retornará falso y se mostrará un mensaje de alerta descriptivo en el navegador.
