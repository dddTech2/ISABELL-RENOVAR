#!/usr/bin/env python3
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sip_phone_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'sip-phone.js')
    
    if not os.path.exists(sip_phone_js):
        print(f"Error: File not found {sip_phone_js}")
        return
        
    with open(sip_phone_js, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if patch is already applied
    if 'keepAliveInterval: 15' in content:
        print("Keepalive and Reconnect patch already present in sip-phone.js")
        return

    # 1. Update transportOptions
    target_options = """            transportOptions: {
                server: wsServer,
                traceSip: false,
                connectionTimeout: 5,
                reconnectionAttempts: 0,
                reconnectionTimeout: 0
            },"""

    replacement_options = """            transportOptions: {
                server: wsServer,
                traceSip: false,
                connectionTimeout: 5,
                keepAliveInterval: 15,
                keepAliveDebounce: 10,
                reconnectionAttempts: 10,
                reconnectionTimeout: 5
            },"""

    if target_options not in content:
        print("Error: Could not find target transportOptions pattern in sip-phone.js")
        return
    content = content.replace(target_options, replacement_options, 1)

    # 2. Reset registerAttempts on Connect
    target_onconnect = """            userAgent.transport.onConnect = function() {
                log('WebSocket connected');
                if (!state.authFailed) {
                    register();
                }
            };"""

    replacement_onconnect = """            userAgent.transport.onConnect = function() {
                log('WebSocket connected');
                registerAttempts = 0; // Reset attempts on successful connection
                if (!state.authFailed) {
                    register();
                }
            };"""

    if target_onconnect not in content:
        print("Error: Could not find target onConnect pattern in sip-phone.js")
        return
    content = content.replace(target_onconnect, replacement_onconnect, 1)

    # 3. Add page visibility listener before return Public API
    target_api = """    // Public API
    return {"""

    replacement_api = """    // Handle tab visibility change to recover connection if throttled
    window.jQuery(document).on('visibilitychange', function() {
        if (!document.hidden) {
            log('Tab became visible. Checking connection status...');
            if (userAgent && !state.registered && !state.authFailed) {
                log('WebPhone is not registered. Forcing reconnect...');
                reconnect();
            }
        }
    });

    // Public API
    return {"""

    if target_api not in content:
        print("Error: Could not find target Public API return pattern in sip-phone.js")
        return
    content = content.replace(target_api, replacement_api, 1)

    # Save changes
    with open(sip_phone_js, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Successfully patched keep-alive and reconnection features in sip-phone.js")

if __name__ == '__main__':
    main()
