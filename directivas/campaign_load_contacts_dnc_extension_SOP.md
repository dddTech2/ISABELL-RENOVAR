# SOP - Validación de Columna Extension al Cargar Contactos de Campaña Saliente

## Objetivo
Al cargar contactos en una campaña saliente (`?menu=campaign_out&action=load_contacts`), detectar si el archivo CSV (o los atributos del contacto) contiene una columna denominada `extension` (evaluada de forma *case-insensitive*, ej: `extension`, `Extension`, `EXTENSION`). Si dicha columna está presente, los registros correspondientes deben guardarse obligatoriamente en la tabla `calls` con el campo `dnc = 1` (Do Not Call).

## Entradas y Salidas
- **Entrada:** Archivo CSV cargado desde la interfaz de administración de campaña saliente, o invocación del cargador con estructura de atributos.
- **Salida:** Inserción de registros en la tabla `calls` con la columna `dnc = 1` cuando exista la columna `extension`.

## Lógica y Pasos

1. **Actualizar `paloContactInsert.class.php` (`modules/campaign_out/libs/paloContactInsert.class.php`)**:
   - Modificar la función `insertOneContact($number, $attributes, $dncOverride = null)`.
   - Si `$dncOverride` es verdadero/no nulo o si en el arreglo `$attributes` existe algún atributo cuya etiqueta (`$attr[0]`) coincida con `'extension'` (*case-insensitive* vía `strtolower(trim($attr[0])) === 'extension'`), establecer `$iDNC = 1`.

2. **Actualizar el Cargador CSV `Uploader_CSV` (`modules/campaign_out/uploaders/CSV/index.php`)**:
   - En la función `addCampaignNumbersFromFile()`, durante el procesamiento de la primera línea de cabecera (`$iNumLinea == 1`), inspeccionar todos los nombres de columnas de la cabecera.
   - Si alguna cabecera coincide con `'extension'` (vía `strtolower(trim($header)) === 'extension'`), marcar la bandera `$hasExtensionCol = true`.
   - Al invocar `$inserter->insertOneContact($numero, $atributos, $hasExtensionCol ? 1 : null)`, pasar la bandera para forzar `dnc = 1` en todos los contactos importados del archivo.

## Restricciones y Trampas Conocidas
- La comparación debe ser estricta en el valor `'extension'`, pero insensible a mayúsculas/minúsculas y espacios en blanco alrededor (`strtolower(trim($col)) === 'extension'`).
- Debe revisarse la cabecera completa del archivo CSV antes del desplazamiento `array_shift()`, para no ignorar el caso en que la columna 0 sea la cabecera del número y también pudiera llamarse `extension`.
- Mantener la firma compatible en `paloContactInsert::insertOneContact` añadiendo el parámetro opcional `$dncOverride = null` para no romper llamadas existentes ni documentación del módulo.
