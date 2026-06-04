import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Attended Transfer Caller ID Update Fix ===")

    # 1. Update sip-phone.js to add parser and handle re-INVITE
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()

        # Target insertion point before bindSessionEvents
        target_insertion = "    function bindSessionEvents(session, direction) {"
        
        helpers_code = """    function parseCallerIdHeader(headerValue) {
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
            var uriMatch2 = headerValue.match(/sip:([^@\\s;>]+)/);
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

"""

        # Avoid double patching
        if "function parseCallerIdHeader(headerValue)" not in content:
            content = content.replace(target_insertion, helpers_code + target_insertion)
            print("Injected helper functions parseCallerIdHeader and handleConnectedLineUpdate.")
        else:
            print("Helper functions already present in sip-phone.js.")

        # Patch delegate inside bindSessionEvents
        target_delegate = """    function bindSessionEvents(session, direction) {
        session.delegate = {
            onSessionDescriptionHandler: function(sdh, provisional) {
                log(direction + ' SessionDescriptionHandler created. Provisional: ' + provisional);
                attachMedia(sdh, session);
            }
        };"""

        replacement_delegate = """    function bindSessionEvents(session, direction) {
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
        };"""

        if target_delegate in content:
            content = content.replace(target_delegate, replacement_delegate)
            with open(sip_phone_js, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully updated session.delegate in bindSessionEvents to handle onInvite (re-INVITE).")
        else:
            print("Target delegate structure not found or already patched.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=10", "webphone.css?v=11")
        content = content.replace("sip-phone.js?v=10", "sip-phone.js?v=11")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=11")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=10", "webphone.css?v=11")
        content = content.replace("sip-phone.js?v=10", "sip-phone.js?v=11")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=11")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Transfer identity update fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
