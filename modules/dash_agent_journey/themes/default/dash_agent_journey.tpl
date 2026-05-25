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
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    text-align: center;
    border-top: 4px solid #007bff;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.06);
}

.card h3 {
    margin: 0 0 12px 0;
    font-size: 13px;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}

.card .value {
    font-size: 28px;
    font-weight: 700;
    color: #212529;
}

.card.cyan { border-top-color: #17a2b8; }
.card.green { border-top-color: #28a745; }
.card.orange { border-top-color: #fd7e14; }
.card.purple { border-top-color: #6f42c1; }

/* Main Content Area */
.dash-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}

.chart-container, .agent-stats, .event-log-container {
    background: #ffffff;
    padding: 24px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    margin-bottom: 20px;
}

.chart-container h3, .agent-stats h3, .event-log-container h3 {
    margin-top: 0;
    color: #1a202c;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 12px;
    font-size: 16px;
    font-weight: 600;
}

.agent-card {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid #adb5bd;
}

.agent-card.best { border-left-color: #28a745; }
.agent-card.worst { border-left-color: #dc3545; }

.agent-card h4 {
    margin: 0 0 6px 0;
    font-size: 14px;
    color: #495057;
}

.agent-card p {
    margin: 0;
    font-size: 13px;
    color: #6c757d;
}

/* Table styling for event log */
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
    color: #212529;
}

.event-table tr:hover {
    background-color: #f1f3f5;
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
{/literal}
</style>

<div class="dash-wrapper" style="position: relative;">
    <div class="loading-overlay" id="dash-loading">Cargando Métricas...</div>

    <div class="dash-header">
        <h2>Dashboard de Journey</h2>
        <button class="reload-btn" onclick="fetchMetrics()">Actualizar</button>
    </div>

    <div class="summary-cards">
        <div class="card cyan">
            <h3>Salientes por Campaña</h3>
            <div class="value" id="val-outbound-campaign">0</div>
        </div>
        <div class="card purple">
            <h3>Salientes Manuales</h3>
            <div class="value" id="val-outbound-manual">0</div>
        </div>
        <div class="card green">
            <h3>Total de Llamadas</h3>
            <div class="value" id="val-total-calls">0</div>
        </div>
        <div class="card orange">
            <h3>Total Pausas (Min)</h3>
            <div class="value" id="val-break-time">0</div>
        </div>
    </div>

    <div class="dash-main">
        <div class="chart-container">
            <h3>Distribución de Actividad</h3>
            <canvas id="activityChart"></canvas>
        </div>

        <div class="agent-stats">
            <h3>Rendimiento (Llamadas)</h3>
            <div class="agent-card best">
                <h4>Mayor Tiempo Hablado</h4>
                <p id="best-agent-name">N/A</p>
                <p><strong id="best-agent-time">0 min</strong></p>
            </div>
            
            <div class="agent-card worst">
                <h4>Menor Tiempo Hablado</h4>
                <p id="worst-agent-name">N/A</p>
                <p><strong id="worst-agent-time">0 min</strong></p>
            </div>
        </div>
    </div>
    
    <div class="chart-container">
        <h3>Comparación de Agentes (Minutos)</h3>
        <canvas id="agentCompareChart" height="100"></canvas>
    </div>

    <div class="event-log-container">
        <h3>Bitácora General de Eventos Recientes</h3>
        <div style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
            <table class="event-table" id="eventLogTable">
                <thead>
                    <tr>
                        <th>Agente</th>
                        <th>Fecha/Hora</th>
                        <th>Evento</th>
                        <th>Detalle</th>
                        <th>Duración</th>
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
var activityChartInstance = null;
var agentCompareChartInstance = null;

function formatMinutes(seconds) {
    if (!seconds || seconds <= 0) return '0.0';
    return (seconds / 60).toFixed(1);
}

function formatTimeHHMMSS(seconds) {
    if (!seconds || seconds <= 0) return '00:00:00';
    var h = Math.floor(seconds / 3600);
    var m = Math.floor((seconds % 3600) / 60);
    var s = Math.floor(seconds % 60);
    return (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
}

function fetchMetrics() {
    var loading = document.getElementById('dash-loading');
    loading.style.display = 'flex';

    // Get filter values
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
            renderDashboard(data);
        })
        .catch(err => {
            loading.style.display = 'none';
            console.error(err);
            alert("Error fetching metrics.");
        });
}

function translateEventType(type) {
    const map = {
        'LOGIN': 'Inicio de Sesión',
        'LOGOUT': 'Cierre de Sesión',
        'BREAK': 'Pausa',
        'INCOMING_CALL': 'Llamada Entrante',
        'OUTGOING_CALL': 'Llamada Saliente',
        'MANUAL_INCOMING': 'Llamada Entrante Manual',
        'MANUAL_OUTGOING': 'Llamada Saliente Manual',
        'HOLD': 'Hold'
    };
    return map[type] || type;
}

function renderDashboard(data) {
    var totals = data.totals || {};
    var counts = data.counts || {};
    
    // Calculate calls
    var outboundCampaign = counts['OUTGOING_CALL'] || 0;
    var outboundManual = counts['MANUAL_OUTGOING'] || 0;
    var totalCalls = (counts['INCOMING_CALL'] || 0) + (counts['OUTGOING_CALL'] || 0) + 
                     (counts['MANUAL_INCOMING'] || 0) + (counts['MANUAL_OUTGOING'] || 0);
    
    var breakTime = totals['BREAK'] || 0;
    
    // Update summary cards
    document.getElementById('val-outbound-campaign').innerText = outboundCampaign;
    document.getElementById('val-outbound-manual').innerText = outboundManual;
    document.getElementById('val-total-calls').innerText = totalCalls;
    document.getElementById('val-break-time').innerText = formatMinutes(breakTime);
    
    // Best / Worst Agents
    if (data.bestAgent) {
        document.getElementById('best-agent-name').innerText = data.bestAgent.name + ' (' + data.bestAgent.number + ')';
        document.getElementById('best-agent-time').innerText = formatMinutes(data.bestAgent.talk_time) + ' min';
    } else {
        document.getElementById('best-agent-name').innerText = 'N/A';
        document.getElementById('best-agent-time').innerText = '0 min';
    }

    if (data.worstAgent) {
        document.getElementById('worst-agent-name').innerText = data.worstAgent.name + ' (' + data.worstAgent.number + ')';
        document.getElementById('worst-agent-time').innerText = formatMinutes(data.worstAgent.talk_time) + ' min';
    } else {
        document.getElementById('worst-agent-name').innerText = 'N/A';
        document.getElementById('worst-agent-time').innerText = '0 min';
    }

    // Render Activity Chart (Pie)
    var ctxAct = document.getElementById('activityChart').getContext('2d');
    if (activityChartInstance) activityChartInstance.destroy();
    activityChartInstance = new Chart(ctxAct, {
        type: 'doughnut',
        data: {
            labels: ['Entrantes', 'Salientes Campaña', 'Salientes Manual', 'Pausas/Otros'],
            datasets: [{
                data: [
                    (totals['INCOMING_CALL'] || 0) + (totals['MANUAL_INCOMING'] || 0),
                    totals['OUTGOING_CALL'] || 0,
                    totals['MANUAL_OUTGOING'] || 0,
                    (totals['BREAK'] || 0) + (totals['HOLD'] || 0)
                ],
                backgroundColor: ['#28a745', '#17a2b8', '#6f42c1', '#fd7e14']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Render Agent Compare Chart (Bar) - Converted to Minutes
    var ctxComp = document.getElementById('agentCompareChart').getContext('2d');
    if (agentCompareChartInstance) agentCompareChartInstance.destroy();
    
    var topAgents = data.agentStats ? data.agentStats.slice(0, 15) : [];
    
    agentCompareChartInstance = new Chart(ctxComp, {
        type: 'bar',
        data: {
            labels: topAgents.map(a => a.name),
            datasets: [
                {
                    label: 'Tiempo Hablado (Min)',
                    data: topAgents.map(a => parseFloat(formatMinutes(a.talk_time))),
                    backgroundColor: '#007bff'
                },
                {
                    label: 'Tiempo Pausa (Min)',
                    data: topAgents.map(a => parseFloat(formatMinutes(a.break_time))),
                    backgroundColor: '#fd7e14'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: false },
                y: { 
                    stacked: false, 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Minutos'
                    }
                }
            }
        }
    });

    // Render Event Log Table
    var tbody = document.querySelector('#eventLogTable tbody');
    tbody.innerHTML = ''; // clear existing
    if (data.recent_events && data.recent_events.length > 0) {
        // Reverse array to show newest first, assuming recordset comes in chronological order
        var events = data.recent_events.slice().reverse();
        events.forEach(function(ev) {
            var tr = document.createElement('tr');
            
            var tdAgent = document.createElement('td');
            tdAgent.innerText = ev.name + " (" + ev.number + ")";
            
            var tdTime = document.createElement('td');
            tdTime.innerText = ev.event_time;
            
            var tdEvent = document.createElement('td');
            tdEvent.innerText = translateEventType(ev.event_type);
            
            var tdDetail = document.createElement('td');
            tdDetail.innerText = ev.event_detail || '';
            
            var tdDur = document.createElement('td');
            tdDur.innerText = formatTimeHHMMSS(ev.duration);
            
            tr.appendChild(tdAgent);
            tr.appendChild(tdTime);
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
        td.innerText = 'No hay eventos recientes en este filtro.';
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

// Initial fetch
document.addEventListener("DOMContentLoaded", function() {
    fetchMetrics();
});
{/literal}
</script>
