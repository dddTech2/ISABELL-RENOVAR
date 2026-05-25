# SOP - Dashboard de Monitoreo de Jornada de Agente (Agent Journey Dashboard)

## Objetivo
Transformar el módulo legacy `agent_journey` en un panel de control interactivo de alta calidad visual (modo oscuro, estilo premium con colores HSL vibrantes, gráficos y telemetría avanzada). Esto permitirá al supervisor extraer métricas clave del día o de un rango de fechas, ver la bitácora de eventos y recibir alertas de auditoría heurística basadas en datos de la central SIP, respetando en todo momento los filtros de búsqueda del módulo.

## Entradas y Salidas
- **Entradas (Base de datos MySQL `call_center`):**
  - Tabla `agent`: Telemetría e información básica de los agentes.
  - Tabla `audit`: Registro de inicios de sesión (logins), cierres de sesión (logouts) y pausas (breaks).
  - Tabla `calls`: Registro de llamadas salientes, duración y estado final ('Success', 'ShortCall', etc.).
  - Tabla `call_entry` / `queue_call_entry`: Registro de llamadas entrantes, colas y tiempos de conversación.
  - Tabla `break`: Tipos de pausa (gestión, almuerzo, etc.).
- **Filtros de Entrada (Formulario de Búsqueda):**
  - `date_start`: Fecha de inicio del reporte.
  - `date_end`: Fecha de fin del reporte.
  - `agent`: Agente específico a filtrar (o todos).
  - `holdincluded`: Si se incluyen las pausas de tipo Hold ('yes'/'no').
- **Salidas:**
  - Panel responsive HTML/CSS/JS inyectado con Smarty.
  - Endpoints de API en PHP (`index.php`) que devuelven JSON con los datos agregados aplicando los filtros seleccionados.
  - Gráficos interactivos generados en el frontend (usando Chart.js).

## Métricas Relevantes Identificadas
1. **Llamadas Salientes (Cards):** Total de llamadas realizadas y cuántas terminaron exitosamente ('Success') dentro del rango y filtro seleccionado.
2. **Eficacia / SLA (Cards):** Porcentaje de llamadas exitosas sobre el total de llamadas (meta objetivo: 70% o superior).
3. **Agentes Conectados (Cards):** Proporción de agentes logueados en relación al total de agentes registrados (si no se filtra un agente único).
4. **Duración Promedio (Cards):** T. promedio hablado por llamada.
5. **Tiempo en Pausa (Cards):** Tiempo total acumulado que los agentes han pasado en break.
6. **Distribución de Carga por Hora:** Volumen de llamadas y pausas iniciadas desglosadas por cada hora del rango de fechas.
7. **Resultado de Llamadas (Gráfico de Dona):** Distribución de llamadas en éxito, llamadas cortas (ShortCall, < 5 seg) y fallidas/cortadas.
8. **Proporción Hablado vs Pausas (Min):** Comparación de tiempo hablado versus tiempo en pausa por cada agente activo en el filtro.
9. **Monitoreo de Agentes Activos (Tabla):** Listado de agentes con sus extensiones, estado actual (si aplica para hoy), llamadas SLA y tiempo hablado acumulado.
10. **Bitácora de Eventos Recientes:** Listado cronológico de eventos registrados bajo los filtros actuales.
11. **Auditor de Operaciones (AI Alert Cards):** Heurísticas inteligentes adaptadas a los filtros.

## Lógica y Pasos

### 1. Definición del Backend PHP (`index.php` y `paloSantoAgentJourney.class.php`)
- En `index.php`:
  - Recoger los parámetros del formulario de filtros (`date_start`, `date_end`, `agent`, `holdincluded`).
  - Implementar la acción `getMetrics` que extrae el `$recordset` de `getAgentJourney` aplicando dichos filtros y lo procesa para retornar un JSON estructurado con toda la telemetría agregada.
  - Modificar `listadoAgentJourney()` para que inyecte la plantilla del dashboard y pase los filtros actuales como variables iniciales al frontend.

### 2. Integración de Filtros en las Consultas y Agregaciones
- Las agregaciones de métricas en el backend (totales, promedios, distribución horaria, resultados por agente) se realizarán a partir del `$recordset` filtrado devuelto por la consulta principal `getAgentJourney($date_start, $date_end, $idAgent, $bHoldIncluded)`.
- Si se filtra por un solo agente:
  - Las métricas del dashboard se enfocarán únicamente en dicho agente.
  - El gráfico "Hablado vs Pausas" mostrará el desglose individual de ese agente.
  - El total de agentes conectados se limitará a 1 / 1.

### 3. Diseño e Interfaz Frontend (`agent_journey.tpl` y `javascript.js`)
- Crear `themes/default/agent_journey.tpl` con estilo premium:
  - Formulario de filtros nativo de Issabel en la parte superior.
  - Grid con tarjetas de métricas principales.
  - Fila de gráficos (Distribución horaria, Dona de resultados de llamadas, Barras de comparación de agentes).
  - Tabla de monitoreo de agentes y bitácora de eventos con buscador y paginador integrados en el cliente.
  - Script AJAX que al presionar "Recargar" o cambiar los filtros realiza una petición POST con los datos del formulario y refresca dinámicamente los gráficos y métricas sin recargar toda la página.

## Restricciones y Trampas Conocidas
- **Huso Horario y Rangos de Fechas:** Las fechas del filtro deben convertirse correctamente de `dd Mmm yyyy` a `yyyy-mm-dd hh:mm:ss`.
- **Rendimiento con Grandes Volúmenes:** Si el rango de fechas seleccionado es muy amplio (ej. un mes completo), la agregación en PHP de miles de registros puede tardar. Se debe recomendar al usuario mantener rangos cortos (de 1 a 7 días) o mostrar un spinner de carga en el dashboard durante el procesamiento AJAX.
- **Gráficos Vacíos:** Si el filtro no devuelve registros, el script de frontend debe limpiar los gráficos y mostrar un mensaje descriptivo ("No hay datos para los filtros seleccionados") para evitar errores de renderizado de Chart.js.
- **Renderizado de Custom HTML:** La clase `paloSantoGrid` NO tiene un método `customHTML()`. Llamarlo causará un Error Fatal (HTTP 500) en PHP. Para renderizar un dashboard personalizado, simplemente retorna el HTML directamente desde la función `_moduleContent` (o de la función renderizadora invocada por esta) en lugar de utilizar `paloSantoGrid` para este propósito.
- **Bitácora Integrada:** Para no realizar otra petición completa al servidor, los últimos eventos se inyectan en el JSON payload inicial bajo la llave `recent_events` extraída del `$recordset` ya calculado, y se dibuja la tabla en el frontend.
- **Distinción Salientes:** Al contabilizar llamadas salientes, se separa estrictamente `OUTGOING_CALL` (campaña/marcador) de `MANUAL_OUTGOING` (tecleado manual) para auditar qué proporción de tiempo dedica el agente a gestión propia.
- **Formato de Tiempo en Gráficos:** Para que los gráficos de barra o líneas sean legibles, el frontend debe formatear los segundos de las agregaciones a **Minutos** (ej. `(segundos / 60).toFixed(1)`), ya que Chart.js no escala bien temporalmente cuando hay miles de segundos.
- **Estética Visual (Light Theme):** El dashboard de Journey debe priorizar una interfaz "Light" (clara), con fondos blancos o grises claros (`#f4f6f9`), bordes suaves y tarjetas con `box-shadow` limpios. No se recomiendan "Dark Modes" para este módulo por petición del usuario.
- **KPIs Avanzados:** El backend parsea el campo `event_detail` mediante expresiones regulares para derivar los estados de las llamadas (`Success`, `Busy`, `Failed`, etc.) y el tipo de descansos (`GESTION`, `LUNCH`). El cálculo de Contactabilidad (`Success` / `Total Intentos`), Tasa de Congestión, TMO y Llamadas Cortas se debe realizar basándose en estos sub-estados.
- **Vistas Dinámicas (2 Niveles):** Si la consulta devuelve exactamente 1 agente (filtrado en el formulario superior), JavaScript debe cambiar la vista del coordinador (Dashboard Global) a la vista de analítica del agente (Ficha Individual y Métricas de Desviación de TMO), garantizando que las métricas globales no confundan la vista individual.
- **Cálculo de Tiempo Libre (Idle Time):** El `Tiempo Libre` se calcula restando el Tiempo Hablado y el Tiempo en Pausa del `Tiempo de Login` total. Para sesiones activas (sin evento de `LOGOUT`), el backend inyecta una función `TIMEDIFF(NOW(), audit.datetime_init)` en el SQL de `LOGIN` para considerar los segundos acumulados de la sesión en curso.
