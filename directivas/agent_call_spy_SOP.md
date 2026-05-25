# SOP - Escucha de Llamadas en Tiempo Real (Call Spy / ChanSpy)

## Objetivo
1. Permitir a los coordinadores y supervisores escuchar en tiempo real las llamadas activas de los agentes que se encuentren en estado ocupado ("Busy", "Ocupado", "On Call" o similar).
2. Proporcionar una opción rápida `👂 Escuchar Llamada` en el menú contextual de los agentes para iniciar el monitoreo silencioso de la llamada.
3. Solicitar e intermediar la extensión del supervisor para originar la llamada de escucha y guardarla en el navegador (`localStorage`) para facilitar futuras escuchas.

## Entradas y Salidas
- **Entradas:**
  - Canal/Identificador del agente seleccionado (ej. `Agent/9002` o `PJSIP/2002`).
  - Extensión telefónica del supervisor (introducida en la interfaz).
- **Salidas:**
  - Petición AJAX POST a `index.php` con acción `spyAgent`.
  - Conexión AMI originando llamada de la extensión del supervisor a la función ChanSpy del agente (`<chanspy_code><agent_ext>`).

## Lógica y Pasos

### 1. Interfaz Gráfica y Menú Contextual (Template y JavaScript)
- **Modificación en template (`informacion_campania.tpl`):**
  - Agregar `<a href="#" id="btnSpyAgent">👂 Escuchar Llamada</a>` dentro del menú contextual `#agentContextMenu`.
- **Modificación en estilos (`styles.css`):**
  - Añadir cursor pointer y efectos de hover (`filter: brightness(1.1)`) para las filas de agentes cuyo estado contenga "busy", "ocupado", "oncall", "on call" u "occupé".
- **Modificación en controlador JS (`javascript.js`):**
  - En la delegación de clic sobre las filas de agentes:
    - Evaluar si el estado del agente contiene `"busy"`, `"ocupado"`, `"oncall"` o `"occupé"`.
    - Si es así, mostrar la opción `#btnSpyAgent` y ocultar las demás opciones del menú contextual (como unbreak y login). Mostrar el menú contextual en la posición del puntero.
  - En el manejador de clic sobre `#btnSpyAgent`:
    - Leer la última extensión de supervisor del `localStorage` (clave `supervisor_extension`).
    - Presentar un `prompt()` solicitando la extensión del supervisor y pre-llenándolo con el valor leído.
    - Si el usuario cancela o deja vacío, abortar la acción.
    - Validar que sea numérico. Si es correcto, guardarlo en `localStorage`.
    - Cambiar el texto del botón a "Conectando...".
    - Realizar un `$.post` con la acción `spyAgent` enviando los parámetros `agentchannel` y `supervisorext`.
    - Al recibir la respuesta: Ocultar el menú contextual, restaurar el texto a "👂 Escuchar Llamada" y mostrar una alerta (`alert()`) confirmando el éxito o reportando el error detallado.

### 2. Controlador Backend (PHP)
- **Modificación en controlador principal (`index.php`):**
  - Agregar el caso `spyAgent` al switch de peticiones AJAX en `_moduleContent()`.
  - Crear la función `manejarMonitoreo_spyAgent(...)` para procesar la petición:
    - Extraer y limpiar parámetros (`agentchannel`, `supervisorext`).
    - Obtener el número de extensión del agente a partir del canal usando expresiones regulares (ej. `/(\d+)/` o similar). Si no se puede extraer, retornar error.
    - Conectar al DSN de Asterisk en MySQL (`generarDSNSistema('asteriskuser', 'asterisk')`) para buscar el código de ChanSpy en la tabla `featurecodes` (normalmente de `modulename = 'core'` y `feature = 'chanspy'`). Si no se encuentra o la BD falla, usar `555` como fallback.
    - Cargar e instanciar `AGI_AsteriskManager` e iniciar conexión con las credenciales locales de AMI (`admin` y `obtenerClaveAMIAdmin()`).
    - Ejecutar la acción AMI `Originate` con:
      - `Channel`: `local/<supervisorext>@from-internal`
      - `Exten`: `<chanspy_code><agent_ext>` (ej. `5552002`)
      - `Context`: `from-internal`
      - `Priority`: `1`
      - `Async`: `true`
      - `CallerID`: `Escucha: Agente <agent_ext> <chanspy_code><agent_ext>`
    - Verificar la respuesta de la AMI y retornar JSON con `status` 'success' o 'error'.

## Restricciones y Trampas Conocidas
- **Extracción de la Extensión del Agente:** Ciertos canales de agentes dinámicos pueden no tener el formato exacto `Agent/XXX`. El regex de extracción debe ser robusto y soportar tanto `Agent/XXXX` como `PJSIP/XXXX`, `SIP/XXXX`, etc.
- **Canal Local para Supervisor:** Originar hacia `local/<ext>@from-internal` es más compatible que originar a `PJSIP/<ext>` o `SIP/<ext>` directamente, ya que permite llamar a la extensión independientemente de su tipo de dispositivo (SIP/PJSIP/IAX2/virtual).
- **Asincronía del Originate:** `Async` debe estar configurado como `true` para evitar retardos o bloqueos en la ejecución de la petición web mientras el supervisor contesta el teléfono.
