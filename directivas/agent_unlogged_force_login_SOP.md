# SOP - Filtrar Extensiones y Forzar Inicio de Sesión de Agente (con Auto-Login)

## Objetivo
1. Ocultar del panel de monitoreo a los agentes que no están logueados y cuya extensión física no está registrada/activa en Asterisk, reduciendo ruido visual.
2. Listar únicamente a los agentes activos (sesión iniciada) o inactivos (sesión no iniciada) pero que tengan su extensión registrada/activa en Asterisk.
3. Permitir que el supervisor inicie la sesión del agente (Login) directamente desde el menú contextual haciendo clic izquierdo sobre las filas de agentes en estado "No logon".
4. Permitir que la consola del agente (`agent_console`) detecte automáticamente si el agente ha sido logueado remotamente por el supervisor, realizando la transición de pantalla de manera transparente.

## Entradas y Salidas
- **Entradas:**
  - El listado de miembros de campañas/colas recuperados del ECCP.
  - La verificación de registro de la extensión en Asterisk (`extensionEstaRegistrada`).
  - La extensión del usuario web actual de la sesión de Issabel.
- **Salidas:**
  - Tabla de agentes filtrada mostrando únicamente agentes logueados o agentes con extensión activa.
  - Petición AJAX (POST) a `index.php` con la acción `forceLoginAgent` para iniciar sesión.
  - Redirección automática y actualización de la sesión de Call Center del agente al detectar inicio de sesión remoto.

## Lógica y Pasos

### 1. Filtrado de Agentes No Registrados en el Backend PHP (`index.php` de `campaign_monitoring`)
- En `modules/campaign_monitoring/index.php`:
  - Al cargar los detalles de campaña (`manejarMonitoreo_getCampaignDetail`): Iterar sobre los agentes devueltos por `leerEstadoCampania()` y eliminar (`unset`) a los agentes cuyo estado es `offline` y cuya extensión no está registrada (`!$oPaloConsola->extensionEstaRegistrada(...)`).
  - Al procesar el estado en tiempo real (`manejarMonitoreo_checkStatus`): Realizar la misma depuración sobre `$estadoCampania['agents']` al inicio del ciclo de chequeo.
  - En la recepción del evento `queuemembership` dentro de `checkStatus`: Si el agente nuevo ingresado a la cola está `offline` y su extensión no está registrada, no agregarlo a la lista del cliente.

### 2. Implementación de la Acción AJAX de Login (`index.php` de `campaign_monitoring`)
- En `modules/campaign_monitoring/index.php`:
  - Añadir la acción `forceLoginAgent` en el switch principal de peticiones AJAX.
  - Implementar la función `manejarMonitoreo_forceLoginAgent(...)`:
    - Leer el parámetro `agentchannel`.
    - Instanciar `PaloSantoConsola($agentChannel)` y ejecutar el método `loginAgente($agentChannel)`.
    - Retornar respuesta JSON.

### 3. Detección de Auto-Login en el Backend PHP (`index.php` de `agent_console`)
- Implementar la función auxiliar `_verificarYAutoLogonear($module_name, $autoStartSession = false)`:
  - Obtener la extensión SIP del usuario web actual desde la ACL.
  - Buscar la extensión dinámica (`PJSIP/ext` o similar) en la lista de agentes.
  - Consultar el estado en Asterisk mediante `estadoAgenteLogoneado()`.
  - Si el estado final es `logged-in` y `$autoStartSession` es verdadero, actualizar las variables de sesión del Call Center (`estado_consola` a `logged-in`, `agente`, `agente_nombre`, `extension`).
  - Retornar si el agente está logueado o no.
- En `manejarLogin()`:
  - Si la acción está vacía (carga inicial de la página), llamar a `_verificarYAutoLogonear($module_name, true)`. Si retorna verdadero, redirigir inmediatamente a la consola del agente para pasar de pantalla.
  - Añadir la acción `checkAutoLogin` que invoca a `manejarLogin_checkAutoLogin($module_name)` para responder la petición AJAX de polling de la pantalla de login.

### 4. Controlador JavaScript y Polling (`javascript.js` de `agent_console`)
- En `modules/agent_console/themes/default/js/javascript.js`:
  - Definir la función `start_check_autologin()` que realiza un `$.post` con la acción `checkAutoLogin` cada 3 segundos.
  - Si la respuesta es exitosa (`response.status === true`), recargar la página (`window.location.reload()`) para iniciar sesión automáticamente.
  - Iniciar el polling en el `$(document).ready(...)` si se detecta que el botón `#submit_agent_login` existe en pantalla (evitando consultar si ya se inició sesión o si el modal de espera de login ya está activo).

## Restricciones y Trampas Conocidas
- **Verificación Ligera de Conexión ECCP:** El método `loginAgente` de `PaloSantoConsola` requiere inicializar una conexión ECCP temporal asociada al agente. Si no se puede autenticar, retornará falso.
- **Evitar Colisión de Polling:** El bucle de auto-login no debe correr si el agente ya presionó manualmente el botón "Ingresar" y el spinner de espera del login manual está visible en la interfaz, para evitar sobreescribir o interferir con el flujo de espera nativo.
