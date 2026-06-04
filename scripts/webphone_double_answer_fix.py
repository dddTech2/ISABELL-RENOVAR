import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Double Answer/Accept Fix ===")

    # 1. Update sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_func = """    function answer() {
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
    }"""

        replacement_func = """    function answer() {
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
    }"""

        if target_func in content:
            content = content.replace(target_func, replacement_func)
            with open(sip_phone_js, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully updated sip-phone.js: patched answer() to check currentSession.state.")
        else:
            print("Target answer() function not found in sip-phone.js or already patched.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=9", "webphone.css?v=10")
        content = content.replace("sip-phone.js?v=9", "sip-phone.js?v=10")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=10")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=9", "webphone.css?v=10")
        content = content.replace("sip-phone.js?v=9", "sip-phone.js?v=10")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=10")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Double answer fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
