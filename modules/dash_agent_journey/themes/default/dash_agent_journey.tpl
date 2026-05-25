{$FILTER_HTML}
{$CHARTJS}

<style>
{literal}
/* Modern Clean Light Theme Styling */
.dash-wrapper {
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f6f9;
    padding: 25px;
    border-radius: 12px;
    color: #333;
}

.dash-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.dash-header h2 {
    margin: 0;
    color: #1a202c;
    font-weight: 700;
    font-size: 24px;
}

.reload-btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
}

.reload-btn:hover {
    background-color: #0056b3;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    text-align: center;
    border-top: 4px solid #007bff;
}

.card h3 {
    margin: 0 0 10px 0;
    font-size: 13px;
    color: #6c757d;
    text-transform: uppercase;
    font-weight: 600;
}

.card .value {
    font-size: 24px;
    font-weight: 700;
    color: #212529;
}

.card .subtext {
    font-size: 12px;
    color: #adb5bd;
    margin-top: 5px;
}

.card.cyan { border-top-color: #17a2b8; }
.card.green { border-top-color: #28a745; }
.card.orange { border-top-color: #fd7e14; }
.card.purple { border-top-color: #6f42c1; }
.card.red { border-top-color: #dc3545; }

/* Main Content Area */
.dash-main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.chart-container {
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.chart-container h3 {
    margin-top: 0;
    color: #1a202c;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 12px;
    font-size: 16px;
    font-weight: 600;
}

/* Table styling */
.event-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 13px;
}

.event-table th {
    background-color: #f8f9fa;
    color: #495057;
    font-weight: 600;
    text-align: left;
    padding: 12px;
    border-bottom: 2px solid #dee2e6;
}

.event-table td {
    padding: 12px;
    border-bottom: 1px solid #e9ecef;
}

.loading-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.85);
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    color: #007bff;
    z-index: 10;
    border-radius: 12px;
    display: none;
}

/* View Toggles */
#view-coordinator, #view-agent {
    display: none;
}
{/literal}
</style>

<div class="dash-wrapper" style="position: relative;">
    <div class="loading-overlay" id="dash-loading">Cargando Métricas...</div>

    <div class="dash-header">
        <h2 id="dash-title">Dashboard Operativo</h2>
        <button class="reload-btn" onclick="fetchMetrics()">Actualizar Datos</button>
    </div>

    <!-- VISTA DEL COORDINADOR (GLOBAL) -->
    <div id="view-coordinator">
        <div class="summary-cards">
            <div class="card cyan">
                <h3>Salientes Campaña</h3>
                <div class="value" id="glb-camp-calls">0</div>
                <div class="subtext" id="glb-camp-sub">0% Efectividad</div>
            </div>
            <div class="card purple">
                <h3>Salientes Manual</h3>
                <div class="value" id="glb-man-calls">0</div>
                <div class="subtext" id="glb-man-sub">0% Efectividad</div>
            </div>
            <div class="card green">
                <h3>Contactabilidad Global</h3>
                <div class="value" id="glb-contactability">0%</div>
                <div class="subtext" id="glb-contact-sub">0 intentos totales</div>
            </div>
            <div class="card orange">
                <h3>TMO Promedio</h3>
                <div class="value" id="glb-tmo">0 min</div>
                <div class="subtext">Global Efectivo</div>
            </div>
        </div>

        <div class="dash-main">
            <div class="chart-container">
                <h3>Estados de Llamada (Combinadas)</h3>
                <div style="position: relative; height: 300px; width: 100%;">
                    <canvas id="callStatusChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>Distribución de Pausas</h3>
                <div style="position: relative; height: 300px; width: 100%;">
                    <canvas id="breakTypesChart"></canvas>
                </div>
            </div>
        </div>

        <div class="chart-container" style="margin-bottom: 20px;">
            <h3>Comparación TMO vs Contactabilidad por Agente</h3>
            <div style="position: relative; height: 350px; width: 100%;">
                <canvas id="agentCompareChart"></canvas>
            </div>
        </div>
    </div>

    <!-- VISTA DEL ASESOR (INDIVIDUAL) -->
    <div id="view-agent">
        <div class="summary-cards">
            <div class="card cyan">
                <h3>Asesor</h3>
                <div class="value" id="agt-name" style="font-size:20px;">Nombre</div>
                <div class="subtext" id="agt-ext">Ext: 000</div>
            </div>
            <div class="card green">
                <h3>Efectividad Individual</h3>
                <div class="value" id="agt-contactability">0%</div>
                <div class="subtext" id="agt-contact-sub">0 / 0</div>
            </div>
            <div class="card purple">
                <h3>Salientes (Campaña / Manual)</h3>
                <div class="value" id="agt-out-split" style="font-size:20px;">0 / 0</div>
                <div class="subtext" id="agt-out-sub">Totales Marcadas</div>
            </div>
            <div class="card orange">
                <h3>Desviación TMO</h3>
                <div class="value" id="agt-tmo">0 min</div>
                <div class="subtext" id="agt-tmo-sub">vs Campaña</div>
            </div>
        </div>
        
        <div class="dash-main">
            <div class="chart-container">
                <h3>Gestión del Tiempo (Asesor)</h3>
                <div style="position: relative; height: 300px; width: 100%;">
                    <canvas id="agtTimeChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>Resultados de Marcación (Combinados)</h3>
                <div style="position: relative; height: 300px; width: 100%;">
                    <canvas id="agtStatusChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- BITÁCORA (COMÚN) -->
    <div class="chart-container">
        <h3>Línea de Tiempo / Bitácora de Eventos</h3>
        <div style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
            <table class="event-table" id="eventLogTable">
                <thead>
                    <tr>
                        <th>Fecha/Hora</th>
                        <th>Agente</th>
                        <th>Evento</th>
                        <th>Detalle</th>
                        <th>Duración (min)</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Llenado dinámicamente -->
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
var moduleName = '{$MODULE_NAME}';
{literal}
var charts = {};

function destroyCharts() {
    for (let key in charts) {
        if (charts[key]) charts[key].destroy();
    }
}

function formatMinutes(seconds) {
    if (!seconds || seconds <= 0) return '0.0';
    return (seconds / 60).toFixed(1);
}

function fetchMetrics() {
    var loading = document.getElementById('dash-loading');
    loading.style.display = 'flex';

    var date_start = document.getElementsByName('date_start')[0]?.value || '';
    var date_end = document.getElementsByName('date_end')[0]?.value || '';
    var agent = document.getElementsByName('agent')[0]?.value || '';
    var holdincluded = document.getElementsByName('holdincluded')[0]?.value || '';

    var params = new URLSearchParams({
        menu: moduleName,
        rawmode: 'yes',
        action: 'get_metrics',
        date_start: date_start,
        date_end: date_end,
        agent: agent,
        holdincluded: holdincluded
    });

    fetch('index.php?' + params.toString())
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            if(data.error) {
                alert("Error fetching metrics: " + data.error);
                return;
            }
            renderDashboard(data, agent !== '');
        })
        .catch(err => {
            loading.style.display = 'none';
            console.error(err);
            alert("Error fetching metrics.");
        });
}

function translateEventType(type) {
    const map = {
        'LOGIN': 'Login', 'LOGOUT': 'Logout', 'BREAK': 'Pausa',
        'INCOMING_CALL': 'Entrante', 'OUTGOING_CALL': 'Saliente',
        'MANUAL_INCOMING': 'Entrante Manual', 'MANUAL_OUTGOING': 'Saliente Manual', 'HOLD': 'Hold'
    };
    return map[type] || type;
}

function renderDashboard(data, isAgentFiltered) {
    destroyCharts();
    
    // Si la DB reporta 1 agente (y se filtró), mostramos Nivel 2
    var isAgentView = isAgentFiltered && data.agentStats && data.agentStats.length === 1;
    
    document.getElementById('view-coordinator').style.display = isAgentView ? 'none' : 'block';
    document.getElementById('view-agent').style.display = isAgentView ? 'block' : 'none';
    document.getElementById('dash-title').innerText = isAgentView ? 'Dashboard del Asesor' : 'Dashboard General (Coordinación)';

    var c_st = data.campaign_statuses || {};
    var m_st = data.manual_statuses || {};
    
    var campAttempts = (c_st['Success']||0) + (c_st['ShortCall']||0) + (c_st['Busy']||0) + (c_st['Failed']||0) + (c_st['Congestion']||0);
    var campSuccess = (c_st['Success']||0) + (c_st['ShortCall']||0);
    var campEff = campAttempts > 0 ? ((campSuccess / campAttempts) * 100).toFixed(1) : 0;
    
    var manAttempts = (m_st['Success']||0) + (m_st['ShortCall']||0) + (m_st['Busy']||0) + (m_st['Failed']||0) + (m_st['Congestion']||0);
    var manSuccess = (m_st['Success']||0) + (m_st['ShortCall']||0);
    var manEff = manAttempts > 0 ? ((manSuccess / manAttempts) * 100).toFixed(1) : 0;
    
    var totalAttempts = campAttempts + manAttempts;
    var totalSuccesses = campSuccess + manSuccess;
    var totalTalkTime = data.totals['OUTGOING_CALL'] || 0; 
    
    var globalContactability = totalAttempts > 0 ? ((totalSuccesses / totalAttempts) * 100).toFixed(1) : 0;
    var globalTMO = totalSuccesses > 0 ? formatMinutes(totalTalkTime / totalSuccesses) : 0;

    if (isAgentView) {
        var a = data.agentStats[0];
        document.getElementById('agt-name').innerText = a.name;
        document.getElementById('agt-ext').innerText = 'Ext: ' + a.number;
        document.getElementById('agt-contactability').innerText = a.contactability + '%';
        
        var total_s = (a.campaign_statuses['Success']||0) + (a.manual_statuses['Success']||0);
        document.getElementById('agt-contact-sub').innerText = total_s + ' Éxitos / ' + a.outbound_attempts + ' Intentos';
        
        var a_camp = (a.campaign_statuses['Success']||0) + (a.campaign_statuses['ShortCall']||0) + (a.campaign_statuses['Busy']||0) + (a.campaign_statuses['Failed']||0) + (a.campaign_statuses['Congestion']||0);
        var a_man = (a.manual_statuses['Success']||0) + (a.manual_statuses['ShortCall']||0) + (a.manual_statuses['Busy']||0) + (a.manual_statuses['Failed']||0) + (a.manual_statuses['Congestion']||0);
        
        document.getElementById('agt-out-split').innerText = a_camp + ' / ' + a_man;
        
        document.getElementById('agt-tmo').innerText = a.tmo + ' min';
        
        var diff = a.tmo - parseFloat(globalTMO);
        document.getElementById('agt-tmo-sub').innerText = (diff > 0 ? '+'+diff.toFixed(1) : diff.toFixed(1)) + ' min vs Campaña';

        var ctxAgtTime = document.getElementById('agtTimeChart').getContext('2d');
        charts['agtTime'] = new Chart(ctxAgtTime, {
            type: 'pie',
            data: {
                labels: ['Tiempo Hablado', 'Tiempo en Pausa'],
                datasets: [{
                    data: [parseFloat(formatMinutes(a.talk_time)), parseFloat(formatMinutes(a.break_time))],
                    backgroundColor: ['#28a745', '#fd7e14']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        var ctxAgtSt = document.getElementById('agtStatusChart').getContext('2d');
        charts['agtStatus'] = new Chart(ctxAgtSt, {
            type: 'doughnut',
            data: {
                labels: ['Success', 'ShortCall', 'Busy', 'Failed', 'Congestion'],
                datasets: [{
                    data: [
                        (a.campaign_statuses['Success']||0) + (a.manual_statuses['Success']||0), 
                        (a.campaign_statuses['ShortCall']||0) + (a.manual_statuses['ShortCall']||0),
                        (a.campaign_statuses['Busy']||0) + (a.manual_statuses['Busy']||0), 
                        (a.campaign_statuses['Failed']||0) + (a.manual_statuses['Failed']||0),
                        (a.campaign_statuses['Congestion']||0) + (a.manual_statuses['Congestion']||0)
                    ],
                    backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6c757d']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

    } else {
        // Vista Global
        document.getElementById('glb-camp-calls').innerText = campAttempts;
        document.getElementById('glb-camp-sub').innerText = campEff + '% Efectividad';
        
        document.getElementById('glb-man-calls').innerText = manAttempts;
        document.getElementById('glb-man-sub').innerText = manEff + '% Efectividad';
        
        document.getElementById('glb-contactability').innerText = globalContactability + '%';
        document.getElementById('glb-contact-sub').innerText = totalAttempts + ' intentos totales';
        document.getElementById('glb-tmo').innerText = globalTMO + ' min';

        var ctxSt = document.getElementById('callStatusChart').getContext('2d');
        charts['status'] = new Chart(ctxSt, {
            type: 'doughnut',
            data: {
                labels: ['Success', 'ShortCall', 'Busy', 'Failed', 'Congestion'],
                datasets: [{
                    data: [
                        (c_st['Success']||0) + (m_st['Success']||0), 
                        (c_st['ShortCall']||0) + (m_st['ShortCall']||0), 
                        (c_st['Busy']||0) + (m_st['Busy']||0), 
                        (c_st['Failed']||0) + (m_st['Failed']||0), 
                        (c_st['Congestion']||0) + (m_st['Congestion']||0)
                    ],
                    backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6c757d']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });

        var bt = data.break_types || {};
        var bNames = Object.keys(bt);
        var bValues = bNames.map(k => parseFloat(formatMinutes(bt[k].duration)));
        
        var ctxBrk = document.getElementById('breakTypesChart').getContext('2d');
        charts['break'] = new Chart(ctxBrk, {
            type: 'bar',
            data: {
                labels: bNames.length ? bNames : ['Sin Datos'],
                datasets: [{
                    label: 'Tiempo (Min)',
                    data: bValues.length ? bValues : [0],
                    backgroundColor: '#6f42c1'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        var topAgents = data.agentStats ? data.agentStats.slice(0, 20) : [];
        var ctxComp = document.getElementById('agentCompareChart').getContext('2d');
        charts['comp'] = new Chart(ctxComp, {
            type: 'bar',
            data: {
                labels: topAgents.map(a => a.name),
                datasets: [
                    {
                        label: 'TMO (Min)',
                        data: topAgents.map(a => a.tmo),
                        backgroundColor: '#007bff'
                    },
                    {
                        label: 'Contactabilidad (%)',
                        type: 'line',
                        data: topAgents.map(a => a.contactability),
                        borderColor: '#28a745',
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    y: { title: { display: true, text: 'Minutos' } },
                    y1: { position: 'right', min: 0, max: 100, title: { display: true, text: 'Porcentaje' } }
                }
            }
        });
    }

    // Render Event Log Table
    var tbody = document.querySelector('#eventLogTable tbody');
    tbody.innerHTML = ''; 
    if (data.recent_events && data.recent_events.length > 0) {
        var events = data.recent_events.slice().reverse();
        events.forEach(function(ev) {
            var tr = document.createElement('tr');
            
            var tdTime = document.createElement('td');
            tdTime.innerText = ev.event_time;
            
            var tdAgent = document.createElement('td');
            tdAgent.innerText = ev.name + " (" + ev.number + ")";
            
            var tdEvent = document.createElement('td');
            tdEvent.innerText = translateEventType(ev.event_type);
            
            var tdDetail = document.createElement('td');
            tdDetail.innerText = ev.event_detail || '';
            
            var tdDur = document.createElement('td');
            tdDur.innerText = formatMinutes(ev.duration);
            
            tr.appendChild(tdTime);
            tr.appendChild(tdAgent);
            tr.appendChild(tdEvent);
            tr.appendChild(tdDetail);
            tr.appendChild(tdDur);
            
            tbody.appendChild(tr);
        });
    } else {
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        td.colSpan = 5;
        td.style.textAlign = 'center';
        td.innerText = 'No hay eventos en este filtro.';
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    fetchMetrics();
});
{/literal}
</script>
