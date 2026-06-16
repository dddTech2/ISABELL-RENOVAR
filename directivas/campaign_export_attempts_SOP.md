# SOP - Exportar Historial Completo de Intentos de Llamada en CSV

## Objetivo
Implementar una opción para exportar un reporte detallado en formato CSV con el historial de todos los intentos de marcación (llamadas completadas, fallidas, reintentos) para múltiples campañas salientes a la vez, incluyendo el nombre de la campaña y datos clave del intento (número de intento, troncal, agente, estado de marcación, duración y fecha/hora).

## Entradas y Salidas
- **Entrada:** Arreglo de IDs de campañas seleccionadas (`id_campaign[]`).
- **Salida:** Archivo CSV descargable conteniendo todos los registros correspondientes de la tabla `call_progress_log` combinados con los de `calls` y `campaign`.

## Lógica y Pasos
1. **Modelos (`modules/campaign_out/libs/paloSantoCampaignCC.class.php`):**
   - Crear el método `getCampaignAttemptsData($campaign_ids)` que reciba un arreglo de IDs numéricos.
   - Ejecutar una consulta SQL parametrizada haciendo un `INNER JOIN` entre `call_progress_log`, `calls` y `campaign`, y un `LEFT JOIN` con `agent`.
   - Retornar el arreglo de resultados.

2. **Controlador (`modules/campaign_out/index.php`):**
   - **Modificar la Selección en la Grilla:** Cambiar la etiqueta HTML del selector en la primera columna de tipo `radio` a `checkbox` con el nombre `id_campaign[]`.
   - **Agregar Casilla "Seleccionar Todo":** Añadir una casilla en el encabezado de la columna para seleccionar/deseleccionar de forma masiva mediante JavaScript en línea.
   - **Soporte Multiselección en Procesamiento:**
     - Modificar la extracción de IDs de campaña al inicio de `listCampaign` para soportar arreglos de `id_campaign[]`.
     - Actualizar la lógica de "Eliminar" (`delete`) y "Cambiar Estado" (`change_status`) para que procesen en bucle (foreach) cada ID de campaña seleccionado en lugar de solo uno.
   - **Registrar la Acción Customizada:** Añadir `$oGrid->customAction(...)` para la tarea `csv_attempts`.
   - **Enrutar la Acción de Descarga:** Detectar cuando se pulsa el botón `csv_attempts` (mediante `$_POST['csv_attempts']`). Validar que haya al menos una campaña seleccionada. Si hay campañas seleccionadas, desviar el enrutador hacia la función `displayCampaignAttemptsCSV`.
   - **Implementar `displayCampaignAttemptsCSV`:** 
     - Recuperar los datos de intentos invocando a `$oCampaign->getCampaignAttemptsData($campaign_ids)`.
     - Generar el CSV con las cabeceras: Nombre de Campaña, Teléfono Destino, Fecha & Hora, Número de Intento, Estado, Agente, Troncal, Duración.
     - Forzar los headers HTTP de descarga para archivos de tipo `text/csv`.

3. **Localización (`modules/campaign_out/lang/es.lang` y `en.lang`):**
   - Añadir traducciones para las nuevas cadenas de textos de la acción y validación.

## Restricciones y Trampas Conocidas
- **Inyección SQL:** Validar con `ctype_digit` todos los IDs de campaña y utilizar marcadores de posición (`?`) en la consulta SQL dinámica (`IN (?, ?, ...)`).
- **Cero registros:** Si no hay intentos de marcación registrados para las campañas seleccionadas, el reporte debe retornar un CSV con el mensaje "No Data Found" o cabeceras con filas vacías.
