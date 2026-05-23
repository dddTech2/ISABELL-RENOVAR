# SOP - Finalizar Descanso de Agente desde Interfaz de Monitoreo

## Objetivo
1. Implementar un menú contextual emergente (popover) al hacer clic izquierdo en un agente en estado de descanso (pausa) en la tabla de monitoreo de campañas.
2. Permitir que el supervisor o coordinador finalice el descanso del agente desde la interfaz web, reactivándolo en la cola de llamadas.

## Entradas y Salidas
- **Entradas:**
  - Clic izquierdo sobre una fila (`<tr>`) en la tabla de agentes en monitoreo.
  - El canal del agente (`data-agent`) y el estado actual (`data-status`).
- **Salidas:**
  - Petición AJAX (POST) a `index.php` con la acción `forceUnbreakAgent`.
  - Actualización automática del estado del agente en pantalla a través de la reactividad del backend.

## Lógica y Pasos

### 1. Extensión del Backend en PHP (`index.php`)
- En `modules/campaign_monitoring/index.php`, agregar un nuevo caso en el procesamiento de eventos AJAX: `forceUnbreakAgent`.
- Implementar la función `manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $sDirLocalPlantillas)`:
  - Leer el parámetro `agentchannel` de la petición.
  - Instanciar `PaloSantoConsola($agentChannel)` y ejecutar el método `terminarBreak()`.
  - Retornar una respuesta JSON indicando éxito o error detallado.

### 2. Modificación de la Plantilla HTML (`informacion_campania.tpl`)
- En `modules/campaign_monitoring/themes/default/informacion_campania.tpl`:
  - En la tabla de agentes, agregar la clase `agent-table-wrapper` al contenedor `div.llamadas`.
  - En el elemento `<tr>` de la tabla de agentes, enlazar las propiedades del modelo de datos de Ember mediante `bindAttr` en atributos de datos (`data-agent="canal"` y `data-status="estado"`).
  - Añadir al final de la plantilla el contenedor HTML del menú contextual `#agentContextMenu`.

### 3. Lógica del Lado del Cliente en JavaScript (`javascript.js`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`:
  - Agregar un manejador delegado para el evento `click` sobre las filas de la tabla de agentes (`.agent-table-wrapper table tbody tr`).
  - Validar si el estado (`data-status`) del agente corresponde a una pausa o descanso.
  - Posicionar y mostrar el menú flotante en las coordenadas exactas del cursor (`event.pageX`, `event.pageY`).
  - Agregar el evento de cierre al hacer clic fuera del menú.
  - Implementar la petición AJAX (POST) al hacer clic en "Finalizar Descanso" e inhabilitar temporalmente la opción para evitar peticiones duplicadas.

### 4. Estilos Visuales del Menú Contextual (`styles.css`)
- En `modules/campaign_monitoring/themes/default/css/styles.css`:
  - Definir las reglas de estilo de `#agentContextMenu` usando efectos premium de fondo translúcido (`backdrop-filter: blur`), bordes sutiles y efectos de hover sobre los enlaces.
  - Añadir reglas de cursor pointer y efectos de brillo al pasar el mouse por encima de filas de agentes que estén en descanso para dar retroalimentación visual al usuario.

## Restricciones y Trampas Conocidas
- **Coincidencia de Estados en Clientes Multi-idioma:** Los estados pueden venir traducidos de acuerdo con el idioma configurado en la sesión de Issabel (ej. "En descanso", "On break", "En pause"). El validador en JavaScript de "agente en descanso" debe buscar palabras clave comunes como "descanso", "break", "pause" o "paused" de forma insensible a mayúsculas y minúsculas.
- **Peticiones Duplicadas:** Se debe deshabilitar temporalmente la acción en la UI tras el primer clic para evitar envíos múltiples si el usuario hace clic rápidamente varias veces.
