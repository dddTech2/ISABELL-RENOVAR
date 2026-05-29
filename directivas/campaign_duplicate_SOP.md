# SOP - Duplicar Campaña Saliente

## Objetivo
Implementar una opción en el listado de campañas salientes (`menu=campaign_out`) para duplicar una campaña seleccionada. El sistema copiará la configuración de la campaña original (troncal, contexto, script, URLs y formularios asociados) y permitirá al usuario configurar el nuevo nombre, el rango de fechas de ejecución, el horario diario, la cola asociada y la cantidad de intentos.

## Entradas y Salidas
- **Entrada:** ID de la campaña origen (`id_campaign`), Nuevo nombre de la campaña (`nombre`), Rango de fechas (`fecha_ini`, `fecha_fin`), Horario diario (`hora_ini_HH`, `hora_ini_MM`, `hora_fin_HH`, `hora_fin_MM`), Cola (`queue`), Intentos (`reintentos`).
- **Salida:** Creación de un nuevo registro en la tabla `campaign` y réplica de relaciones en `campaign_form` en estado **Inactiva** (`estatus = 'I'`).

## Lógica y Pasos
1. Modificar `modules/campaign_out/index.php`:
   - Añadir la acción de envío `'duplicate'` al objeto de grilla `$oGrid`.
   - Interceptar la petición de duplicación y redirigir al formulario de duplicación con la acción `duplicate_campaign`.
   - Definir la función `duplicateCampaign()` para inicializar los campos del formulario con la campaña original y renderizar el formulario.
   - Procesar el envío de duplicación, validar los rangos de fechas y horarios ingresados por el usuario, y realizar la inserción de la nueva campaña y sus formularios asociados.
2. Crear la plantilla `modules/campaign_out/themes/default/duplicate.tpl` con el diseño premium para ingresar el nuevo nombre y los campos editables.
3. Actualizar los archivos de traducción en `modules/campaign_out/lang/es.lang` y `modules/campaign_out/lang/en.lang`.

## Restricciones y Trampas Conocidas
- La nueva campaña debe iniciarse como **Inactiva** (`I`) para permitir al administrador verificar los parámetros o cargar contactos antes de activarla.
- Validar siempre que el nuevo nombre no esté vacío y no exista previamente en la base de datos.
- Validar que la fecha de inicio sea menor o igual a la fecha de fin, y si son iguales, que la hora de inicio sea menor a la hora de fin.
- Las tablas relacionadas como historial de llamadas (`calls`), grabaciones (`call_recording`), datos de formularios recolectados (`form_data_recolected`) e historial de progreso de llamadas (`call_progress_log`) **NO** deben ser duplicadas, ya que son específicas del historial operativo de la campaña origen.
