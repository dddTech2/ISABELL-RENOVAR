/* Dashboard JS -- Coordinator Dashboard
 * Polling every 4s, renders agent cards with live call timers.
 * Uses Chart.js for hourly sparkline.
 */

var CoordDash = (function($) {
    'use strict';

    /* ---- Configuration ---- */
    var POLL_INTERVAL    = 4000;
    var CHART_INTERVAL   = 60000;
    var MODULE_NAME      = window.COORD_MODULE_NAME || 'coordinator_dashboard';

    /* ---- State ---- */
    var state = {
        agents:      [],
        filters:     { status: 'all', queue: 'all', extension: '' },
        shift:       { from: 0, to: 23 },
        pollTimer:   null,
        chartTimer:  null,
        hourlyChart: null,
        callTimers:  {}
    };

    /* ---- Helpers ---- */
    function fmtSeconds(sec) {
        sec = Math.max(0, Math.floor(sec));
        var h = Math.floor(sec / 3600);
        var m = Math.floor((sec % 3600) / 60);
        var s = sec % 60;
        return (h > 0 ? pad(h) + ':' : '') + pad(m) + ':' + pad(s);
    }
    function pad(n) { return n < 10 ? '0' + n : '' + n; }

    function baseUrl(action) {
        return 'index.php?menu=' + encodeURIComponent(MODULE_NAME) + '&action=' + action + '&rawmode=yes';
    }

    function escHtml(s) {
        if (!s) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
    function escAttr(s) { return escHtml(s); }

    /* ---- Error banner ---- */
    function showErrorBanner(title, detail) {
        var $b = $('#coord-error-banner');
        $b.find('strong').text(title);
        $b.find('pre').text(detail ? String(detail).substring(0, 1200) : '');
        $b.show();
    }
    function hideErrorBanner() { $('#coord-error-banner').hide(); }

    /* ---- Toast ---- */
    function showToast(msg, type) {
        var icon = type === 'success' ? '[OK]' : '[!]';
        var $t = $('<div class="coord-toast ' + type + '"><span class="toast-icon">' + icon + '</span><span>' + escHtml(msg) + '</span></div>');
        $('#coord-toast-container').append($t);
        setTimeout(function() { $t.fadeOut(400, function() { $t.remove(); }); }, 3500);
    }

    /* ---- Badge info by status ---- */
    function badgeInfo(agent) {
        var st = agent.status;
        if (agent.on_hold) return { cls: 'badge-hold',    text: 'EN ESPERA' };
        switch (st) {
            case 'online':  return { cls: 'badge-online',  text: 'LISTO' };
            case 'oncall':  return { cls: 'badge-oncall',  text: 'EN LLAMADA' };
            case 'paused':  return { cls: 'badge-paused',  text: 'EN PAUSA' };
            case 'ringing': return { cls: 'badge-ringing', text: 'TIMBRANDO' };
            case 'offline': return { cls: 'badge-offline', text: 'DESCONECTADO' };
            default:        return { cls: 'badge-offline', text: st.toUpperCase() };
        }
    }

    /* ---- Build agent card HTML ---- */
    function buildCard(agent) {
        var ch      = agent.channel;
        var extNum  = ch.replace(/^[^/]+\//, '');
        var badge   = badgeInfo(agent);
        var cardCls = 'agent-card status-' + agent.status;

        // Call info
        var callInfoHtml = '';
        if (agent.status === 'oncall' && agent.call_number) {
            callInfoHtml += '<div class="call-number">Tel: ' + escHtml(agent.call_number) + '</div>';
        }
        if (agent.status === 'oncall' && agent.link_start) {
            var elapsed = Math.floor(Date.now() / 1000) - agent.link_start;
            callInfoHtml += '<div class="call-timer" data-start="' + agent.link_start + '">' + fmtSeconds(elapsed) + '</div>';
        }
        if (agent.status === 'paused' && agent.pause_name) {
            callInfoHtml += '<div class="pause-name">Pausa: ' + escHtml(agent.pause_name) + '</div>';
        }

        // Campaign badge
        var campaignHtml = '';
        if (agent.campaign_name) {
            var typeLabel = agent.call_type === 'outgoing' ? '[Out]' : '[In]';
            campaignHtml = '<span class="campaign-badge">' + typeLabel + ' ' + escHtml(agent.campaign_name) + '</span>';
        }

        // Queue badge
        var queueHtml = '<span class="queue-badge">Cola: ' + escHtml(agent.queue) + '</span>';

        // Metrics
        var metricsHtml =
            '<div class="card-metrics">' +
            '<div class="metric-item"><div class="metric-val">' + agent.num_calls + '</div><div class="metric-lbl">Llamadas</div></div>' +
            '<div class="metric-item"><div class="metric-val">' + fmtSeconds(agent.sec_calls) + '</div><div class="metric-lbl">Habla</div></div>' +
            '<div class="metric-item"><div class="metric-val">' + fmtSeconds(agent.login_time) + '</div><div class="metric-lbl">Login</div></div>' +
            '</div>';

        // Actions
        var canSpy     = (agent.status === 'oncall');
        var canUnbreak = (agent.status === 'paused');
        var canLogin   = (agent.status === 'offline');
        var chAttr     = 'data-channel="' + escAttr(ch) + '"';
        var actionsHtml =
            '<div class="card-actions">' +
            '<button class="action-btn btn-spy" ' + chAttr + (canSpy ? '' : ' disabled') + '>Escuchar</button>' +
            '<button class="action-btn btn-unbreak" ' + chAttr + (canUnbreak ? '' : ' disabled') + '>Despausa</button>' +
            '<button class="action-btn btn-login" ' + chAttr + (canLogin ? '' : ' disabled') + '>Login</button>' +
            '</div>';

        return '<div class="' + cardCls + '" data-channel="' + escAttr(ch) + '" data-status="' + escAttr(agent.status) + '" data-queue="' + escAttr(agent.queue) + '" data-ext="' + escAttr(extNum) + '">' +
            '<div class="card-header"><div><div class="agent-name" title="' + escAttr(agent.name) + '">' + escHtml(agent.name) + '</div></div>' +
            '<div class="agent-ext">' + escHtml(extNum) + '</div></div>' +
            '<div class="status-badge ' + badge.cls + '"><span class="status-dot"></span>' + badge.text + '</div>' +
            '<div class="card-call-info">' + callInfoHtml + '</div>' +
            queueHtml + campaignHtml + metricsHtml + actionsHtml +
            '</div>';
    }

    /* ---- Apply filters ---- */
    function applyFilters() {
        var fStatus = state.filters.status;
        var fQueue  = state.filters.queue;
        var fExt    = state.filters.extension.toLowerCase().trim();

        $('#coord-grid .agent-card').each(function() {
            var $c     = $(this);
            var st     = $c.data('status');
            var q      = String($c.data('queue'));
            var extNum = String($c.data('ext'));

            var ok = (fStatus === 'all' || st === fStatus) &&
                     (fQueue  === 'all' || q  === fQueue)  &&
                     (fExt === '' || extNum.indexOf(fExt) === 0);

            $c.toggleClass('hidden', !ok);
        });

        var visible = $('#coord-grid .agent-card:not(.hidden)').length;
        $('#coord-no-agents').toggle(visible === 0);
    }

    /* ---- Update KPI chips ---- */
    function updateKPI(kpi) {
        $('#kpi-online').text(kpi.online  || 0);
        $('#kpi-oncall').text(kpi.oncall  || 0);
        $('#kpi-paused').text(kpi.paused  || 0);
        $('#kpi-offline').text(kpi.offline || 0);
    }

    /* ---- Render all agent cards ---- */
    function renderAgents(agents) {
        state.agents    = agents;
        state.callTimers = {};

        $.each(agents, function(i, a) {
            if (a.status === 'oncall' && a.link_start) {
                state.callTimers[a.channel] = a.link_start;
            }
        });

        var order = { oncall: 0, ringing: 1, online: 2, paused: 3, offline: 4 };
        agents.sort(function(a, b) {
            var oa = order[a.status] !== undefined ? order[a.status] : 5;
            var ob = order[b.status] !== undefined ? order[b.status] : 5;
            if (oa !== ob) return oa - ob;
            return a.name.localeCompare(b.name);
        });

        var html = '';
        $.each(agents, function(i, a) { html += buildCard(a); });

        if (html === '') {
            $('#coord-grid').html('<div id="coord-no-agents">No se encontraron agentes activos en el sistema.</div>');
        } else {
            $('#coord-grid').html(html + '<div id="coord-no-agents" style="display:none">Sin resultados para los filtros actuales.</div>');
        }
        applyFilters();
    }

    /* ---- Tick call timers ---- */
    function tickTimers() {
        var now = Math.floor(Date.now() / 1000);
        $('#coord-grid .call-timer[data-start]').each(function() {
            var start = parseInt($(this).data('start'), 10);
            $(this).text(fmtSeconds(now - start));
        });
    }

    /* ---- Poll agent status ---- */
    function poll() {
        $.ajax({
            url:     baseUrl('getAgentStatus'),
            type:    'GET',
            data:    { shift_from: state.shift.from, shift_to: state.shift.to },
            dataType: 'text',
            timeout: 8000,
            success: function(raw) {
                var resp;
                try { resp = JSON.parse(raw); }
                catch(e) {
                    showErrorBanner('Respuesta no-JSON del servidor (ver detalle):', raw);
                    return;
                }
                if (resp && resp.status === 'success') {
                    hideErrorBanner();
                    renderAgents(resp.agents || []);
                    updateKPI(resp.kpi || {});
                } else {
                    showErrorBanner('Error: ' + (resp ? resp.message : 'sin mensaje'), raw);
                }
            },
            error: function(xhr, status, err) {
                showErrorBanner('HTTP ' + xhr.status + ' ' + err, xhr.responseText || '(sin respuesta)');
            }
        });
    }

    /* ---- Hourly chart ---- */
    function loadHourlyChart() {
        $.ajax({
            url:     baseUrl('getHourlyStats'),
            type:    'GET',
            dataType: 'json',
            timeout: 6000,
            success: function(resp) {
                if (!resp || resp.status !== 'success') return;
                var data   = resp.data || [];
                var labels = $.map(data, function(d) { return d.label; });
                var values = $.map(data, function(d) { return d.value; });

                if (state.hourlyChart) {
                    state.hourlyChart.data.labels             = labels;
                    state.hourlyChart.data.datasets[0].data   = values;
                    state.hourlyChart.update();
                    return;
                }

                var ctx = document.getElementById('coord-hourly-chart');
                if (!ctx) return;

                state.hourlyChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels:   labels,
                        datasets: [{
                            label:           'Llamadas',
                            data:            values,
                            backgroundColor: 'rgba(124,58,237,0.25)',
                            borderColor:     'rgba(124,58,237,0.8)',
                            borderWidth:     1,
                            borderRadius:    3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#ffffff',
                                borderColor:     '#e2e6ea',
                                borderWidth:     1,
                                titleColor:      '#6b7280',
                                bodyColor:       '#1e2533',
                                callbacks: { label: function(c) { return ' ' + c.raw + ' llamadas'; } }
                            }
                        },
                        scales: {
                            x: { grid: { color: '#f3f4f6' }, ticks: { color: '#9ca3af', font: { size: 10 } } },
                            y: { grid: { color: '#f3f4f6' }, ticks: { color: '#9ca3af', font: { size: 10 }, precision: 0 }, beginAtZero: true }
                        }
                    }
                });
            }
        });
    }

    /* ---- Live clock ---- */
    function startClock() {
        function tick() {
            var d = new Date();
            $('#coord-clock').text(pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds()));
        }
        tick();
        setInterval(tick, 1000);
    }

    /* ---- Actions ---- */
    function spyAgent(channel) {
        $.ajax({
            url: baseUrl('spyAgent'), type: 'POST',
            data: { agentchannel: channel }, dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') showToast(r.message || 'Escucha iniciada', 'success');
                else showToast((r && r.message) || 'Error al escuchar', 'error');
            },
            error: function() { showToast('Error de conexion', 'error'); }
        });
    }
    function unbreakAgent(channel) {
        $.ajax({
            url: baseUrl('forceUnbreakAgent'), type: 'POST',
            data: { agentchannel: channel }, dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') { showToast('Despausa aplicada', 'success'); poll(); }
                else showToast((r && r.message) || 'Error al despausar', 'error');
            },
            error: function() { showToast('Error de conexion', 'error'); }
        });
    }
    function forceLogin(channel) {
        $.ajax({
            url: baseUrl('forceLoginAgent'), type: 'POST',
            data: { agentchannel: channel }, dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') { showToast('Login enviado', 'success'); poll(); }
                else showToast((r && r.message) || 'Error al forzar login', 'error');
            },
            error: function() { showToast('Error de conexion', 'error'); }
        });
    }

    /* ---- Bind events ---- */
    function bindEvents() {
        $('#coord-filters').on('click', '.status-pill', function() {
            var st = $(this).data('status');
            state.filters.status = st;
            $('.status-pill').removeClass('active active-online active-oncall active-paused active-offline');
            $(this).addClass('active');
            if (st !== 'all') $(this).addClass('active-' + st);
            applyFilters();
        });

        $('#coord-queue-filter').on('change', function() {
            state.filters.queue = $(this).val();
            applyFilters();
        });

        $('#coord-ext-filter').on('input', function() {
            state.filters.extension = $(this).val();
            applyFilters();
        });

        $('#coord-shift-apply').on('click', function() {
            state.shift.from = parseInt($('#coord-shift-from').val(), 10);
            state.shift.to   = parseInt($('#coord-shift-to').val(),   10);
            poll();
        });

        $('#coord-grid').on('click', '.btn-spy',     function() { spyAgent($(this).data('channel')); });
        $('#coord-grid').on('click', '.btn-unbreak', function() { unbreakAgent($(this).data('channel')); });
        $('#coord-grid').on('click', '.btn-login',   function() { forceLogin($(this).data('channel')); });
    }

    /* ---- Init ---- */
    function init() {
        startClock();
        bindEvents();
        poll();
        loadHourlyChart();
        state.pollTimer  = setInterval(poll,            POLL_INTERVAL);
        state.chartTimer = setInterval(loadHourlyChart, CHART_INTERVAL);
        setInterval(tickTimers, 1000);
        $('#coord-shift-from').val(0);
        $('#coord-shift-to').val(23);
    }

    return { init: init };

})(jQuery);

$(function() { CoordDash.init(); });
