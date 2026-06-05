import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Takeover Focus and Reject handling Fix ===")

    # 1. Update sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update visibilitychange check
        target_visibility = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });"""

        replacement_visibility = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed && !state.takenOver) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });"""

        if target_visibility in content:
            content = content.replace(target_visibility, replacement_visibility)
            print("Patched visibilitychange handler in sip-phone.js to respect state.takenOver.")
        else:
            print("Target visibilitychange pattern not found or already patched.")

        # Update Registerer options to handle onReject
        target_registerer = """        var registererOptions = {
            registrar: SIP.UserAgent.makeURI('sip:' + config.domain),
            expires: 300
        };

        registerer = new SIP.Registerer(userAgent, registererOptions);"""

        replacement_registerer = """        var registererOptions = {
            registrar: SIP.UserAgent.makeURI('sip:' + config.domain),
            expires: 300,
            requestDelegate: {
                onReject: function(response) {
                    var statusCode = response.message.statusCode;
                    log('Registration rejected by server: status ' + statusCode);
                    if (statusCode === 401 || statusCode === 403) {
                        log('AUTH FAILURE: Stopping all retry attempts to prevent fail2ban block');
                        showError('Contrasena incorrecta');
                        disconnect();
                    } else {
                        showError('Registro fallo: ' + statusCode);
                    }
                }
            }
        };

        registerer = new SIP.Registerer(userAgent, registererOptions);"""

        if target_registerer in content:
            content = content.replace(target_registerer, replacement_registerer)
            print("Patched registererOptions to handle onReject (401/403).")
        else:
            print("Target registererOptions pattern not found or already patched.")

        with open(sip_phone_js, 'w', encoding='utf-8') as f:
            f.write(content)
        print("sip-phone.js patched successfully.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=13", "webphone.css?v=14")
        content = content.replace("sip-phone.js?v=13", "sip-phone.js?v=14")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=14")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console_tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=13", "webphone.css?v=14")
        content = content.replace("sip-phone.js?v=13", "sip-phone.js?v=14")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=14")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Focus and reject fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
