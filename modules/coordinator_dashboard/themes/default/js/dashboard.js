/* Dashboard JS — Coordinator Dashboard
 * Polling every 4s, renders agent cards with live call timers.
 * Uses Chart.js for hourly sparkline.
 */

var CoordDash = (function($) {
    'use strict';

    /* ---- Configuration ---- */
    var POLL_INTERVAL    = 4000;   // ms between polls
    var CHART_INTERVAL   = 60000;  // ms between chart refreshes
    var MODULE_NAME      = window.COORD_MODULE_NAME || 'coordinator_dashboard';
    var LANG             = window.COORD_LANG || {};

    /* ---- State ---- */
    var state = {
        agents:        [],         // last received agent array
        filters: {
            status:    'all',
            queue:     'all',
            extension: ''
        },
        shift: {
            from: 0,
            to:   23
        },
        pollTimer:     null,
        chartTimer:    null,
        hourlyChart:   null,
        callTimers:    {}          // channel -> linkStart unix timestamp (seconds)
    };

    /* ---- Helper: format seconds as HH:MM:SS ---- */
    function fmtSeconds(sec) {
        sec = Math.max(0, Math.floor(sec));
        var h = Math.floor(sec / 3600);
        var m = Math.floor((sec % 3600) / 60);
        var s = sec % 60;
        return (h > 0 ? pad(h) + ':' : '') + pad(m) + ':' + pad(s);
    }
    function pad(n) { return n < 10 ? '0' + n : '' + n; }

    /* ---- Helper: base URL for AJAX ---- */
    function baseUrl(action) {
        return 'index.php?menu=' + encodeURIComponent(MODULE_NAME) + '&action=' + action;
    }

    /* ---- Badge info by status ---- */
    function badgeInfo(agent) {
        var st = agent.status;
        var onHold = agent.on_hold;
        if (onHold && st === 'oncall')  return { cls: 'badge-hold',    icon: '⏸', text: 'EN ESPERA' };
        if (onHold && st === 'paused')  return { cls: 'badge-hold',    icon: '⏸', text: 'EN ESPERA' };
        switch (st) {
            case 'online':  return { cls: 'badge-online',  icon: '●', text: 'LISTO' };
            case 'oncall':  return { cls: 'badge-oncall',  icon: '●', text: 'EN LLAMADA' };
            case 'paused':  return { cls: 'badge-paused',  icon: '●', text: 'EN PAUSA' };
            case 'ringing': return { cls: 'badge-ringing', icon: '●', text: 'TIMBRANDO' };
            case 'offline': return { cls: 'badge-offline', icon: '○', text: 'DESCONECTADO' };
            default:        return { cls: 'badge-offline', icon: '○', text: st.toUpperCase() };
        }
    }

    /* ---- Build agent card HTML ---- */
    function buildCard(agent) {
        var ch       = agent.channel;
        var extNum   = ch.replace(/^[^/]+\//, ''); // "SIP/1001" -> "1001"
        var badge    = badgeInfo(agent);
        var cardCls  = 'agent-card status-' + agent.status;

        // Call info line
        var callInfoHtml = '';
        if (agent.status === 'oncall' && agent.call_number) {
            callInfoHtml += '<div class="call-number">📞 ' + escHtml(agent.call_number) + '</div>';
        }
        if (agent.status === 'oncall' && agent.link_start) {
            var elapsed = Math.floor(Date.now() / 1000) - agent.link_start;
            callInfoHtml += '<div class="call-timer" data-start="' + agent.link_start + '">' + fmtSeconds(elapsed) + '</div>';
        }
        if (agent.status === 'paused' && agent.pause_name) {
            callInfoHtml += '<div class="pause-name">☕ ' + escHtml(agent.pause_name) + '</div>';
        }

        // Campaign badge
        var campaignHtml = '';
        if (agent.campaign_name) {
            var typeIcon = agent.call_type === 'outgoing' ? '📤' : '📥';
            campaignHtml = '<span class="campaign-badge">' + typeIcon + ' ' + escHtml(agent.campaign_name) + '</span>';
        }

        // Queue badge
        var queueHtml = '<span class="queue-badge">Q: ' + escHtml(agent.queue) + '</span>';

        // Metrics
        var loginFmt = fmtSeconds(agent.login_time);
        var talkFmt  = fmtSeconds(agent.sec_calls);
        var metricsHtml =
            '<div class="card-metrics">' +
            '  <div class="metric-item"><div class="metric-val">' + agent.num_calls + '</div><div class="metric-lbl">Llamadas</div></div>' +
            '  <div class="metric-item"><div class="metric-val">' + talkFmt + '</div><div class="metric-lbl">Habla</div></div>' +
            '  <div class="metric-item"><div class="metric-val">' + loginFmt + '</div><div class="metric-lbl">Login</div></div>' +
            '</div>';

        // Action buttons
        var canSpy     = (agent.status === 'oncall');
        var canUnbreak = (agent.status === 'paused');
        var canLogin   = (agent.status === 'offline');
        var chAttr     = 'data-channel="' + escAttr(ch) + '"';
        var actionsHtml =
            '<div class="card-actions">' +
            '  <button class="action-btn btn-spy" ' + chAttr + ' ' + (!canSpy ? 'disabled' : '') + ' title="Escuchar llamada">👂 Escuchar</button>' +
            '  <button class="action-btn btn-unbreak" ' + chAttr + ' ' + (!canUnbreak ? 'disabled' : '') + ' title="Forzar despausa">✋ Despausa</button>' +
            '  <button class="action-btn btn-login" ' + chAttr + ' ' + (!canLogin ? 'disabled' : '') + ' title="Forzar login">🔓 Login</button>' +
            '</div>';

        return '<div class="' + cardCls + '" data-channel="' + escAttr(ch) + '" data-status="' + escAttr(agent.status) + '" data-queue="' + escAttr(agent.queue) + '" data-ext="' + escAttr(extNum) + '">' +
            '<div class="card-header">' +
            '  <div>' +
            '    <div class="agent-name" title="' + escAttr(agent.name) + '">' + escHtml(agent.name) + '</div>' +
            '  </div>' +
            '  <div class="agent-ext">' + escHtml(ch) + '</div>' +
            '</div>' +
            '<div class="status-badge ' + badge.cls + '"><span class="status-dot"></span>' + badge.text + '</div>' +
            '<div class="card-call-info">' + callInfoHtml + '</div>' +
            queueHtml +
            campaignHtml +
            metricsHtml +
            actionsHtml +
            '</div>';
    }

    /* ---- HTML escaping ---- */
    function escHtml(s) {
        if (!s) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
    function escAttr(s) { return escHtml(s); }

    /* ---- Apply filters: show/hide cards ---- */
    function applyFilters() {
        var fStatus = state.filters.status;
        var fQueue  = state.filters.queue;
        var fExt    = state.filters.extension.toLowerCase().trim();

        $('#coord-grid .agent-card').each(function() {
            var $card   = $(this);
            var st      = $card.data('status');
            var q       = String($card.data('queue'));
            var extNum  = String($card.data('ext'));

            var showStatus = (fStatus === 'all' || st === fStatus);
            var showQueue  = (fQueue  === 'all' || q === fQueue);
            var showExt    = (fExt === '' || extNum.indexOf(fExt) === 0);

            if (showStatus && showQueue && showExt) {
                $card.removeClass('hidden');
            } else {
                $card.addClass('hidden');
            }
        });

        // Show "no agents" if all hidden
        var visible = $('#coord-grid .agent-card:not(.hidden)').length;
        if (visible === 0) {
            $('#coord-no-agents').show();
        } else {
            $('#coord-no-agents').hide();
        }
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
        state.agents = agents;
        state.callTimers = {};

        // Collect link_start for active timers
        $.each(agents, function(i, a) {
            if (a.status === 'oncall' && a.link_start) {
                state.callTimers[a.channel] = a.link_start;
            }
        });

        // Sort: oncall first, then ringing, online, paused, offline
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
            $('#coord-grid').html('<div id="coord-no-agents">No se encontraron agentes activos.</div>');
        } else {
            $('#coord-grid').html(html + '<div id="coord-no-agents" style="display:none">Sin resultados para los filtros actuales.</div>');
        }

        applyFilters();
    }

    /* ---- Tick call timers every second ---- */
    function tickTimers() {
        var now = Math.floor(Date.now() / 1000);
        $('#coord-grid .call-timer[data-start]').each(function() {
            var start   = parseInt($(this).data('start'), 10);
            var elapsed = now - start;
            $(this).text(fmtSeconds(elapsed));
        });
    }

    /* ---- Poll agent status ---- */
    function poll() {
        $.ajax({
            url: baseUrl('getAgentStatus'),
            type: 'GET',
            data: {
                shift_from: state.shift.from,
                shift_to:   state.shift.to
            },
            dataType: 'json',
            timeout: 8000,
            success: function(resp) {
                if (resp && resp.status === 'success') {
                    renderAgents(resp.agents || []);
                    updateKPI(resp.kpi || {});
                }
            },
            error: function() {
                // Silent: keep showing last state
            }
        });
    }

    /* ---- Load and render hourly chart ---- */
    function loadHourlyChart() {
        $.ajax({
            url: baseUrl('getHourlyStats'),
            type: 'GET',
            dataType: 'json',
            timeout: 6000,
            success: function(resp) {
                if (!resp || resp.status !== 'success') return;
                var data   = resp.data || [];
                var labels = $.map(data, function(d) { return d.label; });
                var values = $.map(data, function(d) { return d.value; });

                if (state.hourlyChart) {
                    state.hourlyChart.data.labels = labels;
                    state.hourlyChart.data.datasets[0].data = values;
                    state.hourlyChart.update();
                    return;
                }

                var ctx = document.getElementById('coord-hourly-chart');
                if (!ctx) return;

                state.hourlyChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Llamadas',
                            data: values,
                            backgroundColor: 'rgba(129,140,248,0.4)',
                            borderColor: 'rgba(129,140,248,0.9)',
                            borderWidth: 1,
                            borderRadius: 3,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#21262d',
                                borderColor: '#30363d',
                                borderWidth: 1,
                                titleColor: '#8b949e',
                                bodyColor: '#e6edf3',
                                callbacks: {
                                    label: function(ctx) { return ' ' + ctx.raw + ' llamadas'; }
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: { color: '#21262d' },
                                ticks: { color: '#6e7681', font: { size: 10 } }
                            },
                            y: {
                                grid: { color: '#21262d' },
                                ticks: { color: '#6e7681', font: { size: 10 }, precision: 0 },
                                beginAtZero: true
                            }
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
            var s = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
            $('#coord-clock').text(s);
        }
        tick();
        setInterval(tick, 1000);
    }

    /* ---- Toast notification ---- */
    function showToast(msg, type) {
        var icon = type === 'success' ? '✅' : '❌';
        var $t = $('<div class="coord-toast ' + type + '"><span class="toast-icon">' + icon + '</span>' + escHtml(msg) + '</div>');
        $('#coord-toast-container').append($t);
        setTimeout(function() { $t.fadeOut(400, function() { $t.remove(); }); }, 3500);
    }

    /* ---- Action: spy ---- */
    function spyAgent(channel) {
        $.ajax({
            url: baseUrl('spyAgent'),
            type: 'POST',
            data: { agentchannel: channel },
            dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') showToast(r.message || 'Escucha iniciada', 'success');
                else showToast((r && r.message) || 'Error al iniciar escucha', 'error');
            },
            error: function() { showToast('Error de conexión', 'error'); }
        });
    }

    /* ---- Action: unbreak ---- */
    function unbreakAgent(channel) {
        $.ajax({
            url: baseUrl('forceUnbreakAgent'),
            type: 'POST',
            data: { agentchannel: channel },
            dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') { showToast('Despausa aplicada', 'success'); poll(); }
                else showToast((r && r.message) || 'Error al despausar', 'error');
            },
            error: function() { showToast('Error de conexión', 'error'); }
        });
    }

    /* ---- Action: force login ---- */
    function forceLogin(channel) {
        $.ajax({
            url: baseUrl('forceLoginAgent'),
            type: 'POST',
            data: { agentchannel: channel },
            dataType: 'json',
            success: function(r) {
                if (r && r.status === 'success') { showToast('Login enviado', 'success'); poll(); }
                else showToast((r && r.message) || 'Error al forzar login', 'error');
            },
            error: function() { showToast('Error de conexión', 'error'); }
        });
    }

    /* ---- Bind events ---- */
    function bindEvents() {
        // Status pills
        $('#coord-filters').on('click', '.status-pill', function() {
            var st = $(this).data('status');
            state.filters.status = st;

            // Clear active on all
            $('.status-pill').removeClass('active active-online active-oncall active-paused active-offline');
            $(this).addClass('active');
            if (st !== 'all') $(this).addClass('active-' + st);

            applyFilters();
        });

        // Queue filter
        $('#coord-queue-filter').on('change', function() {
            state.filters.queue = $(this).val();
            applyFilters();
        });

        // Extension text filter
        $('#coord-ext-filter').on('input', function() {
            state.filters.extension = $(this).val();
            applyFilters();
        });

        // Shift apply
        $('#coord-shift-apply').on('click', function() {
            state.shift.from = parseInt($('#coord-shift-from').val(), 10);
            state.shift.to   = parseInt($('#coord-shift-to').val(),   10);
            poll();
        });

        // Card action buttons (delegated)
        $('#coord-grid').on('click', '.btn-spy', function() {
            spyAgent($(this).data('channel'));
        });
        $('#coord-grid').on('click', '.btn-unbreak', function() {
            unbreakAgent($(this).data('channel'));
        });
        $('#coord-grid').on('click', '.btn-login', function() {
            forceLogin($(this).data('channel'));
        });
    }

    /* ---- Init ---- */
    function init() {
        startClock();
        bindEvents();

        // First poll immediately
        poll();
        loadHourlyChart();

        // Recurring polls
        state.pollTimer  = setInterval(poll,           POLL_INTERVAL);
        state.chartTimer = setInterval(loadHourlyChart, CHART_INTERVAL);

        // Call timer tick every second
        setInterval(tickTimers, 1000);

        // Initialize shift selectors to current hour
        var now = new Date();
        $('#coord-shift-from').val(0);
        $('#coord-shift-to').val(23);
    }

    return { init: init };

})(jQuery);

// Boot when DOM is ready
$(function() {
    CoordDash.init();
});
