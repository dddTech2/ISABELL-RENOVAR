# SOP - Exportar Reporte de Datos de Campañas en CSV para Múltiples Campañas

## Objetivo
Implementar una opción para exportar un reporte detallado en formato CSV con los datos de las llamadas completadas y los campos de los formularios asociados para múltiples campañas salientes a la vez, consolidando columnas dinámicas de atributos personalizados y de campos de formulario.

## Entradas y Salidas
- **Entrada:** Arreglo de IDs de campañas seleccionadas (`id_campaign[]`).
- **Salida:** Archivo CSV descargable conteniendo todos los registros de contactos y sus respuestas a formularios de forma consolidada y alineada.

## Lógica y Pasos
1. **Controlador (`modules/campaign_out/index.php`):**
   - **Enrutar Acción de Descarga:** Detectar cuando se pulsa el botón `csv_data` por POST. Si hay campañas seleccionadas, enrutar a la función `displayCampaignCSV`.
   - **Implementar `displayCampaignCSV` (Consolidación Multicampaña):**
     - Recuperar los datos utilizando la función legacy `$oCamp->getCompletedCampaignData($id_campaign)` en un bucle para cada campaña seleccionada.
     - Recopilar todos los atributos personalizados únicos (columnas con índice >= 10 en la lista de etiquetas de la base).
     - Recopilar todos los campos de formulario únicos presentes en las campañas seleccionadas mapeados como `[Form: NombreFormulario] CampoLabel`.
     - Generar el CSV imprimiendo primero el encabezado consolidado.
     - Iterar sobre las filas de cada campaña seleccionada alineando los atributos personalizados y respuestas de formularios en la columna global correspondiente, dejando celdas vacías `""` si una campaña no posee ese atributo o formulario.
     - Forzar los headers HTTP de descarga para archivos de tipo `text/csv` y llamar a `exit;` para evitar código HTML basura.

2. **Localización (`modules/campaign_out/lang/es.lang` y `en.lang`):**
   - Añadir traducciones para las nuevas cadenas de textos de la acción `csv_data` y mensajes de validación.

## Restricciones y Trampas Conocidas
- **Alineación de Columnas:** Es crucial identificar correctamente el orden/índice de los atributos y campos de formulario en cada campaña de forma dinámica, ya que varían por campaña. Se debe usar `array_search` sobre las etiquetas locales para mapear el valor hacia la columna global correcta.
- **Evitar HTML en la Salida:** Terminar la ejecución del script con `exit;` inmediatamente después de volcar el contenido CSV para prevenir la inyección de footers o wrappers HTML de la plantilla de Issabel.
