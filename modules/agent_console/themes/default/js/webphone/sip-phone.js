/**
 * WebPhone Panel for Issabel Agent Console
 * Simplified SIP.js wrapper for basic call functionality
 * SECURITY: Stops on auth failure to prevent fail2ban blocks
 */

var WebPhone = (function() {
    function $(selector) {
        var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
        return window.jQuery(selector, context);
    }
    var userAgent = null;
    var registerer = null;
    var currentSession = null;
    var heldSession = null;
    var registerAttempts = 0;
    var maxRegisterAttempts = 1;
    var config = {
        extension: '',
        password: '',
        domain: '',
        wssServer: '',
        wssPort: '8089',
        wssPath: '/ws',
        autoAnswerDelay: 1000 // milliseconds before auto-answering
    };
    var audioElements = {
        remote: null,
        local: null
    };
    var earlyMediaReceived = false; // Track if provider sent early media (183)
    var state = {
        registered: false,
        callState: 'idle', // idle, calling, ringing, connected
        authFailed: false,
        autoAnswer: false,
        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)
        isVoicemail: false, // Track if call was answered by a voicemail system
        muted: false, // Track mute state
        activeNumber: '', // Active call number/identifier
        callStartTime: null
    };
    var callbacks = {
        onRegistered: null,
        onUnregistered: null,
        onCallStateChange: null,
        onError: null
    };
    
    // Audio context for ringtones
    var audioContext = null;
    var ringtoneOscillator = null;
    var ringtoneGain = null;
    var callTimerInterval = null;
    var ringtoneInterval = null;
    
    // Auto-answer timeout reference
    var autoAnswerTimeout = null;

    function log(msg) {
        console.log('[WebPhone] ' + msg);
    }

    // ============================================
    // AUTO-ANSWER
    // ============================================
    
    function setAutoAnswer(enabled) {
        state.autoAnswer = enabled;
        log('Auto-answer ' + (enabled ? 'ENABLED' : 'DISABLED'));
        
        // Update UI
        var $row = $('.webphone-autoanswer-row');
        if (enabled) {
            $row.addClass('active');
        } else {
            $row.removeClass('active');
        }
        
        // Save to localStorage for persistence
        try {
            localStorage.setItem('webphone_autoanswer', enabled ? '1' : '0');
        } catch (e) {}
    }
    
    function loadAutoAnswerPreference() {
        try {
            var saved = localStorage.getItem('webphone_autoanswer');
            if (saved === '1') {
                setAutoAnswer(true);
                $('#webphone-autoanswer').prop('checked', true);
            } else {
                setAutoAnswer(false);
                $('#webphone-autoanswer').prop('checked', false);
            }
        } catch (e) {
            setAutoAnswer(false);
            $('#webphone-autoanswer').prop('checked', false);
        }
    }
    
    function triggerAutoAnswer() {
        if (!state.autoAnswer || !currentSession) {
            return;
        }
        
        log('Auto-answer triggered, will answer in ' + config.autoAnswerDelay + 'ms');
        
        // Clear any existing timeout
        if (autoAnswerTimeout) {
            clearTimeout(autoAnswerTimeout);
        }
        
        // Auto-answer after delay (gives agent a moment to see the incoming call)
        autoAnswerTimeout = setTimeout(function() {
            if (state.callState === 'ringing' && currentSession) {
                log('Auto-answering call now');
                answer();
            }
        }, config.autoAnswerDelay);
    }

    // ============================================
    // AUDIO: Ringtone generation using Web Audio API
    // ============================================
    
    function initAudioContext() {
        if (!audioContext) {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                log('Web Audio API not supported: ' + e.message);
            }
        }
        return audioContext;
    }

    function playRingtoneSound(type) {
        stopRingtoneSound();
        
        var ctx = initAudioContext();
        if (!ctx) return;
        
        // Resume audio context if suspended (browser autoplay policy)
        if (ctx.state === 'suspended') {
            ctx.resume();
        }
        
        ringtoneGain = ctx.createGain();
        ringtoneGain.gain.value = 0.3;
        ringtoneGain.connect(ctx.destination);
        
        if (type === 'incoming') {
            // Incoming call ringtone: classic phone ring pattern
            var ringPattern = function() {
                if (!ringtoneGain) return;
                
                // Create oscillator for ring tone
                ringtoneOscillator = ctx.createOscillator();
                ringtoneOscillator.type = 'sine';
                ringtoneOscillator.frequency.value = 440; // A4 note
                ringtoneOscillator.connect(ringtoneGain);
                ringtoneOscillator.start();
                
                // Stop after 400ms, pause 200ms, repeat
                setTimeout(function() {
                    if (ringtoneOscillator) {
                        ringtoneOscillator.stop();
                        ringtoneOscillator.disconnect();
                        ringtoneOscillator = null;
                    }
                }, 400);
            };
            
            ringPattern();
            ringtoneInterval = setInterval(ringPattern, 600); // Ring every 600ms
            
        } else if (type === 'outgoing') {
            // Outgoing call ringback tone: standard ring pattern (1s on, 3s off)
            var beepPattern = function() {
                if (!ringtoneGain) return;
                
                ringtoneOscillator = ctx.createOscillator();
                ringtoneOscillator.type = 'sine';
                ringtoneOscillator.frequency.value = 440; // A4 note - standard ringback
                ringtoneOscillator.connect(ringtoneGain);
                ringtoneOscillator.start();
                
                setTimeout(function() {
                    if (ringtoneOscillator) {
                        ringtoneOscillator.stop();
                        ringtoneOscillator.disconnect();
                        ringtoneOscillator = null;
                    }
                }, 1000); // 1 second beep
            };
            
            beepPattern();
            ringtoneInterval = setInterval(beepPattern, 4000); // Repeat every 4 seconds (1s on + 3s off)
        }
        
        log('Playing ' + type + ' ringtone');
    }

    function stopRingtoneSound() {
        if (ringtoneInterval) {
            clearInterval(ringtoneInterval);
            ringtoneInterval = null;
        }
        if (ringtoneOscillator) {
            try {
                ringtoneOscillator.stop();
                ringtoneOscillator.disconnect();
            } catch (e) {}
            ringtoneOscillator = null;
        }
        if (ringtoneGain) {
            try {
                ringtoneGain.disconnect();
            } catch (e) {}
            ringtoneGain = null;
        }
        log('Ringtone stopped');
    }

    // ============================================

    function updateCallState(newState) {
        state.callState = newState;
        if (newState === 'connected') {
            state.callStartTime = new Date().getTime();
        }
        if (callbacks.onCallStateChange) {
            callbacks.onCallStateChange(newState);
        }
        updateUI();
    }

    function updateUI() {
        var $status = $('#webphone-status');
        var $callBtn = $('#webphone-btn-call');
        var $hangupBtn = $('#webphone-btn-hangup');
        var $answerBtn = $('#webphone-btn-answer');
        var $reconnectBtn = $('#webphone-btn-reconnect');
        var $muteBtn = $('#webphone-btn-mute');
        var $dialpad = $('#webphone-dialpad');
        var $statusText = $status.find('.status-text');
        var $callInfo = $('#webphone-call-info');

        // Nuevos selectores para Hold y Transferencia
        var $holdBtn = $('#webphone-btn-hold');
        var $transferBtn = $('#webphone-btn-transfer');
        var $transferRow = $('#webphone-transfer-row');
        var $heldInfo = $('#webphone-held-info');
        var $heldNumber = $('#webphone-held-number');

        // Remove all call-related classes
        $status.removeClass('webphone-calling webphone-ringing-incoming webphone-connected');

        // Control del panel de llamada retenida (Hold)
        if (heldSession) {
            var heldNum = (heldSession.remoteIdentity && heldSession.remoteIdentity.uri && heldSession.remoteIdentity.uri.user) || 'Desconocido';
            $heldNumber.text(heldNum);
            $heldInfo.css('display', 'flex');
        } else {
            $heldInfo.hide();
        }

        var $gestionBtn = $('#webphone-btn-gestion');
        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
            $gestionBtn.hide();
        } else if (state.lastCallError) {
            $status.removeClass('webphone-registered webphone-connected').addClass('webphone-unregistered');
            $statusText.text(state.lastCallError);
            $gestionBtn.hide();
        } else if (state.registered) {
            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');
            $statusText.text('Registrado');
            $gestionBtn.show();
            
            // Sync active state based on global estadoCliente if available
            if (typeof estadoCliente !== 'undefined' && estadoCliente.break_id != null) {
                var $gestionQuickBtn = window.jQuery('.btn-quickbreak').filter(function() {
                    var text = window.jQuery(this).text().toUpperCase();
                    return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
                });
                if ($gestionQuickBtn.length && $gestionQuickBtn.data('breakid') == estadoCliente.break_id) {
                    $gestionBtn.addClass('active').text('Fin Gestión');
                } else {
                    $gestionBtn.removeClass('active').text('Gestión');
                }
            } else {
                $gestionBtn.removeClass('active').text('Gestión');
            }
        } else {
            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');
            $statusText.text('No registrado');
            $gestionBtn.hide();
        }

        // Show reconnect button only on auth failure
        if (state.authFailed) {
            $reconnectBtn.show();
        } else {
            $reconnectBtn.hide();
        }

        switch(state.callState) {
            case 'idle':
                $callBtn.show().prop('disabled', !state.registered);
                $hangupBtn.hide();
                $answerBtn.hide();
                $muteBtn.hide();
                $holdBtn.hide();
                $transferBtn.hide();
                $transferRow.hide();
                setMute(false); // Reset mute state when idle
                $('#webphone-number').prop('disabled', false);
                var activeEl = document.activeElement;
                var isTypingElsewhere = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable) && activeEl.id !== 'webphone-number';
                if (!isTypingElsewhere) {
                    $('#webphone-number').focus();
                }
                stopRingtoneSound();
                state.activeNumber = ''; // Clear active number
                break;
            case 'calling':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $muteBtn.hide();
                $holdBtn.hide();
                $transferBtn.hide();
                $transferRow.hide();
                setMute(false); // Reset mute state when dialing
                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-calling');
                $statusText.text('LLAMANDO...');
                playRingtoneSound('outgoing');
                break;
            case 'ringing':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.show().prop('disabled', false);
                $muteBtn.hide();
                $holdBtn.hide();
                $transferBtn.hide();
                $transferRow.hide();
                setMute(false); // Reset mute state when ringing
                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-ringing-incoming');
                $statusText.text('LLAMADA ENTRANTE!');
                playRingtoneSound('incoming');
                break;
            case 'connected':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $muteBtn.show().prop('disabled', false);

                // Control de los botones de Hold y Transferencia en estado conectado
                if (heldSession) {
                    // Si hay una llamada retenida, no se muestra Hold directo (se maneja alternando),
                    // pero se muestra Transferir para realizar transferencia atendida.
                    $holdBtn.hide();
                    $transferBtn.show().text('Transferir').prop('disabled', false);
                } else {
                    $holdBtn.show().text('Hold').removeClass('holding').prop('disabled', false);
                    $transferBtn.show().text('Transferir').prop('disabled', false);
                }

                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-connected');
                if (state.isVoicemail) {
                    $statusText.text('BUZÓN DE VOZ');
                } else {
                    $statusText.text('EN LLAMADA');
                }
                stopRingtoneSound();
                break;
        }

        if (state.callState === 'connected') {
            $dialpad.show();
        } else {
            $dialpad.hide();
        }

        // Garantizar que el botón de gestión NUNCA se muestre fuera de la consola de agente
        var isConsole = $('#issabel-callcenter-area-principal').length > 0;
        if (!isConsole) {
            $gestionBtn.hide();
        }

        // === Layout dinámico de botones según visibilidad ===
        // CSS no puede detectar display:none de hermanos; lo manejamos en JS.
        var gestionVisible = $gestionBtn.is(':visible');
        var answerVisible  = $answerBtn.is(':visible');

        // LLAMAR: full width cuando Gestión oculta (login), mitad cuando Gestión visible (consola)
        $callBtn.css('grid-column', gestionVisible ? 'span 1' : 'span 2');

        // COLGAR:
        //   - Ringing (Contestar visible): span 1 para quedar junto a Contestar
        //   - Calling con Gestión visible: span 1 para quedar junto a Gestión
        //   - Connected (sin Contestar): span 2 (botón principal de acción)
        if (answerVisible) {
            $hangupBtn.css('grid-column', 'span 1');
        } else if (state.callState === 'calling' && gestionVisible) {
            $hangupBtn.css('grid-column', 'span 1');
        } else {
            $hangupBtn.css('grid-column', 'span 2');
        }

        // Show/hide call info panel based on active number
        if ($callInfo.length) {
            var $callTimer = $callInfo.find('.call-timer');
            if (state.callState !== 'idle' && state.activeNumber) {
                var infoLabel = 'Llamada';
                if (state.callState === 'calling') {
                    infoLabel = 'Llamando a';
                    $callTimer.hide();
                } else if (state.callState === 'ringing') {
                    infoLabel = 'Llamada de';
                    $callTimer.hide();
                } else if (state.callState === 'connected') {
                    infoLabel = 'En llamada con';
                    $callTimer.show();
                    if (!callTimerInterval) {
                        callTimerInterval = setInterval(function() {
                            if (state.callState !== 'connected') return;
                            var now = new Date().getTime();
                            var diff = Math.floor((now - state.callStartTime) / 1000);
                            var m = Math.floor(diff / 60);
                            var s = diff % 60;
                            m = m < 10 ? '0' + m : m;
                            s = s < 10 ? '0' + s : s;
                            $callTimer.text(m + ':' + s);
                        }, 1000);
                    }
                }
                $callInfo.find('.caller-id').text(infoLabel + ': ' + state.activeNumber);
                $callInfo.addClass('active').show();
            } else {
                $callInfo.removeClass('active').hide();
                $callInfo.find('.caller-id').text('');
                $callTimer.hide().text('00:00');
                if (callTimerInterval) {
                    clearInterval(callTimerInterval);
                    callTimerInterval = null;
                }
            }
        }
    }


    function init(cfg, cbs) {
        config = Object.assign(config, cfg);
        callbacks = Object.assign(callbacks, cbs);
        registerAttempts = 0;
        state.authFailed = false;

        log('Initializing WebPhone for extension: ' + config.extension);

        if (typeof SIP === 'undefined') {
            log('ERROR: SIP.js library not loaded');
            if (callbacks.onError) callbacks.onError('SIP.js library not loaded');
            return false;
        }

        createAudioElements();
        createUserAgent();
        return true;
    }

    function createAudioElements() {
        if (!audioElements.remote) {
            audioElements.remote = document.createElement('audio');
            audioElements.remote.id = 'webphone-remote-audio';
            audioElements.remote.autoplay = true;
            document.body.appendChild(audioElements.remote);
        }
        if (!audioElements.local) {
            audioElements.local = document.createElement('audio');
            audioElements.local.id = 'webphone-local-audio';
            audioElements.local.muted = true;
            audioElements.local.autoplay = true;
            document.body.appendChild(audioElements.local);
        }
    }

    function createUserAgent() {
        var wsServer = 'wss://' + config.wssServer + ':' + config.wssPort + config.wssPath;
        log('WebSocket Server: ' + wsServer);

        var uri = SIP.UserAgent.makeURI('sip:' + config.extension + '@' + config.domain);
        if (!uri) {
            log('ERROR: Failed to create URI');
            showError('Failed to create SIP URI');
            return;
        }

        var options = {
            uri: uri,
            transportOptions: {
                server: wsServer,
                traceSip: false,
                connectionTimeout: 5,
                keepAliveInterval: 15,
                keepAliveDebounce: 10,
                reconnectionAttempts: 10,
                reconnectionDelay: 5
            },
            sessionDescriptionHandlerFactoryOptions: {
                peerConnectionConfiguration: {
                    bundlePolicy: 'balanced',
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                },
                iceGatheringTimeout: 2000
            },
            displayName: config.extension,
            authorizationUsername: config.extension,
            authorizationPassword: config.password,
            hackIpInContact: true,
            userAgentString: 'Issabel WebPhone 1.0 (SIP.js 0.20.0)',
            autoStart: false,
            autoStop: true,
            register: false,
            noAnswerTimeout: 60,
            logLevel: 'warn',
            contactParams: { transport: 'wss' },
            delegate: {
                onInvite: function(session) {
                    handleIncomingCall(session);
                }
            }
        };

        try {
            userAgent = new SIP.UserAgent(options);

            userAgent.transport.onConnect = function() {
                log('WebSocket connected');
                registerAttempts = 0; // Reset attempts on successful connection
                if (!state.authFailed) {
                    register();
                }
            };

            userAgent.transport.onDisconnect = function(error) {
                log('WebSocket disconnected: ' + (error ? error : 'normal'));
                if (!state.authFailed) {
                    state.registered = false;
                    updateUI();
                    if (callbacks.onUnregistered) callbacks.onUnregistered();
                }
            };

            userAgent.start();

        } catch (e) {
            log('ERROR creating UserAgent: ' + e.message);
            showError(e.message);
        }
    }

    function showError(msg) {
        state.authFailed = true;
        state.registered = false;
        updateUI();
        log('ERROR: ' + msg);
        if (callbacks.onError) callbacks.onError(msg);
        
        // Update status text with error
        var $status = $('#webphone-status');
        $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
        $status.find('.status-text').text('Error: ' + msg);
    }

    function register() {
        if (!userAgent) {
            log('Cannot register: no UserAgent');
            return;
        }

        if (state.authFailed) {
            log('Already failed auth, not retrying');
            return;
        }

        registerAttempts++;
        if (registerAttempts > maxRegisterAttempts) {
            log('Max register attempts reached (' + maxRegisterAttempts + '), stopping');
            showError('Maximos intentos alcanzados');
            disconnect();
            return;
        }

        log('Registering... (attempt ' + registerAttempts + '/' + maxRegisterAttempts + ')');

        var registererOptions = {
            registrar: SIP.UserAgent.makeURI('sip:' + config.domain),
            expires: 300
        };

        registerer = new SIP.Registerer(userAgent, registererOptions);

        registerer.stateChange.addListener(function(newState) {
            log('Registerer state: ' + newState);
            switch(newState) {
                case SIP.RegistererState.Registered:
                    state.registered = true;
                    updateUI();
                    if (callbacks.onRegistered) callbacks.onRegistered();
                    break;
                case SIP.RegistererState.Unregistered:
                    state.registered = false;
                    updateUI();
                    if (callbacks.onUnregistered) callbacks.onUnregistered();
                    break;
                case SIP.RegistererState.Terminated:
                    state.registered = false;
                    updateUI();
                    break;
            }
        });

        registerer.register()
            .then(function() {
                log('Registration request sent successfully');
            })
            .catch(function(e) {
                var errorMsg = e.message || String(e);
                var statusCode = extractStatusCode(e);
                log('Registration failed: ' + errorMsg + ' (status: ' + statusCode + ')');
                
                if (statusCode === 401 || statusCode === 403) {
                    // Authentication failure - STOP to prevent fail2ban
                    log('AUTH FAILURE: Stopping all retry attempts to prevent fail2ban block');
                    showError('Contrasena incorrecta');
                    disconnect();
                } else {
                    showError('Registro fallo: ' + statusCode);
                }
            });
    }

    function extractStatusCode(e) {
        // Try to extract SIP status code from error object
        if (e && typeof e === 'object') {
            if (e.message && typeof e.message === 'string') {
                var match = e.message.match(/(\d{3})/);
                if (match) return parseInt(match[1], 10);
            }
            if (e.response && e.response.statusCode) {
                return e.response.statusCode;
            }
        }
        return 0;
    }

    function parseCallerIdHeader(headerValue) {
        if (!headerValue) return null;
        
        var displayName = '';
        var number = '';
        
        var nameMatch = headerValue.match(/"([^"]+)"/);
        if (nameMatch) {
            displayName = nameMatch[1].trim();
        }
        
        var uriMatch = headerValue.match(/<sip:([^@>]+)/);
        if (uriMatch) {
            number = uriMatch[1].trim();
        } else {
            var uriMatch2 = headerValue.match(/sip:([^@\s;>]+)/);
            if (uriMatch2) {
                number = uriMatch2[1].trim();
            }
        }
        
        if (!number) return null;
        
        if (displayName && displayName !== number) {
            return displayName + ' (' + number + ')';
        }
        return number;
    }

    function handleConnectedLineUpdate(message) {
        if (!message) return;
        
        var pai = message.getHeader('P-Asserted-Identity');
        var rpid = message.getHeader('Remote-Party-ID');
        
        log('Checking headers for connected line update. PAI: ' + pai + ', RPID: ' + rpid);
        
        var newCaller = parseCallerIdHeader(pai) || parseCallerIdHeader(rpid);
        if (newCaller) {
            log('Updating active number to: ' + newCaller);
            state.activeNumber = newCaller;
            updateUI();
        }
    }

    function bindSessionEvents(session, direction) {
        session.delegate = {
            onSessionDescriptionHandler: function(sdh, provisional) {
                log(direction + ' SessionDescriptionHandler created. Provisional: ' + provisional);
                attachMedia(sdh, session);
            },
            onInvite: function(request, response) {
                log(direction + ' Re-INVITE received');
                if (request && request.message) {
                    handleConnectedLineUpdate(request.message);
                }
            }
        };

        session.stateChange.addListener(function(newState) {
            log(direction + ' session state changed: ' + newState);
            switch(newState) {
                case SIP.SessionState.Established:
                    if (session === currentSession) {
                        if (direction === 'Incoming' && autoAnswerTimeout) {
                            clearTimeout(autoAnswerTimeout);
                            autoAnswerTimeout = null;
                        }
                        updateCallState('connected');
                        attachMedia(undefined, session);
                    }
                    break;
                case SIP.SessionState.Terminated:
                    log(direction + ' call terminated');
                    if (direction === 'Incoming' && autoAnswerTimeout) {
                        clearTimeout(autoAnswerTimeout);
                        autoAnswerTimeout = null;
                    }
                    stopRingtoneSound();
                    
                    if (session === currentSession) {
                        currentSession = null;
                        
                        // Auto-resume disabled: keep held session, update call state to idle
                        if (heldSession) {
                            log('Active call terminated. Keeping held session.');
                        }
                        updateCallState('idle');
                    } else if (session === heldSession) {
                        log('Held call terminated');
                        heldSession = null;
                        updateUI();
                    }
                    break;
            }
        });
    }

    function handleIncomingCall(session) {
        var caller = session.remoteIdentity.uri.user;
        if (session.remoteIdentity.displayName && session.remoteIdentity.displayName !== caller) {
            caller = session.remoteIdentity.displayName + ' (' + caller + ')';
        }
        log('Incoming call from: ' + caller);
        state.activeNumber = caller;
        
        // If there's already an active session, reject the new call
        if (currentSession) {
            log('Already in a call, rejecting incoming call');
            session.reject().catch(function(e) {
                log('Reject failed: ' + (e.message || e));
            });
            return;
        }
        
        currentSession = session;
        updateCallState('ringing');
        bindSessionEvents(currentSession, 'Incoming');
        
        // Trigger auto-answer if enabled
        triggerAutoAnswer();
    }

    function answer() {
        if (!currentSession) {
            log('No session to answer');
            return;
        }

        // Avoid duplicate answering attempts if already establishing or established
        if (currentSession.state === 'Establishing' || currentSession.state === 'Established') {
            log('Session is already establishing or established (' + currentSession.state + '). Ignoring duplicate answer call.');
            return;
        }

        log('Answering call...');

        var options = {
            sessionDescriptionHandlerOptions: {
                constraints: {
                    audio: true,
                    video: false
                }
            }
        };

        currentSession.accept(options).then(function() {
            log('Call answered');
            stopRingtoneSound();
            attachMedia();
        }).catch(function(e) {
            log('Failed to answer: ' + (e.message || e));
            // Only update state to idle if the current session is actually not establishing/established anymore
            if (currentSession && currentSession.state !== 'Establishing' && currentSession.state !== 'Established') {
                updateCallState('idle');
            }
        });
    }

    function hangup() {
        if (!currentSession) {
            log('No session to hangup');
            return;
        }

        var sessionState = currentSession.state;
        log('Hanging up... current session state: ' + sessionState);

        // Important: Don't nullify session immediately - let the state change listener handle cleanup
        // The listener will set currentSession = null when state becomes Terminated

        try {
            if (sessionState === SIP.SessionState.Initial || sessionState === SIP.SessionState.Establishing) {
                // Call not yet connected
                // For outgoing calls (Inviter): use cancel()
                // For incoming calls (Invitation): use reject()
                if (currentSession instanceof SIP.Invitation) {
                    // Incoming call - reject it
                    log('Rejecting incoming call (state: ' + sessionState + ')');
                    if (currentSession.reject) {
                        currentSession.reject().then(function() {
                            log('Reject sent successfully');
                        }).catch(function(e) {
                            log('Reject error: ' + (e.message || e));
                            forceCleanup();
                        });
                    } else {
                        log('No reject method, forcing cleanup');
                        forceCleanup();
                    }
                } else {
                    // Outgoing call - cancel it
                    log('Canceling outgoing call (state: ' + sessionState + ')');
                    if (currentSession.cancel) {
                        currentSession.cancel().then(function() {
                            log('Cancel sent successfully');
                        }).catch(function(e) {
                            log('Cancel error: ' + (e.message || e));
                            forceCleanup();
                        });
                    } else {
                        log('No cancel method, forcing cleanup');
                        forceCleanup();
                    }
                }
            } else if (sessionState === SIP.SessionState.Established) {
                // Call is active - send BYE
                log('Sending BYE (active call)');
                currentSession.bye().then(function() {
                    log('BYE sent successfully');
                }).catch(function(e) {
                    log('BYE error: ' + (e.message || e));
                    forceCleanup();
                });
            } else {
                log('Session in unexpected state: ' + sessionState + ', forcing cleanup');
                forceCleanup();
            }
        } catch (e) {
            log('Exception during hangup: ' + e.message);
            forceCleanup();
        }

        stopRingtoneSound();
    }

    function forceCleanup() {
        log('Force cleanup called');
        stopRingtoneSound();
        currentSession = null;
        updateCallState('idle');
    }

    function call(number) {
        if (!userAgent || !state.registered) {
            log('Cannot call: not registered');
            return;
        }

        if (!number || number.trim() === '') {
            log('Cannot call: no number provided');
            return;
        }

        // If already in a call, don't start a new one
        if (currentSession) {
            log('Already in a call, cannot dial');
            return;
        }

        log('Calling: ' + number);
        state.lastCallError = ''; // Clear previous error
        state.isVoicemail = false; // Reset voicemail flag
        earlyMediaReceived = false; // Reset early media flag for new call
        state.activeNumber = number; // Set active call number

        var target = SIP.UserAgent.makeURI('sip:' + number + '@' + config.domain);
        if (!target) {
            log('Invalid target URI');
            return;
        }

        updateCallState('calling');

        var inviterOptions = {
            earlyMedia: true,
            sessionDescriptionHandlerOptions: {
                constraints: {
                    audio: true,
                    video: false
                }
            }
        };

        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);
        bindSessionEvents(currentSession, 'Outgoing');

        var inviteOptions = {
            requestDelegate: {
                onReject: function(response) {
                    var statusCode = response.message.statusCode;
                    var reason = response.message.reasonPhrase || 'Rechazado';
                    log('Call rejected, status code: ' + statusCode + ' reason: ' + reason);

                    if (statusCode === 487) {
                        return; // Normal cancellation when user hangs up before answering
                    }

                    var friendlyMessage = 'Llamada rechazada';
                    if (statusCode === 404) {
                        friendlyMessage = 'Número no existe (404)';
                    } else if (statusCode === 486) {
                        friendlyMessage = 'Línea ocupada (486)';
                    } else if (statusCode === 480) {
                        friendlyMessage = 'No disponible (480)';
                    } else if (statusCode === 403) {
                        friendlyMessage = 'Sin permisos (403)';
                    } else if (statusCode === 400) {
                        friendlyMessage = 'Número inválido (400)';
                    } else if (statusCode === 503) {
                        friendlyMessage = 'Congestión / Canales ocupados (503)';
                    } else {
                        friendlyMessage = 'Error ' + statusCode + ': ' + reason;
                    }

                    state.lastCallError = friendlyMessage;
                    updateUI();

                    // Clear error message after 5 seconds
                    setTimeout(function() {
                        if (state.lastCallError === friendlyMessage) {
                            state.lastCallError = '';
                            updateUI();
                        }
                    }, 5000);
                },
                onAccept: function(response) {
                    log('Call accepted (200 OK)');
                    if (response && response.message) {
                        var vmHeader = response.message.getHeader('X-Voicemail') || response.message.getHeader('X-Asterisk-Voicemail');
                        if (vmHeader && (vmHeader.toLowerCase() === 'yes' || vmHeader.toLowerCase() === 'true')) {
                            log('Detected voicemail answer via custom SIP header');
                            state.isVoicemail = true;
                            updateUI();
                        }
                    }
                }
            }
        };

        currentSession.invite(inviteOptions).then(function() {
            log('INVITE sent successfully');
        }).catch(function(e) {
            log('INVITE failed: ' + (e.message || e));
            stopRingtoneSound();
            currentSession = null;
            updateCallState('idle');
        });
    }

    function attachMedia(sdh, session) {
        var activeSession = session || currentSession;
        if (!activeSession) return;

        var handler = sdh || activeSession.sessionDescriptionHandler;
        if (!handler) {
            log('No sessionDescriptionHandler available');
            return;
        }

        var pc = handler.peerConnection;
        if (!pc) {
            log('No peerConnection available');
            return;
        }

        log('Attaching media, setting up track listeners');

        var remoteAudio = audioElements.remote;

        // Function to assign stream/track to audio element
        function setRemoteStream(stream) {
            if (remoteAudio.srcObject !== stream) {
                remoteAudio.srcObject = stream;
                log('Remote media stream assigned');
            }
            remoteAudio.play().catch(function(e) {
                log('Audio play failed: ' + e.message);
            });
        }

        // Set up ontrack listener on the peer connection if not already set
        if (!pc._mediaAttached) {
            pc._mediaAttached = true;
            pc.addEventListener('track', function(event) {
                log('pc ontrack event received, kind: ' + event.track.kind);
                if (state.callState === 'connected') {
                    // Call established: stop local ringtone, let remote audio play
                    stopRingtoneSound();
                    remoteAudio.muted = false;
                } else if (state.callState === 'calling') {
                    // Early media (183 Session Progress) from provider:
                    // Stop our synthetic local tone and let the provider's ringback play.
                    // This avoids the double-beep where both the local tone and provider
                    // ringback sound simultaneously.
                    if (!earlyMediaReceived) {
                        earlyMediaReceived = true;
                        log('Early media received from provider — stopping local ringback tone, using provider audio');
                        stopRingtoneSound();
                        remoteAudio.muted = false;
                    }
                } else {
                    log('Track received in state: ' + state.callState);
                    remoteAudio.muted = false;
                }
                if (event.streams && event.streams[0]) {
                    setRemoteStream(event.streams[0]);
                } else {
                    var stream = remoteAudio.srcObject || new MediaStream();
                    stream.addTrack(event.track);
                    setRemoteStream(stream);
                }
            });
        }

        // Also check if receivers already have tracks (call already has early media)
        var remoteStream = null;
        pc.getReceivers().forEach(function(receiver) {
            if (receiver.track) {
                log('Found existing receiver track: ' + receiver.track.kind);
                if (state.callState === 'connected') {
                    stopRingtoneSound();
                    remoteAudio.muted = false;
                } else if (state.callState === 'calling' && !earlyMediaReceived) {
                    earlyMediaReceived = true;
                    log('Existing early media track — stopping local ringback, using provider audio');
                    stopRingtoneSound();
                    remoteAudio.muted = false;
                }
                if (!remoteStream) {
                    remoteStream = new MediaStream();
                }
                remoteStream.addTrack(receiver.track);
            }
        });

        if (remoteStream) {
            setRemoteStream(remoteStream);
        }
    }

    function disconnect() {
        log('Disconnecting...');

        stopRingtoneSound();

        if (heldSession) {
            hangupHeld();
        }

        if (currentSession) {
            hangup();
        }

        if (registerer) {
            registerer.unregister().catch(function(e) {
                log('Unregister failed: ' + (e.message || e));
            });
        }

        if (userAgent) {
            userAgent.stop().catch(function(e) {
                log('Stop failed: ' + (e.message || e));
            });
        }

        state.registered = false;
        updateUI();
    }

    function reconnect() {
        log('Reconnecting...');
        stopRingtoneSound();
        registerAttempts = 0;
        state.authFailed = false;
        state.registered = false;
        updateUI();
        
        if (userAgent) {
            userAgent.stop().then(function() {
                createUserAgent();
            }).catch(function() {
                createUserAgent();
            });
        } else {
            createUserAgent();
        }
    }

    var audioCtx = null;
    function playDTMFTone(tone) {
        var dtmfFreqs = {
            '1': [697, 1209],
            '2': [697, 1336],
            '3': [697, 1477],
            '4': [770, 1209],
            '5': [770, 1336],
            '6': [770, 1477],
            '7': [852, 1209],
            '8': [852, 1336],
            '9': [852, 1477],
            '*': [941, 1209],
            '0': [941, 1336],
            '#': [941, 1477]
        };
        var freqs = dtmfFreqs[tone];
        if (!freqs) return;
        try {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            var osc1 = audioCtx.createOscillator();
            var osc2 = audioCtx.createOscillator();
            var gainNode = audioCtx.createGain();
            osc1.type = 'sine';
            osc1.frequency.value = freqs[0];
            osc2.type = 'sine';
            osc2.frequency.value = freqs[1];
            gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
            osc1.connect(gainNode);
            osc2.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            osc1.start();
            osc2.start();
            osc1.stop(audioCtx.currentTime + 0.12);
            osc2.stop(audioCtx.currentTime + 0.12);
        } catch (e) {
            log('Failed to play DTMF tone: ' + e.message);
        }
    }

    function sendDTMF(tone) {
        if (!currentSession) {
            log('Cannot send DTMF: no active call session');
            return false;
        }
        var sdh = currentSession.sessionDescriptionHandler;
        var sent = false;
        if (sdh && typeof sdh.sendDtmf === 'function') {
            log('Sending DTMF tone via SDH: ' + tone);
            try {
                sdh.sendDtmf(tone);
                sent = true;
            } catch (e) {
                log('SDH sendDtmf failed: ' + e.message);
            }
        }
        if (!sent && typeof currentSession.info === 'function') {
            log('Sending DTMF tone via SIP INFO: ' + tone);
            try {
                var options = {
                    requestOptions: {
                        body: {
                            contentDisposition: "render",
                            contentType: "application/dtmf-relay",
                            content: "Signal=" + tone + "\r\nDuration=160"
                        }
                    }
                };
                currentSession.info(options);
                sent = true;
            } catch (e) {
                log('SIP INFO send failed: ' + e.message);
            }
        }
        if (sent) {
            playDTMFTone(tone);
            var $numInput = $('#webphone-number');
            if ($numInput.length) {
                $numInput.val($numInput.val() + tone);
            }
            return true;
        }
        log('Cannot send DTMF: no supported DTMF sending method found on session');
        return false;
    }

    function toggleMute() {
        setMute(!state.muted);
    }

    function setMute(muteVal) {
        state.muted = muteVal;
        
        var $muteBtn = $('#webphone-btn-mute');
        if (muteVal) {
            $muteBtn.addClass('muted').text('Silenciado');
        } else {
            $muteBtn.removeClass('muted').text('Silenciar');
        }

        if (!currentSession) {
            return;
        }

        var sdh = currentSession.sessionDescriptionHandler;
        if (!sdh) {
            log('No sessionDescriptionHandler to set mute');
            return;
        }

        var pc = sdh.peerConnection;
        if (!pc) {
            log('No peerConnection to set mute');
            return;
        }

        if (typeof pc.getSenders === 'function') {
            pc.getSenders().forEach(function(sender) {
                if (sender.track && sender.track.kind === 'audio') {
                    sender.track.enabled = !muteVal;
                }
            });
            log('Call audio tracks ' + (muteVal ? 'disabled (muted)' : 'enabled (unmuted)'));
        } else {
            log('getSenders is not supported on peerConnection');
        }
    }

    function toggleHold() {
        if (currentSession) {
            hold();
        }
    }

    function hold() {
        if (!currentSession) {
            log('No active call to hold');
            return;
        }

        var sessionToHold = currentSession;
        log('Holding active call with: ' + (sessionToHold.remoteIdentity && sessionToHold.remoteIdentity.uri && sessionToHold.remoteIdentity.uri.user));

        sessionToHold.sessionDescriptionHandlerOptionsReInvite = {
            constraints: {
                audio: true,
                video: false
            },
            hold: true
        };
        
        sessionToHold.invite().then(function() {
            log('Hold invite sent successfully');
        }).catch(function(e) {
            log('Hold invite failed: ' + e.message);
        });

        heldSession = sessionToHold;
        currentSession = null;
        updateCallState('idle');
    }

    function resume() {
        if (!heldSession) {
            log('No call in hold to resume');
            return;
        }

        var sessionToResume = heldSession;
        log('Resuming call with: ' + (sessionToResume.remoteIdentity && sessionToResume.remoteIdentity.uri && sessionToResume.remoteIdentity.uri.user));

        // If there is an active call, hold it first (automatic swap)
        if (currentSession) {
            var activeSession = currentSession;
            log('Holding current active call before resuming: ' + (activeSession.remoteIdentity && activeSession.remoteIdentity.uri && activeSession.remoteIdentity.uri.user));
            activeSession.sessionDescriptionHandlerOptionsReInvite = {
                constraints: {
                    audio: true,
                    video: false
                },
                hold: true
            };
            activeSession.invite().catch(function(e) {
                log('Hold of active call failed: ' + e.message);
            });
            
            heldSession = activeSession;
        } else {
            heldSession = null;
        }

        sessionToResume.sessionDescriptionHandlerOptionsReInvite = {
            constraints: {
                audio: true,
                video: false
            },
            hold: false
        };

        sessionToResume.invite().then(function() {
            log('Resume invite sent successfully');
        }).catch(function(e) {
            log('Resume invite failed: ' + e.message);
        });

        currentSession = sessionToResume;
        
        var resumedNum = (sessionToResume.remoteIdentity && sessionToResume.remoteIdentity.uri && sessionToResume.remoteIdentity.uri.user) || 'Desconocido';
        if (sessionToResume.remoteIdentity && sessionToResume.remoteIdentity.displayName && sessionToResume.remoteIdentity.displayName !== resumedNum) {
            resumedNum = sessionToResume.remoteIdentity.displayName + ' (' + resumedNum + ')';
        }
        state.activeNumber = resumedNum;

        updateCallState('connected');
        attachMedia(undefined, currentSession);
    }

    function hangupHeld() {
        if (!heldSession) {
            log('No held call to hangup');
            return;
        }

        log('Hanging up held call...');
        try {
            if (heldSession.bye) {
                heldSession.bye().catch(function(e) {
                    log('Bye error on held call: ' + e.message);
                });
            } else if (heldSession.cancel) {
                heldSession.cancel().catch(function(e) {
                    log('Cancel error on held call: ' + e.message);
                });
            }
        } catch (e) {
            log('Exception hanging up held call: ' + e.message);
        }

        heldSession = null;
        updateUI();
    }

    function transfer(target) {
        if (heldSession && currentSession) {
            log('Attended transfer triggered: bridging held session and active session');
            heldSession.refer(currentSession).then(function() {
                log('Attended transfer refer sent, hanging up both sessions');
                var activeToBye = currentSession;
                var heldToBye = heldSession;
                heldSession = null;
                currentSession = null;
                if (heldToBye) heldToBye.bye().catch(function() {});
                if (activeToBye) activeToBye.bye().catch(function() {});
                updateCallState('idle');
            }).catch(function(e) {
                log('Attended transfer failed: ' + e.message);
            });
        } else if (target) {
            var sessionToTransfer = currentSession || heldSession;
            if (!sessionToTransfer) {
                log('No session to transfer');
                return;
            }

            log('Blind transfer triggered to: ' + target);
            var targetURI = SIP.UserAgent.makeURI('sip:' + target + '@' + config.domain);
            if (!targetURI) {
                log('Invalid transfer target URI');
                return;
            }

            sessionToTransfer.refer(targetURI).then(function() {
                log('Blind transfer refer sent successfully, hanging up local session');
                if (sessionToTransfer === currentSession) {
                    currentSession.bye().catch(function() {});
                    currentSession = null;
                    updateCallState('idle');
                } else {
                    heldSession.bye().catch(function() {});
                    heldSession = null;
                    updateUI();
                }
            }).catch(function(e) {
                log('Blind transfer failed: ' + e.message);
            });
        }
    }

    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });


    // Global Event Handlers for Extension Directory
    $(document).ready(function() {
        var extensionsCache = [];

        $(document).on('click', '#webphone-btn-directory', function() {
            var $panel = $('#webphone-directory-panel');
            if ($panel.is(':visible')) {
                $panel.slideUp(200);
            } else {
                $panel.slideDown(200);
                $('#webphone-directory-search').val('').focus();
                loadDirectoryList();
            }
        });

        $(document).on('click', '#webphone-directory-close', function() {
            $('#webphone-directory-panel').slideUp(200);
        });

        $(document).on('keyup', '#webphone-directory-search', function() {
            var search = $(this).val().toLowerCase().trim();
            filterDirectory(search);
        });

        $(document).on('click', '.directory-item-row', function() {
            var ext = $(this).data('extension');
            if ($('#webphone-transfer-row').is(':visible')) {
                $('#webphone-transfer-number').val(ext).focus();
            } else {
                var $numInput = $('#webphone-number');
                if (!$numInput.prop('disabled')) {
                    $numInput.val(ext).focus();
                }
            }
            $('#webphone-directory-panel').slideUp(200);
        });

        function loadDirectoryList() {
            var $loading = $('.directory-loading');
            var $table = $('.directory-table');
            var $list = $('#webphone-directory-list');

            $loading.show().text('Cargando extensiones...');
            $table.hide();
            $list.empty();

            var menu = (config && config.moduleName) ? config.moduleName : 'agent_console';
            window.jQuery.getJSON('index.php?menu=' + menu + '&action=getExtensionsList', function(data) {
                extensionsCache = data;
                renderDirectory(data);
                $loading.hide();
                $table.show();
            }).fail(function() {
                $loading.show().text('Error al cargar extensiones');
            });
        }

        function renderDirectory(items) {
            var $list = $('#webphone-directory-list');
            $list.empty();
            if (!items || items.length === 0) {
                $list.append('<tr><td colspan="3" style="text-align:center; color:#999;">Sin resultados</td></tr>');
                return;
            }
            items.forEach(function(item) {
                var dotClass = item.status === 'online' ? 'online' : 'offline';
                var statusText = item.status === 'online' ? 'Disponible' : 'No disponible';
                var row = $('<tr class="directory-item-row" data-extension="' + item.extension + '">' +
                    '<td style="font-weight:bold; padding: 6px 4px; border-bottom: 1px solid #eee;">' + item.extension + '</td>' +
                    '<td style="padding: 6px 4px; border-bottom: 1px solid #eee;">' + item.name + '</td>' +
                    '<td style="white-space:nowrap; padding: 6px 4px; border-bottom: 1px solid #eee;"><span class="status-dot ' + dotClass + '"></span>' + statusText + '</td>' +
                    '</tr>');
                $list.append(row);
            });
        }

        function filterDirectory(search) {
            if (!search) {
                renderDirectory(extensionsCache);
                return;
            }
            var filtered = extensionsCache.filter(function(item) {
                var extMatch = item.extension.indexOf(search) !== -1;
                var nameMatch = item.name && item.name.toLowerCase().indexOf(search) !== -1;
                return extMatch || nameMatch;
            });
            renderDirectory(filtered);
        }
    });

    // Public API
    return {
        init: init,
        call: call,
        answer: answer,
        hangup: hangup,
        disconnect: disconnect,
        reconnect: reconnect,
        setAutoAnswer: setAutoAnswer,
        loadAutoAnswerPreference: loadAutoAnswerPreference,
        toggleMute: toggleMute,
        sendDTMF: sendDTMF,
        setMute: setMute,
        toggleHold: toggleHold,
        hold: hold,
        resume: resume,
        hangupHeld: hangupHeld,
        transfer: transfer,
        getAudioElements: function() { return audioElements; },
        isRegistered: function() { return state.registered; },
        getState: function() {
            var s = Object.assign({}, state);
            s.heldSession = heldSession;
            return s;
        },
        isAutoAnswer: function() { return state.autoAnswer; }
    };
})();
