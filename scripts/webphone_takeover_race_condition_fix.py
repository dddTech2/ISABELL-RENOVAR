import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Takeover Race Condition and Warnings Fix ===")

    # 1. Update sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add lastConnectTime to state
        target_state = """    var state = {
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
        takenOver: false,
        lastConnectTime: 0
    };"""

        if target_state in content:
            content = content.replace(target_state, replacement_state)
            print("Added lastConnectTime to state.")
        else:
            print("Target state pattern not found or already updated.")

        # Update createUserAgent() to set lastConnectTime
        target_cua = """    function createUserAgent() {
        var wsServer = 'wss://' + config.wssServer + ':' + config.wssPort + config.wssPath;"""

        replacement_cua = """    function createUserAgent() {
        state.lastConnectTime = new Date().getTime();
        var wsServer = 'wss://' + config.wssServer + ':' + config.wssPort + config.wssPath;"""

        if target_cua in content:
            content = content.replace(target_cua, replacement_cua)
            print("Updated createUserAgent to set lastConnectTime.")
        else:
            print("Target createUserAgent pattern not found or already updated.")

        # Update reconnect()
        target_reconnect = """    function reconnect() {
        log('Reconnecting...');
        stopRingtoneSound();
        registerAttempts = 0;
        state.authFailed = false;
        state.registered = false;
        state.takenOver = false; // Reset takenOver state when manually reconnecting
        updateUI();

        // Broadcast takeover message to other tabs to force them to disconnect
        if (window.BroadcastChannel && broadcastChannel) {
            log('Sending takeover message to other tabs on manual reconnect...');
            try {
                broadcastChannel.postMessage('takeover');
            } catch(e) {
                log('Failed to send takeover message: ' + e.message);
            }
        }
        
        if (userAgent) {"""

        replacement_reconnect = """    function reconnect() {
        log('Reconnecting...');
        state.lastConnectTime = new Date().getTime();
        stopRingtoneSound();
        registerAttempts = 0;
        state.authFailed = false;
        state.registered = false;
        state.takenOver = false; // Reset takenOver state when manually reconnecting
        updateUI();

        // Broadcast takeover message to other tabs to force them to disconnect
        if (window.BroadcastChannel && broadcastChannel) {
            log('Sending takeover message to other tabs on manual reconnect...');
            try {
                broadcastChannel.postMessage('takeover');
            } catch(e) {
                log('Failed to send takeover message: ' + e.message);
            }
        }

        if (registerer) {
            try {
                registerer.dispose();
            } catch(e) {}
            registerer = null;
        }
        
        if (userAgent) {"""

        if target_reconnect in content:
            content = content.replace(target_reconnect, replacement_reconnect)
            print("Updated reconnect() to set lastConnectTime and dispose of registerer.")
        else:
            print("Target reconnect() pattern not found or already updated.")

        # Update disconnect()
        target_disconnect = """        if (registerer) {
            registerer.unregister().catch(function(e) {
                log('Unregister failed: ' + (e.message || e));
            });
        }"""

        replacement_disconnect = """        if (registerer) {
            if (state.registered) {
                registerer.unregister().catch(function(e) {
                    log('Unregister failed: ' + (e.message || e));
                });
            }
            try {
                registerer.dispose();
            } catch(e) {}
            registerer = null;
        }"""

        if target_disconnect in content:
            content = content.replace(target_disconnect, replacement_disconnect)
            print("Updated disconnect() to dispose of registerer and only unregister if registered.")
        else:
            print("Target disconnect() pattern not found or already updated.")

        # Update visibilitychange and watchdog handlers to respect 15-second cooldown
        target_handlers = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed && !state.takenOver) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });

    // Start a watchdog interval to ensure registration is maintained
    setInterval(function() {
        if (!state.registered && !state.authFailed && !state.takenOver && state.callState === 'idle' && userAgent) {
            log('Watchdog: WebPhone is not registered. Attempting auto-reconnection...');
            reconnect();
        }
    }, 30000); // Check every 30 seconds"""

        replacement_handlers = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            var now = new Date().getTime();
            if (userAgent && !state.registered && !state.authFailed && !state.takenOver && (now - state.lastConnectTime > 15000)) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });

    // Start a watchdog interval to ensure registration is maintained
    setInterval(function() {
        var now = new Date().getTime();
        if (!state.registered && !state.authFailed && !state.takenOver && state.callState === 'idle' && userAgent && (now - state.lastConnectTime > 15000)) {
            log('Watchdog: WebPhone is not registered. Attempting auto-reconnection...');
            reconnect();
        }
    }, 30000); // Check every 30 seconds"""

        if target_handlers in content:
            content = content.replace(target_handlers, replacement_handlers)
            print("Updated visibilitychange and watchdog handlers to use lastConnectTime cooldown.")
        else:
            print("Target handlers pattern not found or already updated.")

        with open(sip_phone_js, 'w', encoding='utf-8') as f:
            f.write(content)
        print("sip-phone.js patched successfully.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php (bump cache version from v=15 to v=16)
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=15", "webphone.css?v=16")
        content = content.replace("sip-phone.js?v=15", "sip-phone.js?v=16")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=16")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console_tpl (bump cache version from v=15 to v=16)
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=15", "webphone.css?v=16")
        content = content.replace("sip-phone.js?v=15", "sip-phone.js?v=16")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=16")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("All fixes applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
