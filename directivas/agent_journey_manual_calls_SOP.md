# SOP - Integración de Llamadas Manuales en el Recorrido del Agente (Agent Journey)

## Objetivo
Permitir que el módulo `agent_journey` muestre las llamadas manuales (tanto entrantes como salientes) que realizan o reciben los agentes directamente desde sus extensiones (sin usar el marcador predictivo). Esto proporcionará al coordinador una visión integral de toda la actividad de llamadas del gestor en una sola pantalla.

## Entradas y Salidas
- **Entradas:**
  - Tabla `asteriskcdrdb.cdr` (Centralita Asterisk): Registro general de llamadas en la base de datos de Asterisk.
  - Tabla `call_center.agent`: Listado de agentes registrados.
- **Filtros de Entrada:**
  - Rango de fechas (`date_start` y `date_end`).
  - Filtro por agente (`agent` ID o todos).
- **Salidas:**
  - Registros de eventos `'MANUAL_OUTGOING'` y `'MANUAL_INCOMING'` en el `$recordset` de `getAgentJourney`.
  - Duración de la llamada y detalle del destino/origen presentados en la tabla del panel de Journey.

## Lógica y Pasos

### 1. Modificación de la Consulta en la Librería PHP
- Editar `modules/agent_journey/libs/paloSantoAgentJourney.class.php` -> `getAgentJourney()`.
- Agregar dos subconsultas SQL que extraigan llamadas manuales de `asteriskcdrdb.cdr`:
  - **Manuales Salientes (`MANUAL_OUTGOING`):**
    - Unir `asteriskcdrdb.cdr` con `call_center.agent` mediante `cdr.src = agent.number`.
    - Excluir registros cuya `uniqueid` ya exista en `call_center.calls` o `call_center.call_entry` para evitar duplicar llamadas de campaña.
    - Excluir llamadas de cola estándar (`cdr.dcontext != 'from-queue'`).
  - **Manuales Entrantes (`MANUAL_INCOMING`):**
    - Unir `asteriskcdrdb.cdr` con `call_center.agent` mediante `cdr.dst = agent.number`.
    - Aplicar las mismas exclusiones de duplicados y contexto de colas.
- Integrar ambas subconsultas con `UNION ALL` en la consulta principal y ajustar el bucle de preparación de parámetros (`$params`) para 7 subconsultas en total.

### 2. Modificación del Controlador PHP
- Editar `modules/agent_journey/index.php` -> `listadoAgentJourney()`.
- Añadir las claves de traducción `'MANUAL_INCOMING'` y `'MANUAL_OUTGOING'` al mapeo de tipos de eventos `$eventTypes`.

### 3. Modificación de Archivos de Lenguaje
- Editar `modules/agent_journey/lang/es.lang` para añadir:
  - `"Manual Incoming" => "Llamada Entrante Manual",`
  - `"Manual Outgoing" => "Llamada Saliente Manual",`
- Editar `modules/agent_journey/lang/en.lang` para añadir:
  - `"Manual Incoming" => "Manual Incoming Call",`
  - `"Manual Outgoing" => "Manual Outgoing Call",`

## Restricciones y Trampas Conocidas
- **Permisos de Base de Datos:** La consulta requiere acceder a la base de datos `asteriskcdrdb` desde la conexión abierta de `call_center`. El usuario MySQL de la conexión del PBX (`asterisk`) tiene privilegios globales en `localhost` que permiten cruzar ambas bases de datos sin problemas.
- **Duplicados:** Es crucial excluir por `uniqueid` las llamadas de la campaña predictiva o entrante del call center, ya que de lo contrario saldrían duplicadas como llamadas de campaña y llamadas manuales.
