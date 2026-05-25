# SOP - Corrección del Módulo Dash Agent Journey (HTTP 500)

## Objetivo
Resolver el error HTTP 500 que ocurre al intentar cargar el módulo `dash_agent_journey` en la interfaz web de Issabel PBX. Este error es causado por un conflicto en el nombre del módulo en su archivo de configuración y por errores de compilación de Smarty debido a la presencia de llaves `{}` en las secciones de estilos CSS y scripts JavaScript del archivo de plantilla.

## Entradas y Salidas
- **Entradas:**
  - Archivos del módulo `dash_agent_journey` en `modules/dash_agent_journey/`.
- **Salidas:**
  - Módulo `dash_agent_journey` funcional que carga correctamente en la interfaz de Issabel sin generar error HTTP 500.

## Lógica y Pasos

### 1. Corrección del Nombre del Módulo en Configuración
- Modificar el archivo `modules/dash_agent_journey/configs/default.conf.php`.
- Cambiar el valor de `$arrConfModule['module_name']` de `'agent_journey'` a `'dash_agent_journey'` para evitar colisiones con el módulo original.

### 2. Escape de Llaves de Smarty en Plantilla (CSS y JS)
- Modificar el archivo `modules/dash_agent_journey/themes/default/dash_agent_journey.tpl`.
- Envolver la sección `<style>` con etiquetas `{literal}` y `{/literal}` de Smarty para evitar que el compilador intente interpretar los selectores CSS.
- En la sección `<script>`:
  - Extraer la variable de Smarty `{$MODULE_NAME}` y asignarla a una variable de JavaScript global (por ejemplo, `var moduleName = '{$MODULE_NAME}';`) fuera de la etiqueta `{literal}`.
  - Envolver el resto del código JavaScript con las etiquetas `{literal}` y `{/literal}`.
  - Actualizar la referencia del parámetro `menu` dentro del objeto `URLSearchParams` para usar la variable de JavaScript `moduleName` en lugar del tag directo de Smarty.

### 3. Agregar Traducciones Faltantes
- Editar `modules/dash_agent_journey/lang/es.lang` para agregar la clave de traducción `"Dash Agent Journey" => "Dashboard de Jornada de Agente",`.
- Editar `modules/dash_agent_journey/lang/en.lang` para agregar la clave de traducción `"Dash Agent Journey" => "Dash Agent Journey",`.

## Restricciones y Trampas Conocidas
- **Smarty Syntax Error:** Cualquier bloque de código CSS o JavaScript que contenga llaves `{}` y sea renderizado por el motor Smarty sin estar envuelto en `{literal}` causará un error fatal en el renderizado de plantillas, resultando en un error HTTP 500.
