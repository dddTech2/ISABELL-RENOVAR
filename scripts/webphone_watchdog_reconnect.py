import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Watchdog Connection Auto-Reconnect ===")

    # 1. Update sip-phone.js to add the watchdog interval
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_str = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });"""

        replacement_str = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });

    // Start a watchdog interval to ensure registration is maintained
    setInterval(function() {
        if (!state.registered && !state.authFailed && state.callState === 'idle' && userAgent) {
            log('Watchdog: WebPhone is not registered. Attempting auto-reconnection...');
            reconnect();
        }
    }, 30000); // Check every 30 seconds"""

        if target_str in content:
            content = content.replace(target_str, replacement_str)
            with open(sip_phone_js, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully updated sip-phone.js: added watchdog interval.")
        else:
            print("Target visibilitychange pattern not found in sip-phone.js or already patched.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=11", "webphone.css?v=12")
        content = content.replace("sip-phone.js?v=11", "sip-phone.js?v=12")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=12")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=11", "webphone.css?v=12")
        content = content.replace("sip-phone.js?v=11", "sip-phone.js?v=12")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=12")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Watchdog auto-reconnect fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
