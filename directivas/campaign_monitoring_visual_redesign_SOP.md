# SOP - Rediseño Visual de Monitoreo de Campañas (Lavado de Cara)

## Objetivo
1. Modernizar la estética visual de la consola de monitoreo de campañas (`/index.php?menu=campaign_monitoring#/details/`) para brindar una experiencia de usuario premium, limpia y contemporánea.
2. Reemplazar las tablas grises planas y con bordes toscos por "Tarjetas" (Cards) con bordes redondeados, sombras suaves, espaciado generoso y la tipografía moderna 'Inter' de Google Fonts.
3. Sustituir las alertas de estado de agentes con colores extremadamente saturados (rojo, verde y amarillo chillones) por tonos pastel suaves y legibles que no cansen la vista ni generen ruido visual.

## Entradas y Salidas
- **Entradas:**
  - Hojas de estilo existentes en `modules/campaign_monitoring/themes/default/css/styles.css`.
  - Plantilla Smarty `modules/campaign_monitoring/themes/default/informacion_campania.tpl`.
  - Archivo JS de Ember `modules/campaign_monitoring/themes/default/js/javascript.js`.
- **Salidas:**
  - Interfaz rediseñada con tarjetas con sombras, bordes redondeados y tipografía 'Inter'.
  - Filas de agentes con colores de fondo pastel suaves correspondientes a sus estados.

## Lógica y Pasos

### 1. Actualización de Reglas CSS (`styles.css`)
- **Tipografía y Contenedor Principal:**
  - Importar Google Fonts `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');` al inicio de `styles.css`.
  - Aplicar `font-family: 'Inter', sans-serif;` a todo el contenedor `#campaignMonitoringApplication`.
  - Cambiar el color de fondo general de la aplicación a un gris azulado ultra suave `#f8fafc` para hacer resaltar las tarjetas blancas.
- **Cabeceras de las Tarjetas y Títulos (Ligeros y Elegantes):**
  - Cambiar el fondo de `.table-header` y `table.titulo` a un gris claro muy limpio `#f8fafc` con un borde inferior sutil `#e2e8f0`.
  - El texto de las cabeceras debe ser gris oscuro/carbón `#0f172a` (en lugar de blanco) para dar un aspecto más liviano y moderno de SaaS.
- **Estructura de Tarjetas (Cards) de Ancho Completo:**
  - Estructurar `.flex-container` con `width: 100% !important; gap: 24px !important;` para que las tarjetas de configuración, tiempos, contadores y estadísticas se extiendan a lo ancho y queden perfectamente alineadas con las tablas inferiores.
  - Quitar bordes colapsados nativos de las tablas `.campaign-table` y `.campaign-table-outgoing`.
  - Aplicarles `border-radius: 8px`, `box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05)`, y `border: 1px solid #e2e8f0`.
  - Usar `border-collapse: separate` y `border-spacing: 0` para permitir bordes redondeados y relleno interno en las tablas.
  - Añadir espaciado interno (padding) en celdas de cabecera y datos para dar respiro visual.
- **Secciones de Agentes y Llamadas:**
  - Dar el mismo aspecto de tarjeta a los contenedores `div.llamadas`.
  - **IMPORTANTE:** Definir `overflow-y: auto !important;` en `div.llamadas` para mantener habilitado el scroll vertical y evitar que la lista de agentes u otros registros se corten.
- **Clase de Llamadas Marcando:**
  - Añadir una clase `.dialing-call-row` con un color de fondo pastel azul `#e8f0fe` para eliminar el color cyan chillón del código HTML.

### 2. Limpieza de Plantilla (`informacion_campania.tpl`)
- Quitar todos los atributos `border="1"` en las etiquetas `<table>` del archivo `informacion_campania.tpl`.
- Reemplazar el estilo inline `style="background-color:#00e7ffa6"` por la clase CSS `.dialing-call-row` en la fila de llamadas marcando.

### 3. Suavizado de Colores de Alerta en JS (`javascript.js`)
- En `modules/campaign_monitoring/themes/default/js/javascript.js`, cambiar los colores de estado en las funciones `agentColor` y `agentUpdateColor`:
  - **Ringing:** Cambiar de `#a6db14` a `#e8f0fe` (azul suave/claro).
  - **Libre/Disponible:** Cambiar de `#01D50A` a `#e6f4ea` (verde pastel).
  - **Ocupado/Busy:** Cambiar de `yellow` a `#fef7e0` (amarillo/ámbar pastel).
  - **Paused/Break:** Cambiar de `orange` a `#fff0e6` (naranja pastel).
  - **No logon/Logged out:** Cambiar de `#f33` a `#fce8e6` (rojo pastel).

## Restricciones y Trampas Conocidas
- **Bordes Redondeados en Tablas:** En CSS, para que `border-radius` funcione correctamente en un elemento `<table>`, es indispensable definir `border-collapse: separate;` y `border-spacing: 0;`, de lo contrario los bordes no se redondean.
- **Herencia de Color en Textos:** Al usar fondos de color pastel (tonos muy claros), es crítico asegurar que el color de texto de las filas y celdas se mantenga oscuro (`#1e293b` o `#000000`) para garantizar la accesibilidad y el contraste de lectura.
