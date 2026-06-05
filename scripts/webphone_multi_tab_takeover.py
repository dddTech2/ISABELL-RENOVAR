import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    webphone_css = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Multi-Tab Takeover Patch ===")

    # 1. Update webphone.css to add .webphone-taken-over
    if os.path.exists(webphone_css):
        with open(webphone_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_css = """.webphone-auth-failed .status-indicator {
    background: #f0ad4e;
}"""

        replacement_css = """.webphone-auth-failed .status-indicator {
    background: #f0ad4e;
}

.webphone-taken-over {
    background: #fcf8e3;
    color: #8a6d3b;
    border: 1px solid #f0ad4e;
}

.webphone-taken-over .status-indicator {
    background: #f0ad4e;
    box-shadow: 0 0 6px #f0ad4e;
}"""

        if "webphone-taken-over" not in content:
            if target_css in content:
                content = content.replace(target_css, replacement_css)
                with open(webphone_css, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Successfully updated webphone.css: added .webphone-taken-over styles.")
            else:
                print("Target CSS pattern not found in webphone.css.")
        else:
            print("webphone-taken-over styles already present in webphone.css.")
    else:
        print(f"Error: webphone.css not found at {webphone_css}")
        return 1

    # 2. Update sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add var broadcastChannel = null;
        target_var = "    var userAgent = null;\n    var registerer = null;"
        replacement_var = "    var userAgent = null;\n    var registerer = null;\n    var broadcastChannel = null;"
        if "var broadcastChannel = null;" not in content:
            content = content.replace(target_var, replacement_var)
            print("Added broadcastChannel variable definition.")

        # Update state object
        target_state = """    var state = {
        registered: false,
        callState: 'idle', // idle, calling, ringing, connected
        authFailed: false,
        autoAnswer: false,
        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)
        isVoicemail: false, // Track if call was answered by a voicemail system
        muted: false, // Track mute state
        activeNumber: '', // Active call number/identifier
        callStartTime: null
    };"""

        replacement_state = """    var state = {
        registered: false,
        callState: 'idle', // idle, calling, ringing, connected
        authFailed: false,
        autoAnswer: false,
        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)
        isVoicemail: false, // Track if call was answered by a voicemail system
        muted: false, // Track mute state
        activeNumber: '', // Active call number/identifier
        callStartTime: null,
        takenOver: false
    };"""

        if "takenOver: false" not in content:
            content = content.replace(target_state, replacement_state)
            print("Added takenOver to state object.")

        # Update updateUI() - status styling
        target_ui_status = """        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
            $gestionBtn.hide();
        } else if (state.lastCallError) {"""

        replacement_ui_status = """        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered webphone-taken-over').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
            $gestionBtn.hide();
        } else if (state.takenOver) {
            $status.removeClass('webphone-registered webphone-unregistered webphone-auth-failed').addClass('webphone-taken-over');
            $statusText.text('Abierto en otra pestaña');
            $gestionBtn.hide();
        } else if (state.lastCallError) {"""

        if "state.takenOver" not in content:
            content = content.replace(target_ui_status, replacement_ui_status)
            print("Patched updateUI() status block.")

        # Update updateUI() - reconnect button
        target_ui_reconnect = """        // Show reconnect button only on auth failure
        if (state.authFailed) {
            $reconnectBtn.show();
        } else {
            $reconnectBtn.hide();
        }"""

        replacement_ui_reconnect = """        // Show reconnect button on auth failure or takeover
        if (state.authFailed || state.takenOver) {
            $reconnectBtn.show();
        } else {
            $reconnectBtn.hide();
        }"""

        content = content.replace(target_ui_reconnect, replacement_ui_reconnect)

        # Update updateUI() - call button disabled
        target_ui_call_btn = """            case 'idle':
                $callBtn.show().prop('disabled', !state.registered);"""

        replacement_ui_call_btn = """            case 'idle':
                $callBtn.show().prop('disabled', !state.registered || state.takenOver);"""

        content = content.replace(target_ui_call_btn, replacement_ui_call_btn)

        # Update showError()
        target_show_error = """        var $status = $('#webphone-status');
        $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');"""

        replacement_show_error = """        var $status = $('#webphone-status');
        $status.removeClass('webphone-registered webphone-unregistered webphone-taken-over').addClass('webphone-auth-failed');"""

        content = content.replace(target_show_error, replacement_show_error)

        # Update init()
        target_init = """    function init(cfg, cbs) {
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
    }"""

        replacement_init = """    function init(cfg, cbs) {
        config = Object.assign(config, cfg);
        callbacks = Object.assign(callbacks, cbs);
        registerAttempts = 0;
        state.authFailed = false;
        state.takenOver = false;

        log('Initializing WebPhone for extension: ' + config.extension);

        if (typeof SIP === 'undefined') {
            log('ERROR: SIP.js library not loaded');
            if (callbacks.onError) callbacks.onError('SIP.js library not loaded');
            return false;
        }

        if (window.BroadcastChannel) {
            if (broadcastChannel) {
                try { broadcastChannel.close(); } catch(e) {}
            }
            broadcastChannel = new window.BroadcastChannel('issabel_webphone_' + config.extension);
            broadcastChannel.onmessage = function(event) {
                if (event.data === 'takeover') {
                    log('Received takeover message from another tab. Disconnecting WebPhone in this tab...');
                    state.takenOver = true;
                    disconnect();
                }
            };
            
            // Claim registration for this tab by broadcasting takeover
            log('Sending takeover message to other tabs on initialization...');
            broadcastChannel.postMessage('takeover');
        }

        createAudioElements();
        createUserAgent();
        return true;
    }"""

        if "window.BroadcastChannel" not in content:
            content = content.replace(target_init, replacement_init)
            print("Patched init() with BroadcastChannel initialization.")

        # Update reconnect()
        target_reconnect = """    function reconnect() {
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
    }"""

        replacement_reconnect = """    function reconnect() {
        log('Reconnecting...');
        stopRingtoneSound();
        registerAttempts = 0;
        state.authFailed = false;
        state.registered = false;
        state.takenOver = false; // Reset takeover state
        updateUI();
        
        // Claim registration by broadcasting takeover
        if (broadcastChannel) {
            log('Sending takeover message to other tabs on explicit reconnect...');
            broadcastChannel.postMessage('takeover');
        }
        
        if (userAgent) {
            userAgent.stop().then(function() {
                createUserAgent();
            }).catch(function() {
                createUserAgent();
            });
        } else {
            createUserAgent();
        }
    }"""

        if "state.takenOver = false;" not in content:
            content = content.replace(target_reconnect, replacement_reconnect)
            print("Patched reconnect() with takeover broadcast.")

        # Update watchdog
        target_watchdog = """    // Start a watchdog interval to ensure registration is maintained
    setInterval(function() {
        if (!state.registered && !state.authFailed && state.callState === 'idle' && userAgent) {
            log('Watchdog: WebPhone is not registered. Attempting auto-reconnection...');
            reconnect();
        }
    }, 30000); // Check every 30 seconds"""

        replacement_watchdog = """    // Start a watchdog interval to ensure registration is maintained
    setInterval(function() {
        if (!state.registered && !state.authFailed && !state.takenOver && state.callState === 'idle' && userAgent) {
            log('Watchdog: WebPhone is not registered. Attempting auto-reconnection...');
            reconnect();
        }
    }, 30000); // Check every 30 seconds"""

        content = content.replace(target_watchdog, replacement_watchdog)
        
        with open(sip_phone_js, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully updated sip-phone.js with BroadcastChannel logic and watchdog protection.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 3. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=12", "webphone.css?v=13")
        content = content.replace("sip-phone.js?v=12", "sip-phone.js?v=13")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=13")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 4. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=12", "webphone.css?v=13")
        content = content.replace("sip-phone.js?v=12", "sip-phone.js?v=13")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=13")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Multi-tab takeover patch applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
