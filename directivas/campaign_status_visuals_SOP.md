# SOP - Indicador Visual de Estado de Campañas en Monitoreo

## Objetivo
1. Facilitar la identificación rápida del estado de cada campaña (Activa, Inactiva, Terminada) en la lista desplegable de selección de campañas.
2. Incorporar un guiño visual (código de color por estado) y un emoticón de estado (🟢, 🟡, 🔴) en cada elemento del dropdown en la consola de monitoreo de campañas (`/index.php?menu=campaign_monitoring#/details/`).

## Entradas y Salidas
- **Entradas:**
  - Los estados de las campañas provistos por el backend ECCP a través de Ember.js (`status` = `A`/`active`, `I`/`inactive`, `T`/`finished`/`terminada`).
- **Salidas:**
  - Lista desplegable con prefijos de emoji (🟢, 🟡, 🔴, ⚪) y estilos de fondo/texto correspondientes a su estado.

## Lógica y Pasos

### 1. Definición del Formato de Etiquetas en el Modelo Ember (`App.CampaignSummary`)
- Modificar `modules/campaign_monitoring/themes/default/js/javascript.js`.
- Agregar un atributo computado `label_with_status` en la clase `App.CampaignSummary`:
  - Si el estado de la campaña es `A` o `active` o `activequeue`, anteponer el círculo verde `🟢 `.
  - Si el estado es `I` o `inactive`, anteponer el círculo amarillo `🟡 `.
  - Si el estado es `T` o `finished` o `terminada`, anteponer el círculo rojo `🔴 `.
  - Si es otro estado no identificado, anteponer el círculo blanco `⚪ `.

### 2. Creación de una Vista Especializada para el Select (`App.CampaignSelect`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`, heredar de `Ember.Select` y definir `App.CampaignSelect`.
- Personalizar el `optionView` heredando de `Ember.SelectOption` para enlazar clases CSS basadas en el estado del objeto (`campaign-status-active`, `campaign-status-inactive`, `campaign-status-finished`).

### 3. Actualización de la Plantilla HTML (`informacion_campania.tpl`)
- Modificar `modules/campaign_monitoring/themes/default/informacion_campania.tpl`.
- Cambiar la invocación de `Ember.Select` a `App.CampaignSelect`.
- Configurar el label de la opción a la propiedad computada con color/emoji (`content.label_with_status`).

### 4. Adición de Reglas CSS en styles.css
- Modificar `modules/campaign_monitoring/themes/default/css/styles.css`.
- Añadir reglas para dar formato de fondo y color a cada clase de opción de estado:
  - `.campaign-status-active` con fondo verde claro y texto verde oscuro.
  - `.campaign-status-inactive` con fondo amarillo claro y texto marrón/dorado.
  - `.campaign-status-finished` con fondo rojo/rosa claro y texto rojo oscuro.

## Restricciones y Trampas Conocidas
- **Compatibilidad de Navegadores con Estilos de Select/Option:** No todos los navegadores móviles o sistemas operativos heredan estilos complejos en elementos `<option>`. Por este motivo, el uso del prefijo Unicode/Emoji (🟢, 🟡, 🔴) en la etiqueta de texto es fundamental para asegurar la visibilidad en cualquier dispositivo o navegador.
- **Respeto a la Reactividad de Ember 1.5.1:** Asegurarse de que el uso de `label_with_status` y la clase personalizada no interfiera con la observación de `key_campaign` y la transición correcta a la ruta de detalles de la campaña seleccionada.
