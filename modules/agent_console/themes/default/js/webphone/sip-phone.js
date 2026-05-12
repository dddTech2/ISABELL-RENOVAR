/**
 * WebPhone Panel for Issabel Agent Console
 * Simplified SIP.js wrapper for basic call functionality
 */

var WebPhone = (function() {
    var userAgent = null;
    var registerer = null;
    var currentSession = null;
    var config = {
        extension: '',
        password: '',
        domain: '',
        wssServer: '',
        wssPort: '8089',
        wssPath: '/ws'
    };
    var audioElements = {
        remote: null,
        local: null
    };
    var state = {
        registered: false,
        callState: 'idle' // idle, calling, ringing, connected
    };
    var callbacks = {
        onRegistered: null,
        onUnregistered: null,
        onCallStateChange: null,
        onError: null
    };

    function log(msg) {
        console.log('[WebPhone] ' + msg);
    }

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

        if (state.registered) {
            $status.removeClass('webphone-unregistered').addClass('webphone-registered');
            $status.find('.status-text').text('Registrado');
        } else {
            $status.removeClass('webphone-registered').addClass('webphone-unregistered');
            $status.find('.status-text').text('No registrado');
        }

        switch(state.callState) {
            case 'idle':
                $callBtn.show().prop('disabled', !state.registered);
                $hangupBtn.hide();
                $answerBtn.hide();
                $('#webphone-number').prop('disabled', false);
                break;
            case 'calling':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $('#webphone-number').prop('disabled', true);
                break;
            case 'ringing':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.show().prop('disabled', false);
                $('#webphone-number').prop('disabled', true);
                break;
            case 'connected':
                $callBtn.hide();
                $hangupBtn.show().prop('disabled', false);
                $answerBtn.hide();
                $('#webphone-number').prop('disabled', true);
                break;
        }
    }

    function init(cfg, cbs) {
        config = Object.assign(config, cfg);
        callbacks = Object.assign(callbacks, cbs);

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
        // Create remote audio element for incoming audio
        audioElements.remote = document.createElement('audio');
        audioElements.remote.id = 'webphone-remote-audio';
        audioElements.remote.autoplay = true;
        document.body.appendChild(audioElements.remote);

        // Local audio (for muting detection, not typically played)
        audioElements.local = document.createElement('audio');
        audioElements.local.id = 'webphone-local-audio';
        audioElements.local.muted = true;
        audioElements.local.autoplay = true;
        document.body.appendChild(audioElements.local);
    }

    function createUserAgent() {
        var wsServer = 'wss://' + config.wssServer + ':' + config.wssPort + config.wssPath;
        log('WebSocket Server: ' + wsServer);

        var uri = SIP.UserAgent.makeURI('sip:' + config.extension + '@' + config.domain);
        if (!uri) {
            log('ERROR: Failed to create URI');
            if (callbacks.onError) callbacks.onError('Failed to create SIP URI');
            return;
        }

        var options = {
            uri: uri,
            transportOptions: {
                server: wsServer,
                traceSip: false,
                connectionTimeout: 10
            },
            sessionDescriptionHandlerFactoryOptions: {
                peerConnectionConfiguration: {
                    bundlePolicy: 'balanced',
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                }
            },
            displayName: config.extension,
            authorizationUsername: config.extension,
            authorizationPassword: config.password,
            hackIpInContact: true,
            userAgentString: 'Issabel WebPhone 1.0 (SIP.js 0.20.0)',
            autoStart: true,
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
                register();
            };

            userAgent.transport.onDisconnect = function(error) {
                log('WebSocket disconnected: ' + (error ? error : 'normal'));
                state.registered = false;
                updateUI();
                if (callbacks.onUnregistered) callbacks.onUnregistered();
            };

            userAgent.start();

        } catch (e) {
            log('ERROR creating UserAgent: ' + e.message);
            if (callbacks.onError) callbacks.onError(e.message);
        }
    }

    function register() {
        if (!userAgent) {
            log('Cannot register: no UserAgent');
            return;
        }

        log('Registering...');

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

        registerer.register().catch(function(e) {
            log('Registration failed: ' + e.message || e);
            if (callbacks.onError) callbacks.onError('Registration failed');
        });
    }

    function handleIncomingCall(session) {
        log('Incoming call from: ' + session.remoteIdentity.uri.user);
        currentSession = session;
        updateCallState('ringing');

        session.stateChange.addListener(function(newState) {
            log('Session state: ' + newState);
            switch(newState) {
                case SIP.SessionState.Established:
                    updateCallState('connected');
                    attachMedia();
                    break;
                case SIP.SessionState.Terminated:
                    updateCallState('idle');
                    currentSession = null;
                    break;
            }
        });

        // Play ringtone (using system notification or audio)
        playRingtone(true);
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
            playRingtone(false);
            attachMedia();
        }).catch(function(e) {
            log('Failed to answer: ' + e.message || e);
            updateCallState('idle');
        });
    }

    function hangup() {
        if (!currentSession) {
            log('No session to hangup');
            return;
        }

        log('Hanging up...');

        if (currentSession.state === SIP.SessionState.Initial) {
            currentSession.cancel().catch(function(e) {
                log('Cancel failed: ' + e.message || e);
            });
        } else {
            currentSession.bye().catch(function(e) {
                log('Bye failed: ' + e.message || e);
            });
        }

        playRingtone(false);
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
            log('Session state: ' + newState);
            switch(newState) {
                case SIP.SessionState.Established:
                    updateCallState('connected');
                    attachMedia();
                    break;
                case SIP.SessionState.Terminated:
                    updateCallState('idle');
                    currentSession = null;
                    break;
            }
        });

        currentSession.invite().then(function() {
            log('INVITE sent');
        }).catch(function(e) {
            log('INVITE failed: ' + e.message || e);
            updateCallState('idle');
            currentSession = null;
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

    function playRingtone(play) {
        // Simple ringtone using Web Audio API or HTML5 audio
        // For now, we'll just use a visual indicator
        if (play) {
            $('#webphone-status').addClass('webphone-ringing');
        } else {
            $('#webphone-status').removeClass('webphone-ringing');
        }
    }

    function disconnect() {
        log('Disconnecting...');

        if (currentSession) {
            hangup();
        }

        if (registerer) {
            registerer.unregister().catch(function(e) {
                log('Unregister failed: ' + e.message || e);
            });
        }

        if (userAgent) {
            userAgent.stop().catch(function(e) {
                log('Stop failed: ' + e.message || e);
            });
        }

        state.registered = false;
        updateUI();
    }

    // Public API
    return {
        init: init,
        call: call,
        answer: answer,
        hangup: hangup,
        disconnect: disconnect,
        isRegistered: function() { return state.registered; },
        getState: function() { return state; }
    };
})();
