# SOP - Exportar Todos los Contactos en Campaña Saliente

## Objetivo
Modificar la descarga de datos CSV de campañas salientes (`menu=campaign_out`) para exportar la lista completa de contactos que fueron cargados en la campaña, incluyendo aquellos que no han sido llamados (donde el campo `status` es `NULL` en la base de datos), en lugar de limitar el reporte únicamente a las llamadas realizadas o procesadas.

## Entradas y Salidas
- **Entrada:** ID de la campaña (`id_campaign`).
- **Salida:** Cadena de texto formateada en CSV que incluye el estado, los atributos personalizados y los datos de formularios de todos los contactos de la campaña.

## Lógica y Pasos
1. Modificar el archivo `modules/campaign_out/libs/paloSantoCampaignCC.class.php`.
2. En la función `getCompletedCampaignData($id_campaign)`:
   - Modificar la consulta `$sqlLlamadas` para remover la cláusula `AND (c.status='Success' OR c.status='Failure' OR c.status='ShortCall' OR c.status='NoAnswer' OR c.status='Abandoned')`. Esto permitirá seleccionar todas las llamadas asociadas a la campaña, incluso las que están pendientes (cuyo `status` es `NULL`).
   - Modificar la consulta `$sqlAtributos` para remover la misma cláusula de filtrado por estados. Esto asegura que se recuperen los atributos personalizados (como nombre, cédula, dirección, etc.) de todos los contactos cargados.
   - Modificar la consulta `$sqlDatosForm` para remover la misma cláusula de filtrado por estados.

## Restricciones y Trampas Conocidas
- Los contactos cargados que aún no se han marcado tendrán `c.status` como `NULL`. En el archivo CSV exportado, esto se representará como una cadena vacía `""`, lo cual es el comportamiento correcto para llamadas pendientes.
- El campo `number` del agente y la fecha/hora/duración de la llamada también saldrán vacíos en el CSV para los contactos no procesados.
