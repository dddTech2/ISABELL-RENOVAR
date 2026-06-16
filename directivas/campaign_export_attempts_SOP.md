# SOP - Exportar Historial Completo de Intentos de Llamada en CSV

## Objetivo
Implementar una opción para exportar un reporte detallado en formato CSV con el historial de todos los intentos de marcación (llamadas completadas, fallidas, reintentos) para múltiples campañas salientes a la vez, incluyendo el nombre de la campaña, datos clave del intento (número de intento, troncal, agente, estado de marcación, duración y fecha/hora) y **todos los atributos personalizados del contacto provenientes del CSV de carga (como Nombre, Cédula, Dirección, etc.)**. Para simplificar la lectura, el reporte se filtrará para mostrar únicamente los resultados finales de cada intento, omitiendo estados intermedios.

## Entradas y Salidas
- **Entrada:** Arreglo de IDs de campañas seleccionadas (`id_campaign[]`).
- **Salida:** Archivo CSV descargable conteniendo todos los registros correspondientes de la tabla `call_progress_log` combinados con los de `calls` y `campaign`, más sus respectivos atributos en columnas alineadas.

## Lógica y Pasos
1. **Modelos (`modules/campaign_out/libs/paloSantoCampaignCC.class.php`):**
   - Crear el método `getCampaignAttemptsData($campaign_ids)` que reciba un arreglo de IDs numéricos.
   - Ejecutar una consulta SQL parametrizada haciendo un `INNER JOIN` entre `call_progress_log`, `calls` y `campaign`, y un `LEFT JOIN` con `agent` para obtener los intentos.
   - **Filtro de simplificación y prevención de duplicados:** Para evitar registros redundantes de un mismo intento, se realiza un `INNER JOIN` con una subconsulta que agrupa los logs por llamada (`id_call_outgoing`) e intento (`retry`) obteniendo el identificador más reciente (`MAX(id)`):
      ```sql
      INNER JOIN (
          SELECT MAX(cpl2.id) AS max_id
          FROM call_progress_log cpl2
          INNER JOIN calls c2 ON cpl2.id_call_outgoing = c2.id
          WHERE cpl2.new_status IN ('Success', 'Failure', 'NoAnswer', 'Abandoned', 'ShortCall')
            AND c2.id_campaign IN ($placeholders)
          GROUP BY cpl2.id_call_outgoing, cpl2.retry
      ) sub ON cpl.id = sub.max_id
      ```
     Esto garantiza obtener exactamente una sola fila correspondiente al desenlace de cada intento de llamada.
   - Ejecutar una segunda consulta SQL para obtener todos los atributos de los contactos (`call_attribute`) cargados para las campañas seleccionadas.
   - Retornar una estructura con los resultados de ambas consultas (`ATTEMPTS` y `ATTRIBUTES`).

2. **Controlador (`modules/campaign_out/index.php`):**
   - **Modificar la Selección en la Grilla:** Cambiar la etiqueta HTML del selector en la primera columna de tipo `radio` a `checkbox` con el nombre `id_campaign[]`.
   - **Agregar Casilla "Seleccionar Todo":** Añadir una casilla en el encabezado de la columna para seleccionar/deseleccionar de forma masiva mediante JavaScript en línea.
   - **Soporte Multiselección en Procesamiento:**
     - Modificar la extracción de IDs de campaña al inicio de `listCampaign` para soportar arreglos de `id_campaign[]`.
     - Actualizar la lógica de "Eliminar" (`delete`) y "Cambiar Estado" (`change_status`) para que procesen en bucle (foreach) cada ID de campaña seleccionado en lugar de solo uno.
   - **Registrar la Acción Customizada:** Añadir `$oGrid->customAction(...)` para la tarea `csv_attempts`.
   - **Enrutar la Acción de Descarga:** Detectar cuando se pulsa el botón `csv_attempts` (mediante `$_POST['csv_attempts']`). Validar que haya al menos una campaña seleccionada. Si hay campañas seleccionadas, desviar el enrutador hacia la función `displayCampaignAttemptsCSV`.
   - **Implementar `displayCampaignAttemptsCSV`:** 
     - Recuperar los datos invocando a `$oCampaign->getCampaignAttemptsData($campaign_ids)`.
     - Organizar los atributos de contacto en un mapa asociativo agrupado por ID de llamada (`id_call`) y recopilar todos los nombres únicos de atributos (etiquetas) presentes en las campañas seleccionadas.
     - Generar el CSV con las cabeceras base (Nombre de Campaña, Teléfono Destino, Fecha & Hora, Número de Intento, Estado, Agente, Troncal, Duración) concatenadas con la lista de etiquetas de atributos únicos ordenados.
     - Por cada intento en el log, buscar su ID de llamada, alinear sus valores con las columnas de los atributos y escribir la fila en el CSV.
     - Forzar los headers HTTP de descarga para archivos de tipo `text/csv`.

3. **Localización (`modules/campaign_out/lang/es.lang` y `en.lang`):**
   - Añadir traducciones para las nuevas cadenas de textos de la acción y validación.

## Restricciones y Trampas Conocidas
- **Inyección SQL:** Validar con `ctype_digit` todos los IDs de campaña y utilizar marcadores de posición (`?`) en la consulta SQL dinámica (`IN (?, ?, ...)`).
- **Cero registros:** Si no hay intentos de marcación registrados para las campañas seleccionadas, el reporte debe retornar un CSV con el mensaje "No Data Found" o cabeceras con filas vacías.
- **Alineación de Atributos:** Dado que se pueden seleccionar múltiples campañas con diferentes estructuras de atributos cargados, se debe consolidar una lista global de cabeceras únicas y mapear los valores de forma segura, dejando celdas vacías `""` si una campaña no posee un atributo específico.
- **Filtro de Estados Finales:** Asegurarse de que los estados simplificados coincidan con los de finalización reales del dialer para no perder intentos no respondidos o fallidos.
- **Duración de Habla en Success:** En `call_progress_log`, los eventos de tipo `Success` se guardan en el momento exacto en que la llamada es contestada, por lo que su campo `duration` queda en `NULL` o `0`. Para obtener la duración de habla real de la llamada conectada, se debe utilizar la expresión `IF(cpl.new_status = 'Success', calls.duration, cpl.duration) AS duracion`.



