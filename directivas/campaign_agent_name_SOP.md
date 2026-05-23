# SOP - Concatenar Nombre del Agente a su Extensión en Monitoreo

## Objetivo
1. Mostrar el nombre completo del agente junto a su extensión en la columna "Agente" de la tabla de agentes en la consola de monitoreo de campañas.
2. Evitar romper las dependencias internas de CSS y selectores JS que dependen del identificador de canal del agente (ej. `PJSIP/2002`).

## Entradas y Salidas
- **Entradas:**
  - El listado de agentes activos del ECCP.
  - La consulta a la tabla `agent` en la base de datos `call_center` para obtener la relación entre canal (extensión) y nombre del agente.
- **Salidas:**
  - Columna de la interfaz web que muestra: `Canal/Extensión - Nombre del Agente` (ej. `PJSIP/2002 - David Daza`), manteniendo la reactividad y las clases CSS intactas.

## Lógica y Pasos

### 1. Obtención de Nombres de Agentes en PHP (`index.php`)
- En `modules/campaign_monitoring/index.php`, dentro de `formatoAgente($agent)`:
  - Cargar estáticamente la lista de agentes usando `$oPaloConsola->listarAgentes()`.
  - Esta lista mapea el canal (ej. `PJSIP/2002`) a la cadena `"PJSIP/2002 - Nombre Agente"`.
  - Modificar el arreglo de salida de `formatoAgente` para incluir una nueva clave `'name'`. Si existe en el mapa de agentes, asignar el valor formateado; de lo contrario, usar el canal crudo.

### 2. Procesamiento del Nombre en Ember.js (`javascript.js`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`, al crear u organizar los objetos de agentes:
  - En la inicialización (`agents.add`): Asignar la propiedad `nombre` a `agente.name || agente.agent`.
  - En las actualizaciones (`agents.update`): Asignar la propiedad `nombre` a `agente.name || agente.agent`.
  - Dejar la propiedad `canal` con el canal crudo (ej. `PJSIP/2002`) para asegurar que `<tr {{bindAttr class="canal"}}>` genere la clase CSS exacta y `agentColor` / `agentUpdateColor` puedan ubicar los elementos del DOM.

### 3. Actualización de la Plantilla Smarty (`informacion_campania.tpl`)
- En `modules/campaign_monitoring/themes/default/informacion_campania.tpl`:
  - Cambiar el contenido de la primera celda (`<td>`) de la tabla de agentes de `{{canal}}` a `{{nombre}}`.

## Restricciones y Trampas Conocidas
- **Clases CSS e Identificadores de Canal:** El identificador del canal (ej. `PJSIP/2002`) se usa como clase CSS en la fila `<tr>` y es utilizado por selectores JS en el cliente para cambiar el color de fondo dinámicamente según el estado del agente. Si alteramos la propiedad `canal` (cambiándola por el nombre concatenado), el selector `getElementsByClassName` fallará debido a los espacios y caracteres especiales. Por tanto, se DEBEN mantener separados la propiedad `canal` (para lógica y CSS) y la propiedad `nombre` (exclusivamente para renderizado de texto).
