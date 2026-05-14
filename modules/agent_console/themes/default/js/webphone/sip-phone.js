/**
 * WebPhone Panel for Issabel Agent Console
 * Simplified SIP.js wrapper for basic call functionality
 * SECURITY: Stops on auth failure to prevent fail2ban blocks
 */

var WebPhone = (function() {
    var userAgent = null;
    var registerer = null;
    var currentSession = null;
    var registerAttempts = 0;
    var maxRegisterAttempts = 1;
    var config = {
        extension: '',
        password: '',
        domain: '',
        wssServer: '',
        wssPort: '8089',
        wssPath: '/ws',
        autoAnswerDelay: 500 // milliseconds before auto-answering
    };
    var audioElements = {
        remote: null,
        local: null
    };
    var state = {
        registered: false,
        callState: 'idle', // idle, calling, ringing, connected
        authFailed: false,
        autoAnswer: false
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
            }
        } catch (e) {}
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
            // Outgoing call ringback tone: periodic beeps
            var beepPattern = function() {
                if (!ringtoneGain) return;
                
                ringtoneOscillator = ctx.createOscillator();
                ringtoneOscillator.type = 'sine';
                ringtoneOscillator.frequency.value = 480; // Ringback tone frequency
                ringtoneOscillator.connect(ringtoneGain);
                ringtoneOscillator.start();
                
                setTimeout(function() {
                    if (ringtoneOscillator) {
                        ringtoneOscillator.stop();
                        ringtoneOscillator.disconnect();
                        ringtoneOscillator = null;
                    }
                }, 200);
            };
            
            beepPattern();
            ringtoneInterval = setInterval(beepPattern, 500);
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
        var $statusText = $status.find('.status-text');

        // Remove all call-related classes
        $status.removeClass('webphone-calling webphone-ringing-incoming webphone-connected');

        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
        } else if (state.registered) {
            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');
            $statusText.text('Registrado');
        } else {
            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');
            $statusText.text('No registrado');
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
                $('#webphone-number').prop('disabled', false);
                stopRingtoneSound();
                break;
            case 'calling':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-calling');
                $statusText.text('LLAMANDO...');
                playRingtoneSound('outgoing');
                break;
            case 'ringing':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.show().prop('disabled', false);
                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-ringing-incoming');
                $statusText.text('LLAMADA ENTRANTE!');
                playRingtoneSound('incoming');
                break;
            case 'connected':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $('#webphone-number').prop('disabled', true);
                $status.addClass('webphone-connected');
                $statusText.text('EN LLAMADA');
                stopRingtoneSound();
                break;
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
                reconnectionAttempts: 0,
                reconnectionTimeout: 0
            },
            sessionDescriptionHandlerFactoryOptions: {
                peerConnectionConfiguration: {
                    bundlePolicy: 'balanced',
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                },
                iceGatheringTimeout: 500
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

    function handleIncomingCall(session) {
        log('Incoming call from: ' + session.remoteIdentity.uri.user);
        
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

        session.stateChange.addListener(function(newState) {
            log('Incoming session state: ' + newState);
            switch(newState) {
                case SIP.SessionState.Established:
                    // Clear auto-answer timeout if call was answered manually
                    if (autoAnswerTimeout) {
                        clearTimeout(autoAnswerTimeout);
                        autoAnswerTimeout = null;
                    }
                    updateCallState('connected');
                    attachMedia();
                    break;
                case SIP.SessionState.Terminated:
                    log('Incoming call terminated');
                    // Clear auto-answer timeout
                    if (autoAnswerTimeout) {
                        clearTimeout(autoAnswerTimeout);
                        autoAnswerTimeout = null;
                    }
                    stopRingtoneSound();
                    currentSession = null;
                    updateCallState('idle');
                    break;
            }
        });
        
        // Trigger auto-answer if enabled
        triggerAutoAnswer();
    }

    function answer() {
        if (!currentSession) {
            log('No session to answer');
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
            updateCallState('idle');
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

        var target = SIP.UserAgent.makeURI('sip:' + number + '@' + config.domain);
        if (!target) {
            log('Invalid target URI');
            return;
        }

        updateCallState('calling');

        var inviterOptions = {
            sessionDescriptionHandlerOptions: {
                constraints: {
                    audio: true,
                    video: false
                }
            }
        };

        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);

        currentSession.stateChange.addListener(function(newState) {
            log('Outgoing session state: ' + newState);
            switch(newState) {
                case SIP.SessionState.Established:
                    updateCallState('connected');
                    attachMedia();
                    break;
                case SIP.SessionState.Terminated:
                    log('Outgoing call terminated');
                    stopRingtoneSound();
                    currentSession = null;
                    updateCallState('idle');
                    break;
            }
        });

        currentSession.invite().then(function() {
            log('INVITE sent successfully');
        }).catch(function(e) {
            log('INVITE failed: ' + (e.message || e));
            stopRingtoneSound();
            currentSession = null;
            updateCallState('idle');
        });
    }

    function attachMedia() {
        if (!currentSession) return;

        var pc = currentSession.sessionDescriptionHandler.peerConnection;
        if (!pc) {
            log('No peerConnection available');
            return;
        }

        // Get remote stream
        var remoteStream = new MediaStream();
        pc.getReceivers().forEach(function(receiver) {
            if (receiver.track) {
                remoteStream.addTrack(receiver.track);
            }
        });

        audioElements.remote.srcObject = remoteStream;
        audioElements.remote.play().catch(function(e) {
            log('Audio play failed: ' + e.message);
        });

        log('Remote media attached');
    }

    function disconnect() {
        log('Disconnecting...');

        stopRingtoneSound();

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
        isRegistered: function() { return state.registered; },
        getState: function() { return state; },
        isAutoAnswer: function() { return state.autoAnswer; }
    };
})();
