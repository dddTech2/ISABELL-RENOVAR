{$FILTER_HTML}
{$CHARTJS}

<style>
/* Modern Dashboard Styling */
.dash-wrapper {
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f7f6;
    padding: 20px;
    border-radius: 8px;
    color: #333;
}

.dash-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.dash-header h2 {
    margin: 0;
    color: #2c3e50;
    font-weight: 600;
}

.reload-btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

.reload-btn:hover {
    background-color: #2980b9;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    text-align: center;
    border-left: 5px solid #3498db;
    transition: transform 0.2s ease;
}

.card:hover {
    transform: translateY(-5px);
}

.card h3 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #7f8c8d;
    text-transform: uppercase;
}

.card .value {
    font-size: 24px;
    font-weight: 700;
    color: #2c3e50;
}

.card.green { border-left-color: #2ecc71; }
.card.red { border-left-color: #e74c3c; }
.card.yellow { border-left-color: #f1c40f; }

/* Main Content Area */
.dash-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}

.chart-container {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.chart-container h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
}

.agent-stats {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.agent-stats h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
}

.agent-card {
    background: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    border-left: 4px solid #ccc;
}

.agent-card.best {
    border-left-color: #2ecc71;
}

.agent-card.worst {
    border-left-color: #e74c3c;
}

.agent-card h4 {
    margin: 0 0 5px 0;
    font-size: 16px;
    color: #34495e;
}

.agent-card p {
    margin: 0;
    font-size: 14px;
    color: #7f8c8d;
}

.loading-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 20px;
    font-weight: bold;
    color: #3498db;
    z-index: 10;
    border-radius: 8px;
    display: none;
}
</style>

<div class="dash-wrapper" style="position: relative;">
    <div class="loading-overlay" id="dash-loading">Loading Metrics...</div>

    <div class="dash-header">
        <h2>Agent Journey Dashboard</h2>
        <button class="reload-btn" onclick="fetchMetrics()">Refresh Metrics</button>
    </div>

    <div class="summary-cards">
        <div class="card">
            <h3>Total Talk Time</h3>
            <div class="value" id="val-talk-time">00:00:00</div>
        </div>
        <div class="card yellow">
            <h3>Total Break Time</h3>
            <div class="value" id="val-break-time">00:00:00</div>
        </div>
        <div class="card green">
            <h3>Total Calls</h3>
            <div class="value" id="val-total-calls">0</div>
        </div>
        <div class="card red">
            <h3>Avg Talk Time / Call</h3>
            <div class="value" id="val-avg-talk">00:00:00</div>
        </div>
    </div>

    <div class="dash-main">
        <div class="chart-container">
            <h3>Activity Distribution</h3>
            <canvas id="activityChart"></canvas>
        </div>

        <div class="agent-stats">
            <h3>Agent Performance</h3>
            <div class="agent-card best">
                <h4>Top Performer (Talk Time)</h4>
                <p id="best-agent-name">N/A</p>
                <p><strong id="best-agent-time">00:00:00</strong></p>
            </div>
            
            <div class="agent-card worst">
                <h4>Lowest Performer (Talk Time)</h4>
                <p id="worst-agent-name">N/A</p>
                <p><strong id="worst-agent-time">00:00:00</strong></p>
            </div>
        </div>
    </div>
    
    <div class="chart-container" style="margin-top: 20px;">
        <h3>Agent Comparison (Talk vs Break)</h3>
        <canvas id="agentCompareChart" height="100"></canvas>
    </div>
</div>

<script>
var activityChartInstance = null;
var agentCompareChartInstance = null;

function formatTime(seconds) {
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
        menu: '{$MODULE_NAME}',
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

function renderDashboard(data) {
    // Totals
    var totals = data.totals;
    var talkTime = (totals['INCOMING_CALL'] || 0) + (totals['OUTGOING_CALL'] || 0) + 
                   (totals['MANUAL_INCOMING'] || 0) + (totals['MANUAL_OUTGOING'] || 0);
    var breakTime = totals['BREAK'] || 0;
    
    // Count calls from agents events to get total calls correctly
    var totalCalls = 0;
    data.agents.forEach(a => {
        // We'll approximate total calls from events duration, but we should actually count occurrences.
        // For now, let's just show events count as total calls or we might need backend change.
        // We will just use raw events count related to calls if we can.
    });
    
    document.getElementById('val-talk-time').innerText = formatTime(talkTime);
    document.getElementById('val-break-time').innerText = formatTime(breakTime);
    
    // Best / Worst Agents
    if (data.bestAgent) {
        document.getElementById('best-agent-name').innerText = data.bestAgent.name + ' (' + data.bestAgent.number + ')';
        document.getElementById('best-agent-time').innerText = formatTime(data.bestAgent.talk_time) + ' Talk Time';
    } else {
        document.getElementById('best-agent-name').innerText = 'N/A';
        document.getElementById('best-agent-time').innerText = '00:00:00';
    }

    if (data.worstAgent) {
        document.getElementById('worst-agent-name').innerText = data.worstAgent.name + ' (' + data.worstAgent.number + ')';
        document.getElementById('worst-agent-time').innerText = formatTime(data.worstAgent.talk_time) + ' Talk Time';
    } else {
        document.getElementById('worst-agent-name').innerText = 'N/A';
        document.getElementById('worst-agent-time').innerText = '00:00:00';
    }

    // Render Activity Chart (Pie)
    var ctxAct = document.getElementById('activityChart').getContext('2d');
    if (activityChartInstance) activityChartInstance.destroy();
    activityChartInstance = new Chart(ctxAct, {
        type: 'doughnut',
        data: {
            labels: ['Inbound Calls', 'Outbound Calls', 'Breaks', 'Hold/Other'],
            datasets: [{
                data: [
                    (totals['INCOMING_CALL'] || 0) + (totals['MANUAL_INCOMING'] || 0),
                    (totals['OUTGOING_CALL'] || 0) + (totals['MANUAL_OUTGOING'] || 0),
                    totals['BREAK'] || 0,
                    totals['HOLD'] || 0
                ],
                backgroundColor: ['#2ecc71', '#3498db', '#f1c40f', '#95a5a6']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Render Agent Compare Chart (Bar)
    var ctxComp = document.getElementById('agentCompareChart').getContext('2d');
    if (agentCompareChartInstance) agentCompareChartInstance.destroy();
    
    // Limit to top 10 agents for display
    var topAgents = data.agentStats.slice(0, 10);
    
    agentCompareChartInstance = new Chart(ctxComp, {
        type: 'bar',
        data: {
            labels: topAgents.map(a => a.name),
            datasets: [
                {
                    label: 'Talk Time (sec)',
                    data: topAgents.map(a => a.talk_time),
                    backgroundColor: '#3498db'
                },
                {
                    label: 'Break Time (sec)',
                    data: topAgents.map(a => a.break_time),
                    backgroundColor: '#f1c40f'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { stacked: false },
                y: { stacked: false, beginAtZero: true }
            }
        }
    });
}

// Initial fetch
document.addEventListener("DOMContentLoaded", function() {
    fetchMetrics();
});
</script>
