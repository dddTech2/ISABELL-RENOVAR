# SOP — Coordinator Dashboard (Módulo: coordinator_dashboard)

## Objetivo
Crear un módulo nuevo en Issabel llamado `coordinator_dashboard` que ofrezca a los coordinadores de call center una vista premium en tiempo real de todas las extensiones activas, sus estados, llamadas en curso, campañas asociadas, y métricas del turno.

## Entradas / Fuentes de Datos
- **PaloSantoConsola::listarEstadoMonitoreoAgentes()**: Estado en tiempo real de todos los agentes (online/oncall/paused/offline/ringing), número de teléfono en llamada (`linkstart`, `callnumber`), nombre del agente (`agentname`), cola, hold, etc. Viene del ECCP via AMI.
- **PaloSantoConsola::listarAgentes()**: Mapa `canal => "TIPO/NUM - Nombre del Agente"` desde DB `call_center.agent`. Fuente del nombre real del agente.
- **Nombre del usuario de extensión (FreePBX asterisk DB)**: Tabla `users` en la base de datos `asterisk`, campo `name` relacionado con `extension`. Query: `SELECT name FROM users WHERE extension = ?`. Esto da el nombre asignado a la extensión en FreePBX.
- **consultarLlamadasAgentes()**: Llamadas completadas del turno por agente (`num_calls`, `sec_calls`) desde `call_entry` y `calls`.
- **consultarTiempoBreakAgentes()**: Tiempo total de breaks del turno.
- **consultarTiempoHoldAgentes()**: Tiempo total de hold del turno.
- **consultarTiempoLoginAgentes()**: Tiempo total de login del turno.
- **PaloSantoConsola::leerListaCampanias()**: Lista de campañas activas/inactivas con tipo (incoming/outgoing) e ID.
- **Campaña activa del agente**: Disponible en `callinfo.calltype` + `callinfo.campaign_id` cuando el agente está oncall.

## Salidas
- Página web de módulo Issabel con diseño dark premium
- JSON endpoint `/index.php?menu=coordinator_dashboard&action=getAgentStatus` que devuelve estado completo de todos los agentes
- JSON endpoint `/index.php?menu=coordinator_dashboard&action=getCampaignList` que devuelve lista de campañas

## Arquitectura del Módulo

### Estructura de Archivos
```
modules/coordinator_dashboard/
├── index.php                          # Controlador principal PHP
├── configs/
│   └── default.conf.php               # DSN de call_center
├── lang/
│   └── es.lang                        # Traducciones ES
│   └── en.lang                        # Traducciones EN
├── images/                            # Iconos del módulo
└── themes/
    └── default/
        ├── coordinator_dashboard.tpl  # Plantilla Smarty principal
        └── js/
            └── dashboard.js           # Lógica polling y renderizado
```

### Componentes Visuales (Frontend)

#### 1. Header Bar
- Reloj en vivo (JavaScript `setInterval`)
- KPI chips: Agentes Online | En Llamada | En Pausa | Desconectados
- Botón "Wall Board" (activa fullscreen vía Fullscreen API)

#### 2. Filtros
- Dropdown: Filtrar por Cola (`queue`)
- Pills de Estado: Todos | Online | En Llamada | En Pausa | Desconectados
- Input de búsqueda de extensión (filtra en tiempo real con `startsWith` sobre el número, ej: escribir "4" muestra 4000, 4001, 4002)
- Selector de turno (hora inicio / hora fin)

#### 3. Grid de Tarjetas de Agentes
Cada tarjeta muestra:
- **Nombre del agente** (de `listarAgentes()` — campo `name` de DB `agent`) en grande
- **Extensión** (ej: `SIP/1001` o `PJSIP/4000`) en monospace
- **Badge de estado** con color/icono animado:
  - 🟢 `LISTO` (online) — verde
  - 🟡 `EN PAUSA: [nombre pausa]` — amarillo
  - 🔴 `EN LLAMADA` — rojo pulsante
  - ⚫ `DESCONECTADO` — gris
  - 🔵 `TIMBRANDO` — azul animado
  - 🟠 `EN HOLD` — naranja
- **Número en llamada** (de `callinfo.callnumber`) — visible solo si `oncall`
- **Campaña** (badge púrpura) — visible si `callinfo.campaign_id != null`
- **Timer de llamada** (cuenta segundos desde `callinfo.linkstart`) — animado en verde
- **Métricas del turno**: Llamadas realizadas | Contestadas | Talk time

#### 4. Panel Lateral de Campañas
- Lista desplegable de campañas activas
- Barra de progreso: conectadas / total

#### 5. Gráfica de Volumen por Hora
- Simple `<canvas>` con sparkline de llamadas por hora (query a DB `call_entry`)

### Acciones del Coordinador (Botones en tarjeta)

#### A. Escuchar la llamada (Spy)
- Botón 👂 en tarjeta cuando agente está `oncall`
- Reutilizar endpoint existente `spyAgent` de `campaign_monitoring/index.php`
- Este hace un `AMI Originate` al canal del coordinador con `ChanSpy`
- **Requiere**: extensión del coordinador (pedir al cargar el módulo o leer de sesión)

#### B. Forzar despausa (Unbreak)
- Botón ✋ visible cuando agente está `paused`
- Reutilizar endpoint `forceUnbreakAgent` de `campaign_monitoring/index.php`

#### C. Forzar login (Force Login)
- Botón 🔓 cuando agente está `offline`
- Reutilizar endpoint `forceLoginAgent` de `campaign_monitoring/index.php`

### Lógica de Nombres de Agente

Hay dos fuentes de nombres, en orden de prioridad:
1. **Base de datos `call_center.agent`**: `SELECT name FROM agent WHERE CONCAT(type,'/',number) = ?` — este es el nombre configurado en el módulo de Call Center agents
2. **Base de datos `asterisk.users`**: `SELECT name FROM users WHERE extension = ?` — nombre del usuario FreePBX vinculado a la extensión

En la implementación PHP:
1. Llamar `listarAgentes()` → obtener mapa `[canal] => nombre`
2. Si el agente no está en ese mapa (raro), consultar `asterisk.users` con el número de extensión extraído del canal
3. Fallback: mostrar el canal crudo

### Lógica de Polling (Frontend)
- Usar `setInterval` cada **4000ms** (4 segundos)
- Llamar `action=getAgentStatus` con parámetros de turno y filtro de cola
- Comparar estado anterior vs nuevo y animar solo las tarjetas que cambiaron
- Actualizar timers de llamada en cada tick aunque no haya cambio en el servidor

## Restricciones y Trampas Conocidas

> **NOTA POST-IMPLEMENTACIÓN:** La función `coordDash_resolveNameFromFreePBX()` en `index.php` usa credenciales hardcoded `asteriskuser / amp109` para conectar a la DB `asterisk`. Si el servidor usa una contraseña diferente para ese usuario, cambiar en el código. La contraseña real está en `/etc/freepbx.conf` como `$amp_conf['AMPDBPASS']`.



1. **Nombres con espacios en clases CSS**: El canal del agente (ej: `SIP/1001`) no puede usarse directamente como clase CSS porque contiene `/`. Usar `data-agent-channel` como atributo en la tarjeta y seleccionar con `querySelector('[data-agent-channel="SIP/1001"]')`.

2. **El campo `agentname` en `listarEstadoMonitoreoAgentes()`**: Este campo viene del ECCP XML y puede devolver el canal mismo en vez del nombre real. La fuente más confiable de nombres es la DB `call_center.agent.name`. Usar siempre `listarAgentes()` como fuente principal del nombre.

3. **FreePBX users vs Call Center agents**: Un agente en `call_center.agent` puede tener un número (ej: `1001`) diferente al usuario FreePBX. La relación es: `agent.number` == `users.extension`. Esto funciona para agentes SIP/PJSIP dinámicos. Para agentes tipo `Agent/9000` (estáticos), no hay un usuario FreePBX correspondiente.

4. **Spy requiere canal activo**: La acción de espiar solo es válida cuando el agente está `oncall`. Verificar el estado antes de enviar el request AMI.

5. **Wall Board y throttling del navegador**: En tabs de fondo, `setInterval` puede ser throttled a 1/min. Implementar el mismo truco de PiP o `noSleep` visto en el webphone si se activa el modo wall board.

6. **Filtro de extensión por prefijo**: El usuario escribirá "4" y quiere ver "4000", "4001", "4002". Implementar con `agentchannel.split('/')[1].startsWith(filterText)` en JavaScript.

7. **Gráfica por hora**: Query simple a `call_entry` y `calls` agrupando por `HOUR(datetime_init)`. Limitar a las últimas 12 horas.

## Plan de Ejecución

### Fase 1: Backend PHP
1. Crear `modules/coordinator_dashboard/index.php` con:
   - Acción por defecto: renderizar HTML via Smarty
   - `action=getAgentStatus`: devuelve JSON con estado completo de agentes + nombres
   - `action=getCampaignList`: devuelve JSON con lista de campañas activas
   - `action=getHourlyStats`: devuelve JSON con llamadas por hora
   - `action=spyAgent`: delega a lógica spy AMI
   - `action=forceUnbreakAgent`: delega a ECCP unbreak
   - `action=forceLoginAgent`: delega a ECCP force login

2. Crear `configs/default.conf.php` con DSN de `call_center`

3. Crear archivos de idioma

### Fase 2: Frontend
1. Crear `coordinator_dashboard.tpl` con estructura HTML dark premium
2. Crear `dashboard.js` con:
   - Polling loop `setInterval` cada 4s
   - Renderer de tarjetas de agentes
   - Lógica de filtros (cola, estado, extensión)
   - Timers de llamada animados
   - Sparkline de llamadas por hora (canvas)

### Fase 3: Integración
1. Registrar el módulo en el menú de Issabel
2. Verificar permisos (solo coordinadores/admins)
