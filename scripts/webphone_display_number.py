import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    login_agent_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "login_agent.tpl")
    css_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Modifying template files:\n - {agent_console_tpl}\n - {login_agent_tpl}")
    print(f"Modifying CSS file: {css_file}")
    print(f"Modifying JS file: {js_file}")

    # 1. Modify agent_console.tpl
    if not os.path.exists(agent_console_tpl):
        print(f"Error: Template file not found at {agent_console_tpl}")
        return 1
    
    with open(agent_console_tpl, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_target = (
        '                    <div id="webphone-status" class="webphone-status webphone-unregistered">\n'
        '                        <span class="status-indicator"></span>\n'
        '                        <span class="status-text">Conectando...</span>\n'
        '                    </div>'
    )
    tpl_replace = (
        '                    <div id="webphone-status" class="webphone-status webphone-unregistered">\n'
        '                        <span class="status-indicator"></span>\n'
        '                        <span class="status-text">Conectando...</span>\n'
        '                    </div>\n'
        '                    <div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n'
        '                        <div class="caller-id"></div>\n'
        '                    </div>'
    )

    if tpl_target not in tpl_content_norm:
        print("Error: Target block not found in agent_console.tpl")
        return 1
    
    tpl_content_norm = tpl_content_norm.replace(tpl_target, tpl_replace)

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')
    
    with open(agent_console_tpl, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: agent_console.tpl updated.")

    # 2. Modify login_agent.tpl
    if not os.path.exists(login_agent_tpl):
        print(f"Error: Template file not found at {login_agent_tpl}")
        return 1
    
    with open(login_agent_tpl, 'r', encoding='utf-8') as f:
        login_content = f.read()

    login_content_norm = login_content.replace('\r\n', '\n')

    login_target = (
        '        <div id="webphone-status" class="webphone-status webphone-unregistered">\n'
        '            <span class="status-indicator"></span>\n'
        '            <span class="status-text">Conectando...</span>\n'
        '        </div>'
    )
    login_replace = (
        '        <div id="webphone-status" class="webphone-status webphone-unregistered">\n'
        '            <span class="status-indicator"></span>\n'
        '            <span class="status-text">Conectando...</span>\n'
        '        </div>\n'
        '        <div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n'
        '            <div class="caller-id"></div>\n'
        '        </div>'
    )

    if login_target not in login_content_norm:
        print("Error: Target block not found in login_agent.tpl")
        return 1
    
    login_content_norm = login_content_norm.replace(login_target, login_replace)

    if '\r\n' in login_content:
        login_content_norm = login_content_norm.replace('\n', '\r\n')
    
    with open(login_agent_tpl, 'w', encoding='utf-8') as f:
        f.write(login_content_norm)
    print("Success: login_agent.tpl updated.")

    # 3. Modify webphone.css
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_target = (
        '.webphone-call-info {\n'
        '    margin-top: 10px;\n'
        '    padding: 8px;\n'
        '    background: #fff;\n'
        '    border: 1px solid #ddd;\n'
        '    border-radius: 3px;\n'
        '    display: none;\n'
        '}'
    )
    css_replace = (
        '.webphone-call-info {\n'
        '    margin-top: 10px;\n'
        '    padding: 8px;\n'
        '    background: #fff;\n'
        '    border: 1px solid #ddd;\n'
        '    border-radius: 3px;\n'
        '    display: none;\n'
        '    text-align: center;\n'
        '}'
    )

    if css_target not in css_content_norm:
        print("Warning: Target block not found in webphone.css. Appending styling at the end.")
        css_content_norm += (
            '\n.webphone-call-info {\n'
            '    text-align: center;\n'
            '}\n'
        )
    else:
        css_content_norm = css_content_norm.replace(css_target, css_replace)

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: webphone.css updated.")

    # 4. Modify sip-phone.js
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Add activeNumber to state
    state_target = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "        isVoicemail: false, // Track if call was answered by a voicemail system\n"
        "        muted: false // Track mute state\n"
        "    };"
    )
    state_replace = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "        isVoicemail: false, // Track if call was answered by a voicemail system\n"
        "        muted: false, // Track mute state\n"
        "        activeNumber: '' // Active call number/identifier\n"
        "    };"
    )

    if state_target not in js_content_norm:
        print("Error: State definition target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(state_target, state_replace)

    # Add $callInfo to updateUI variables
    ui_var_target = (
        "    function updateUI() {\n"
        "        var $status = $('#webphone-status');\n"
        "        var $callBtn = $('#webphone-btn-call');\n"
        "        var $hangupBtn = $('#webphone-btn-hangup');\n"
        "        var $answerBtn = $('#webphone-btn-answer');\n"
        "        var $reconnectBtn = $('#webphone-btn-reconnect');\n"
        "        var $muteBtn = $('#webphone-btn-mute');\n"
        "        var $dialpad = $('#webphone-dialpad');\n"
        "        var $statusText = $status.find('.status-text');"
    )
    ui_var_replace = (
        "    function updateUI() {\n"
        "        var $status = $('#webphone-status');\n"
        "        var $callBtn = $('#webphone-btn-call');\n"
        "        var $hangupBtn = $('#webphone-btn-hangup');\n"
        "        var $answerBtn = $('#webphone-btn-answer');\n"
        "        var $reconnectBtn = $('#webphone-btn-reconnect');\n"
        "        var $muteBtn = $('#webphone-btn-mute');\n"
        "        var $dialpad = $('#webphone-dialpad');\n"
        "        var $statusText = $status.find('.status-text');\n"
        "        var $callInfo = $('#webphone-call-info');"
    )

    if ui_var_target not in js_content_norm:
        print("Error: updateUI variables target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(ui_var_target, ui_var_replace)

    # Clear activeNumber in idle state
    idle_target = (
        "            case 'idle':\n"
        "                $callBtn.show().prop('disabled', !state.registered);\n"
        "                $hangupBtn.hide();\n"
        "                $answerBtn.hide();\n"
        "                $muteBtn.hide();\n"
        "                $holdBtn.hide();\n"
        "                $transferBtn.hide();\n"
        "                $transferRow.hide();\n"
        "                setMute(false); // Reset mute state when idle\n"
        "                $('#webphone-number').prop('disabled', false);\n"
        "                var activeEl = document.activeElement;\n"
        "                var isTypingElsewhere = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable) && activeEl.id !== 'webphone-number';\n"
        "                if (!isTypingElsewhere) {\n"
        "                    $('#webphone-number').focus();\n"
        "                }\n"
        "                stopRingtoneSound();\n"
        "                break;"
    )
    idle_replace = (
        "            case 'idle':\n"
        "                $callBtn.show().prop('disabled', !state.registered);\n"
        "                $hangupBtn.hide();\n"
        "                $answerBtn.hide();\n"
        "                $muteBtn.hide();\n"
        "                $holdBtn.hide();\n"
        "                $transferBtn.hide();\n"
        "                $transferRow.hide();\n"
        "                setMute(false); // Reset mute state when idle\n"
        "                $('#webphone-number').prop('disabled', false);\n"
        "                var activeEl = document.activeElement;\n"
        "                var isTypingElsewhere = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable) && activeEl.id !== 'webphone-number';\n"
        "                if (!isTypingElsewhere) {\n"
        "                    $('#webphone-number').focus();\n"
        "                }\n"
        "                stopRingtoneSound();\n"
        "                state.activeNumber = ''; // Clear active number\n"
        "                break;"
    )

    if idle_target not in js_content_norm:
        print("Error: Idle case target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(idle_target, idle_replace)

    # Show/hide call info in updateUI
    dialpad_target = (
        "        if (answerVisible) {\n"
        "            $hangupBtn.css('grid-column', 'span 1');\n"
        "        } else if (state.callState === 'calling' && gestionVisible) {\n"
        "            $hangupBtn.css('grid-column', 'span 1');\n"
        "        } else {\n"
        "            $hangupBtn.css('grid-column', 'span 2');\n"
        "        }\n"
        "    }"
    )
    dialpad_replace = (
        "        if (answerVisible) {\n"
        "            $hangupBtn.css('grid-column', 'span 1');\n"
        "        } else if (state.callState === 'calling' && gestionVisible) {\n"
        "            $hangupBtn.css('grid-column', 'span 1');\n"
        "        } else {\n"
        "            $hangupBtn.css('grid-column', 'span 2');\n"
        "        }\n"
        "\n"
        "        // Show/hide call info panel based on active number\n"
        "        if ($callInfo.length) {\n"
        "            if (state.callState !== 'idle' && state.activeNumber) {\n"
        "                var infoLabel = 'Llamada';\n"
        "                if (state.callState === 'calling') {\n"
        "                    infoLabel = 'Llamando a';\n"
        "                } else if (state.callState === 'ringing') {\n"
        "                    infoLabel = 'Llamada de';\n"
        "                } else if (state.callState === 'connected') {\n"
        "                    infoLabel = 'En llamada con';\n"
        "                }\n"
        "                $callInfo.find('.caller-id').text(infoLabel + ': ' + state.activeNumber);\n"
        "                $callInfo.addClass('active').show();\n"
        "            } else {\n"
        "                $callInfo.removeClass('active').hide();\n"
        "                $callInfo.find('.caller-id').text('');\n"
        "            }\n"
        "        }\n"
        "    }"
    )

    if dialpad_target not in js_content_norm:
        print("Error: Dialpad block target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(dialpad_target, dialpad_replace)

    # Set activeNumber in handleIncomingCall
    incoming_target = (
        "    function handleIncomingCall(session) {\n"
        "        log('Incoming call from: ' + session.remoteIdentity.uri.user);"
    )
    incoming_replace = (
        "    function handleIncomingCall(session) {\n"
        "        var caller = session.remoteIdentity.uri.user;\n"
        "        if (session.remoteIdentity.displayName && session.remoteIdentity.displayName !== caller) {\n"
        "            caller = session.remoteIdentity.displayName + ' (' + caller + ')';\n"
        "        }\n"
        "        log('Incoming call from: ' + caller);\n"
        "        state.activeNumber = caller;"
    )

    if incoming_target not in js_content_norm:
        print("Error: handleIncomingCall target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(incoming_target, incoming_replace)

    # Set activeNumber in call(number)
    call_target = (
        "        log('Calling: ' + number);\n"
        "        state.lastCallError = ''; // Clear previous error\n"
        "        state.isVoicemail = false; // Reset voicemail flag\n"
        "        earlyMediaReceived = false; // Reset early media flag for new call"
    )
    call_replace = (
        "        log('Calling: ' + number);\n"
        "        state.lastCallError = ''; // Clear previous error\n"
        "        state.isVoicemail = false; // Reset voicemail flag\n"
        "        earlyMediaReceived = false; // Reset early media flag for new call\n"
        "        state.activeNumber = number; // Set active call number"
    )

    if call_target not in js_content_norm:
        print("Error: call function target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(call_target, call_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: sip-phone.js updated.")

    print("All files updated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
