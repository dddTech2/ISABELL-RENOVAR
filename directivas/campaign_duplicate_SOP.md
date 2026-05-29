# SOP - Duplicar Campaña Saliente

## Objetivo
Implementar una opción en el listado de campañas salientes (`menu=campaign_out`) para duplicar una campaña seleccionada. El sistema copiará toda la configuración de la campaña original (fechas, horarios, troncal, cola, script, URLs y formularios asociados) y solicitará al usuario únicamente el nombre para la nueva campaña.

## Entradas y Salidas
- **Entrada:** ID de la campaña origen (`id_campaign`), Nuevo nombre de la campaña (`new_name`).
- **Salida:** Creación de un nuevo registro en la tabla `campaign` y réplica de relaciones en `campaign_form` en estado **Inactiva** (`estatus = 'I'`).

## Lógica y Pasos
1. Modificar `modules/campaign_out/index.php`:
   - Añadir la acción de envío `'duplicate'` al objeto de grilla `$oGrid`.
   - Interceptar la petición de duplicación y redirigir al formulario de nombre con la acción `duplicate_campaign`.
   - Definir la función `duplicateCampaign()` para renderizar el formulario.
   - Insertar la nueva campaña en la base de datos copiando las propiedades de la campaña origen e insertar sus respectivos formularios en `campaign_form`.
2. Crear la plantilla `modules/campaign_out/themes/default/duplicate.tpl` con el diseño premium para ingresar el nuevo nombre.
3. Actualizar los archivos de traducción en `modules/campaign_out/lang/es.lang` y `modules/campaign_out/lang/en.lang`.

## Restricciones y Trampas Conocidas
- La nueva campaña debe iniciarse como **Inactiva** (`I`) para permitir al administrador verificar los parámetros o cargar contactos antes de activarla.
- Validar siempre que el nuevo nombre no esté vacío y no exista previamente en la base de datos.
- Las tablas relacionadas como historial de llamadas (`calls`), grabaciones (`call_recording`), datos de formularios recolectados (`form_data_recolected`) e historial de progreso de llamadas (`call_progress_log`) **NO** deben ser duplicadas, ya que son específicas del historial operativo de la campaña origen.
