{* Coordinator Dashboard — Smarty Template
   Dark premium real-time view for call center coordinators *}

{* Load Inter font + Chart.js CDN *}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

{* Module CSS *}
<link rel="stylesheet" href="modules/{$MODULE_NAME}/themes/default/css/dashboard.css">

{* Pass module name and translations to JS *}
<script>
window.COORD_MODULE_NAME = {$MODULE_NAME|json_encode};
window.COORD_LANG        = {$LANG_JSON};
</script>

{* Toast container *}
<div id="coord-toast-container"></div>

{* ======================================================
   MAIN DASHBOARD WRAPPER
   ====================================================== *}
<div id="coord-dashboard">

    {* ---- HEADER BAR ---- *}
    <div id="coord-header">
        <div class="header-brand">⚡ Coordinador CC</div>
        <span id="coord-clock">00:00:00</span>

        <div class="kpi-chips">
            <div class="kpi-chip online">
                <span class="kpi-dot"></span>
                <span class="kpi-num" id="kpi-online">—</span>
                <span class="kpi-lbl">Online</span>
            </div>
            <div class="kpi-chip oncall">
                <span class="kpi-dot"></span>
                <span class="kpi-num" id="kpi-oncall">—</span>
                <span class="kpi-lbl">En Llamada</span>
            </div>
            <div class="kpi-chip paused">
                <span class="kpi-dot"></span>
                <span class="kpi-num" id="kpi-paused">—</span>
                <span class="kpi-lbl">En Pausa</span>
            </div>
            <div class="kpi-chip offline">
                <span class="kpi-dot"></span>
                <span class="kpi-num" id="kpi-offline">—</span>
                <span class="kpi-lbl">Desconect.</span>
            </div>
        </div>
    </div>

    {* ---- FILTER BAR ---- *}
    <div id="coord-filters">

        {* Queue filter *}
        <span class="filter-label">Cola:</span>
        <select id="coord-queue-filter">
            <option value="all">Todas las colas</option>
            {foreach from=$QUEUES item=q}
            <option value="{$q|escape}">{$q|escape}</option>
            {/foreach}
        </select>

        {* Status pills *}
        <div class="status-pills">
            <span class="status-pill active" data-status="all">Todos</span>
            <span class="status-pill" data-status="online">🟢 Online</span>
            <span class="status-pill" data-status="oncall">🔴 En llamada</span>
            <span class="status-pill" data-status="paused">🟡 Pausa</span>
            <span class="status-pill" data-status="offline">⚫ Desconect.</span>
        </div>

        {* Extension prefix search *}
        <span class="filter-label">Extensión:</span>
        <input type="text" id="coord-ext-filter" placeholder="Ej: 40 → 4001, 4002…" maxlength="6">

        {* Shift filter *}
        <div class="shift-group">
            <span class="filter-label">Turno:</span>
            <select id="coord-shift-from">
                {foreach from=$HOURS_OPTIONS item=h}
                <option value="{$h|intval}">{$h}:00</option>
                {/foreach}
            </select>
            <span class="filter-label">—</span>
            <select id="coord-shift-to">
                {foreach from=$HOURS_OPTIONS item=h}
                <option value="{$h|intval}" {if $h == '23'}selected{/if}>{$h}:00</option>
                {/foreach}
            </select>
            <button id="coord-shift-apply" type="button">Aplicar</button>
        </div>

    </div>

    {* ---- AGENT GRID ---- *}
    <div id="coord-grid">
        <div id="coord-no-agents">Cargando agentes…</div>
    </div>

    {* ---- HOURLY CHART ---- *}
    <div id="coord-chart-section">
        <h3>📊 Llamadas por hora (últimas 12h)</h3>
        <canvas id="coord-hourly-chart"></canvas>
    </div>

</div>{* end #coord-dashboard *}

{* Dashboard JS — loaded last to ensure jQuery is available *}
<script src="modules/{$MODULE_NAME}/themes/default/js/dashboard.js"></script>
