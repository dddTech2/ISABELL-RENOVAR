import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Reconnect and Takeover Fix ===")

    # 1. Update reconnect() in sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()

        target_reconnect = """    function reconnect() {
        log('Reconnecting...');
        stopRingtoneSound();
        registerAttempts = 0;
        state.authFailed = false;
        state.registered = false;
        updateUI();
        
        if (userAgent) {"""

        replacement_reconnect = """    function reconnect() {
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

        if target_reconnect in content:
            content = content.replace(target_reconnect, replacement_reconnect)
            print("Patched reconnect() function in sip-phone.js.")
        else:
            print("Target reconnect() pattern not found. Checking if already patched...")
            if "state.takenOver = false; // Reset takenOver state when manually reconnecting" in content:
                print("reconnect() is already patched.")
            else:
                print("Error: Could not find target reconnect() pattern in sip-phone.js.")
                return 1

        with open(sip_phone_js, 'w', encoding='utf-8') as f:
            f.write(content)
        print("sip-phone.js patched successfully.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php (bump cache version from v=14 to v=15)
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=14", "webphone.css?v=15")
        content = content.replace("sip-phone.js?v=14", "sip-phone.js?v=15")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=15")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console_tpl (bump cache version from v=14 to v=15)
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=14", "webphone.css?v=15")
        content = content.replace("sip-phone.js?v=14", "sip-phone.js?v=15")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=15")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("All fixes applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
