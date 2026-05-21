# SOP - Botones de Descanso Rápido (Quick Breaks) en Consola de Agente

## Objetivo
1. Evitar múltiples pasos para iniciar un descanso en la Consola de Agente (hacer clic en "Descanso", seleccionar tipo en el modal y confirmar).
2. Crear una fila adicional de descansos rápidos debajo de la barra de controles donde se muestre cada tipo de descanso como un botón de acción rápida.
3. Permitir que el agente inicie un descanso específico con un solo clic.
4. Deshabilitar los botones de descanso cuando el agente ya está en descanso, resaltando con una animación visual y un color distintivo el descanso que se encuentra activo.
5. Rehabilitar todos los botones cuando el agente sale del descanso.

## Entradas y Salidas
- **Entradas:**
  - Lista de descansos configurados (`$LISTA_BREAKS`) desde el backend de Issabel.
  - Clic del agente en uno de los botones rápidos de descanso.
- **Salidas:**
  - Ejecución de la acción de pausa (break) correspondiente mediante petición AJAX (POST).
  - Actualización del estado visual de la fila de descansos rápidos.

## Lógica y Pasos

### 1. Interfaz de Usuario (HTML/TPL)
- En `agent_console.tpl`, agregar un nuevo contenedor `<div id="issabel-callcenter-controles-break">` justo debajo del div de controles principales (`#issabel-callcenter-controles`).
- Dentro de este div, añadir un título/etiqueta descriptiva como `<span class="quickbreak-label">Descansos Rápidos:</span>`.
- Iterar sobre `$LISTA_BREAKS` utilizando la sintaxis de Smarty `{foreach from=$LISTA_BREAKS key=break_id item=break_name}` y renderizar un botón para cada opción:
  ```html
  <button type="button" class="btn-quickbreak" data-breakid="{$break_id}">{$break_name}</button>
  ```

### 2. Estilos Visuales (CSS)
- En `webphone.css`, agregar reglas para la fila de descansos rápidos y los botones:
  - `#issabel-callcenter-controles-break`: debe ocupar el 100% de la fila (`flex: 0 0 100%`), tener fondo claro, bordes redondeados y usar flexbox para alinear la etiqueta y los botones con espacio entre ellos (`gap`).
  - `.quickbreak-label`: etiqueta con fuente en negrita y color gris oscuro.
  - `.btn-quickbreak`: botones modernos, sin usar estilos pesados de jQuery UI, con color de fondo gris claro, bordes suaves y cursor de puntero.
  - `.btn-quickbreak:hover`: hover suave cambiando color de fondo.
  - `.btn-quickbreak:disabled`: opacidad y cursor no permitido.
  - `.btn-quickbreak.active-break`: fondo rojo/alerta para indicar que está activo, y animación de pulso (`break-pulse`) para llamar la atención del agente.

### 3. Lógica de JavaScript (`javascript.js`)
- **Eventos Click:**
  - Registrar evento de clic para `.btn-quickbreak`: al hacer clic, obtener el `data-breakid`, asignarlo al dropdown oculto del modal (`#break_select`) y ejecutar la función global de Issabel `do_break()`.
- **Inicio de Estado:**
  - En la función `initialize_client_state()`, si `estadoCliente.break_id` es diferente de `null`, recorrer los botones `.btn-quickbreak` y deshabilitarlos. Para el botón cuyo ID coincida con el break activo, agregarle la clase `.active-break`.
- **Eventos SSE/Polling:**
  - En el caso `'breakenter'`:
    - Deshabilitar todos los botones rápidos `.btn-quickbreak`.
    - Buscar el botón con el `breakid` correspondiente y añadirle la clase `.active-break`.
  - En el caso `'breakexit'`:
    - Remover la clase `.active-break` de todos los botones `.btn-quickbreak`.
    - Habilitar de nuevo todos los botones rápidos `.btn-quickbreak`.

## Restricciones y Trampas Conocidas
- **Interferencia de jQuery UI:** No aplicar `.button()` de jQuery UI a los botones rápidos si queremos mantener estilos puramente modernos e independientes, ya que jQuery UI inyecta clases css que pueden pisar nuestras reglas personalizadas.
- **Mantener Consistencia con el Dropdown:** Dado que `do_break()` lee el valor desde el dropdown `#break_select`, debemos asegurarnos de que antes de invocarlo actualicemos el valor de dicho dropdown con el break ID seleccionado.
