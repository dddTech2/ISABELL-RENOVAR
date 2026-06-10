# SOP - Notificación de Llamadas Perdidas (Directas y de Cola)

## Objetivo
1. Proporcionar alertas visuales (notificación tipo banner/toast) y auditivas (bip de llamada en espera) al agente cuando entra una llamada directa a su extensión pero es rechazada automáticamente por estar ocupado en otra llamada.
2. Hacer que esta alerta visual y auditiva funcione tanto en la pantalla de inicio de sesión (`login_agent.tpl`) como en la interfaz principal de la consola de agente (`agent_console.tpl`).
3. Añadir una pestaña de **"Llamadas Perdidas de Hoy"** en la consola de agente (`agent_console.tpl`) que liste las llamadas abandonadas hoy en las colas/campañas del agente y permita devolver la llamada (click-to-call) mediante el Webphone.

## Entradas y Salidas
- **Entradas:**
  - Evento de llamada entrante SIP (INVITE) recibido en el Webphone mientras `currentSession` está activa.
  - Registros de llamadas entrantes con estado `'abandonada'` en la base de datos `call_center` para las colas del agente actual.
- **Salidas:**
  - Tono de aviso corto (bip de llamada en espera) reproducido en los auriculares del agente.
  - Alerta visual en pantalla del agente indicando el intento de llamada y el número/nombre del remitente.
  - Pestaña de llamadas perdidas del día actualizada en tiempo real o periódicamente.

## Lógica y Pasos

### 1. Webphone - Alerta de Llamada Directa Ocupada (sip-phone.js)
- En `sip-phone.js`, dentro de la función `handleIncomingCall(session)`:
  - Cuando se detecta que ya existe `currentSession` activa, antes de llamar a `session.reject()`:
    - Extraer el identificador del llamante (número y nombre opcional).
    - Reproducir un tono de aviso corto (ej. bip de frecuencia 440Hz durante 200ms) usando la Web Audio API si está disponible.
    - Invocar un nuevo callback opcional `onCallRejectedBusy` pasándole la información del remitente.
- Asegurar que la reproducción del tono sea segura y no arroje excepciones si el AudioContext está suspendido.

### 2. Vinculación de Callbacks en la UI (agent_console.tpl & login_agent.tpl)
- En la inicialización de `WebPhone.init(...)` en ambos archivos:
  - Añadir la propiedad `onCallRejectedBusy: function(caller) { ... }`.
  - Dentro de la función, invocar a `mostrar_mensaje_error` para pintar el aviso en pantalla.
  - En `login_agent.tpl`, dado que `mostrar_mensaje_error` podría no estar globalmente definido igual que en la consola, usar el elemento `#login_msg_error` o un banner dinámico de alerta para notificar el intento de llamada perdida.

### 3. Pestaña de Llamadas Perdidas de Hoy (agent_console.tpl & index.php)
- En `agent_console.tpl`:
  - Agregar un elemento `<li>` en la navegación de pestañas de `#issabel-callcenter-cejillas-contenido` para la pestaña **"Llamadas Perdidas"** (`#tabs-missed-calls`).
  - Añadir el contenedor `div` correspondiente: `#tabs-missed-calls` con una tabla estilizada para listar los intentos.
- En `index.php`:
  - Implementar una acción `getMissedCalls` o integrar en `checkStatus` la obtención de las llamadas perdidas del día para las colas del agente.
  - La consulta SQL a `call_center` debe:
    - Identificar las colas/campañas a las que pertenece el agente.
    - Buscar en `call_entry` las llamadas de la fecha actual en estado `'abandonada'`.
    - Retornar campos como la hora de entrada (`datetime_entry_queue`), número del cliente (`callerid` o `phone`), y nombre de la campaña.
- En `javascript.js` (o en la plantilla):
  - Actualizar el contenido de la pestaña llamando a la acción de backend.
  - Cada fila debe incluir un botón de "Devolver llamada" (icono de teléfono) que cargue el número en el input `#webphone-number` y ejecute la llamada automáticamente.

## Restricciones y Trampas Conocidas
- **Formato de la llamada en espera (Beep):** El tono de aviso debe ser sutil (200ms a 300ms) y de volumen bajo para evitar molestar la llamada actual del agente.
- **Acceso a Base de Datos:** Las consultas a `call_entry` deben filtrarse estrictamente por el día de hoy (fecha actual) para mantener la consulta ultra rápida y no sobrecargar la base de datos MariaDB.
- **Click-to-Call en Login:** En la página de login no hay pestaña de llamadas perdidas de cola porque el agente no se ha logueado en las colas. Ahí solo aplican las alertas de llamadas directas del Webphone.
- **Conexión a Base de Datos en Backend:**
  - *Nota:* No usar conexiones crudas de `PDO` con credenciales de base de datos hardcodeadas (como `localhost`, `asterisk`, `asterisk`), porque esto causa un error de conexión (500 Internal Server Error) en servidores de producción donde los usuarios, contraseñas o hosts son diferentes.
  - *Solución:* En su lugar, utilizar siempre la clase wrapper nativa `paloDB` instanciada con la cadena DSN global de la configuración: `new paloDB($arrConf['cadena_dsn'])` y usar el método `$pDB->fetchTable(...)` con marcadores posicionales (`?`) para evitar fallos de portabilidad y de conexión.
  - *Manejo de Errores:* Envolver siempre la consulta en un bloque `try-catch` capturando tanto `Exception` como `Throwable` de PHP para evitar que cualquier error de base de datos devuelva un código HTTP 500 y en su lugar responda con un JSON limpio indicando la naturaleza del error.
