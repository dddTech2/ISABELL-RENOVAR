# SOP - Mostrar ID y Ordenar Campañas Salientes por Recientes

## Objetivo
Modificar el módulo de campañas salientes (`menu=campaign_out`) para:
1. Listar primero las campañas más recientes (orden descendente por ID).
2. Mostrar el ID de cada campaña en la grilla del listado.

## Entradas y Salidas
- **Entradas:** Registros de la tabla `campaign` en la base de datos `call_center`.
- **Salidas:** Grilla del listado de campañas salientes ordenada descendentemente por ID, que incluye una columna "ID".

## Lógica y Pasos
1. **Modificar la consulta de campañas en la base de datos:**
   - Ubicar la función `getCampaigns` en `modules/campaign_out/libs/paloSantoCampaignCC.class.php`.
   - Modificar la cláusula `ORDER BY` para ordenar por `c.id DESC` en lugar de `c.datetime_init, c.daytime_init`.
2. **Modificar la interfaz de visualización (Grilla):**
   - Ubicar la función `listCampaign` en `modules/campaign_out/index.php`.
   - Agregar una nueva columna `'ID'` en el arreglo pasado a `$oGrid->setColumns()`.
   - Agregar el campo `$campaign['id']` en el arreglo `$arrData[]` en la posición correspondiente (justo después del radio button).

## Restricciones y Trampas Conocidas
- El radio button es la primera columna (`index 0`), por lo tanto, el ID de la campaña debe insertarse en el `index 1` en `$arrData[]` y la columna `'ID'` debe estar en la misma posición en `$oGrid->setColumns()`.
- Asegurar que no se rompa la alineación de las cabeceras de columnas con los datos de las filas.
