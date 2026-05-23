# SOP - Terminar Descanso de Agente desde Consola (CLI)

## Objetivo
1. Crear un script que pueda ser ejecutado por consola (CLI) en el servidor de Issabel.
2. Permitir que un coordinador o administrador fuerce el fin de descanso ("Fin Descanso") de un agente para regresarlo a la cola de llamadas.
3. Validar el funcionamiento de esta lógica directamente a través de ECCP antes de integrarla en la interfaz web.

## Entradas y Salidas
- **Entradas:**
  - Argumento por consola con el identificador del agente (ej. `PJSIP/2009`, `Agent/1001`, o simplemente el número de extensión `2009`).
- **Salidas:**
  - Mensaje de éxito indicando que el agente ha regresado a la cola de llamadas.
  - Mensaje de error detallado en caso de fallar (ej. conexión ECCP fallida, agente no encontrado o no está en descanso).

## Lógica y Pasos

### 1. Inicialización y Carga de Framework
- El script se debe ejecutar mediante PHP CLI en el servidor (ej. `php scripts/unbreak_agent.php`).
- Debe incluir las rutas de búsqueda para las librerías principales de Issabel (`libs/`, `modules/agent_console/libs/`).
- Cargar archivos de configuración global:
  - `libs/misc.lib.php`
  - `configs/default.conf.php`
  - `libs/paloSantoDB.class.php`
  - `modules/agent_console/libs/paloSantoConsola.class.php`

### 2. Procesamiento de Entrada (Identificador de Agente)
- Validar que se reciba el argumento del agente por consola.
- Si el argumento contiene una barra `/` (ej. `PJSIP/2009`), se asume el canal completo directamente.
- Si el argumento es puramente numérico (ej. `2009`), realizar una consulta a la base de datos `call_center` para encontrar el agente activo (`estatus = 'A'`) con ese número:
  ```sql
  SELECT type, number FROM agent WHERE number = ? AND estatus = 'A'
  ```
  Construir el canal combinando `type` y `number` (ej. `PJSIP/2009` o `Agent/2009`).

### 3. Ejecución de la Acción a través de ECCP
- Instanciar `PaloSantoConsola` con el canal del agente resuelto.
- Invocar el método `terminarBreak()` de la clase `PaloSantoConsola`.
- Este método de forma interna:
  1. Obtiene las credenciales del agente en la base de datos.
  2. Se conecta al demonio ECCP en `localhost:20005`.
  3. Autentica la conexión ECCP y la asocia al agente.
  4. Envía el comando `unpauseagent` a Asterisk / Dialer.
- Validar la respuesta:
  - Si es exitosa, mostrar mensaje de éxito en verde.
  - Si falla, mostrar el error devuelto en `$oConsola->errMsg`.

## Restricciones y Trampas Conocidas
- **Permisos de Ejecución:** El script CLI de PHP debe ejecutarse con un usuario que tenga acceso de lectura a `/etc/asterisk/manager.conf` y a las credenciales de la base de datos (típicamente `asterisk` o `root`).
- **Estado del Agente:** El agente debe estar logueado y en estado de descanso (pausa) para que el comando `unpauseagent` tenga efecto. Si el agente no está logueado, ECCP devolverá un error.
- **Formato del Agente:** Es importante admitir formatos mixtos para facilitar el uso del script por el coordinador sin requerir que conozca el tipo de canal exacto (SIP, PJSIP, Agent).
