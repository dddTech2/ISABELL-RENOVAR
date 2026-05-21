import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    tpl_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    css_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Modifying template file: {tpl_file}")
    print(f"Modifying CSS file: {css_file}")
    print(f"Modifying JS file: {js_file}")

    # 1. Modify agent_console.tpl
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1
    
    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    # Normalize line endings
    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    # Add HTML button
    tpl_btn_target = (
        '                        <button id="webphone-btn-hangup" class="webphone-btn webphone-btn-hangup" style="display:none;">Colgar</button>'
    )
    tpl_btn_replace = (
        '                        <button id="webphone-btn-hangup" class="webphone-btn webphone-btn-hangup" style="display:none;">Colgar</button>\n'
        '                        <button id="webphone-btn-mute" class="webphone-btn webphone-btn-mute" style="display:none;">Silenciar</button>'
    )

    if tpl_btn_target not in tpl_content_norm:
        print("Error: Target hangup button block not found in agent_console.tpl")
        return 1
    
    tpl_content_norm = tpl_content_norm.replace(tpl_btn_target, tpl_btn_replace)

    # Bind click event
    tpl_click_target = (
        "        $('#webphone-btn-hangup').on('click', function() {\n"
        "            WebPhone.hangup();\n"
        "        });"
    )
    tpl_click_replace = (
        "        $('#webphone-btn-hangup').on('click', function() {\n"
        "            WebPhone.hangup();\n"
        "        });\n"
        "\n"
        "        $('#webphone-btn-mute').on('click', function() {\n"
        "            WebPhone.toggleMute();\n"
        "        });"
    )

    if tpl_click_target not in tpl_content_norm:
        print("Error: Click event binding target not found in agent_console.tpl")
        return 1
    
    tpl_content_norm = tpl_content_norm.replace(tpl_click_target, tpl_click_replace)

    # Restore line endings and write back
    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')
    
    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: agent_console.tpl updated.")

    # 2. Modify webphone.css
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')
    
    mute_css_rules = (
        "\n"
        "/* ============================================ \n"
        "   MUTE BUTTON STYLES\n"
        "   ============================================ */\n"
        ".webphone-btn-mute {\n"
        "    background: #6c757d;\n"
        "    color: white;\n"
        "}\n"
        "\n"
        ".webphone-btn-mute:hover:not(:disabled) {\n"
        "    background: #5a6268;\n"
        "}\n"
        "\n"
        ".webphone-btn-mute.muted {\n"
        "    background: #ffc107;\n"
        "    color: #212529;\n"
        "}\n"
        "\n"
        ".webphone-btn-mute.muted:hover:not(:disabled) {\n"
        "    background: #e0a800;\n"
        "}\n"
    )

    # Append to CSS content
    css_content_norm += mute_css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: webphone.css updated.")

    # 3. Modify sip-phone.js
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Add state.muted
    js_state_target = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "        isVoicemail: false // Track if call was answered by a voicemail system\n"
        "    };"
    )
    js_state_replace = (
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

    if js_state_target not in js_content_norm:
        print("Error: State definition target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(js_state_target, js_state_replace)

    # Add $muteBtn cache in updateUI()
    js_ui_cache_target = (
        "    function updateUI() {\n"
        "        var $status = $('#webphone-status');\n"
        "        var $callBtn = $('#webphone-btn-call');\n"
        "        var $hangupBtn = $('#webphone-btn-hangup');\n"
        "        var $answerBtn = $('#webphone-btn-answer');\n"
        "        var $reconnectBtn = $('#webphone-btn-reconnect');\n"
        "        var $statusText = $status.find('.status-text');"
    )
    js_ui_cache_replace = (
        "    function updateUI() {\n"
        "        var $status = $('#webphone-status');\n"
        "        var $callBtn = $('#webphone-btn-call');\n"
        "        var $hangupBtn = $('#webphone-btn-hangup');\n"
        "        var $answerBtn = $('#webphone-btn-answer');\n"
        "        var $reconnectBtn = $('#webphone-btn-reconnect');\n"
        "        var $muteBtn = $('#webphone-btn-mute');\n"
        "        var $statusText = $status.find('.status-text');"
    )

    if js_ui_cache_target not in js_content_norm:
        print("Error: updateUI variables cache target not found in sip-phone.js")
        return 1
    
    js_content_norm = js_content_norm.replace(js_ui_cache_target, js_ui_cache_replace)

    # Update state.callState switch cases in updateUI()
    js_switch_target = (
        "        switch(state.callState) {\n"
        "            case 'idle':\n"
        "                $callBtn.show().prop('disabled', !state.registered);\n"
        "                $hangupBtn.hide();\n"
        "                $answerBtn.hide();\n"
        "                $('#webphone-number').prop('disabled', false);\n"
        "                stopRingtoneSound();\n"
        "                break;\n"
        "            case 'calling':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-calling');\n"
        "                $statusText.text('LLAMANDO...');\n"
        "                playRingtoneSound('outgoing');\n"
        "                break;\n"
        "            case 'ringing':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.show().prop('disabled', false);\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-ringing-incoming');\n"
        "                $statusText.text('LLAMADA ENTRANTE!');\n"
        "                playRingtoneSound('incoming');\n"
        "                break;\n"
        "            case 'connected':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-connected');\n"
        "                if (state.isVoicemail) {\n"
        "                    $statusText.text('BUZÓN DE VOZ');\n"
        "                } else {\n"
        "                    $statusText.text('EN LLAMADA');\n"
        "                }\n"
        "                stopRingtoneSound();\n"
        "                break;\n"
        "        }"
    )
    js_switch_replace = (
        "        switch(state.callState) {\n"
        "            case 'idle':\n"
        "                $callBtn.show().prop('disabled', !state.registered);\n"
        "                $hangupBtn.hide();\n"
        "                $answerBtn.hide();\n"
        "                $muteBtn.hide();\n"
        "                setMute(false); // Reset mute state when idle\n"
        "                $('#webphone-number').prop('disabled', false);\n"
        "                stopRingtoneSound();\n"
        "                break;\n"
        "            case 'calling':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $muteBtn.hide();\n"
        "                setMute(false); // Reset mute state when dialing\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-calling');\n"
        "                $statusText.text('LLAMANDO...');\n"
        "                playRingtoneSound('outgoing');\n"
        "                break;\n"
        "            case 'ringing':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.show().prop('disabled', false);\n"
        "                $muteBtn.hide();\n"
        "                setMute(false); // Reset mute state when ringing\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-ringing-incoming');\n"
        "                $statusText.text('LLAMADA ENTRANTE!');\n"
        "                playRingtoneSound('incoming');\n"
        "                break;\n"
        "            case 'connected':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $muteBtn.show().prop('disabled', false);\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-connected');\n"
        "                if (state.isVoicemail) {\n"
        "                    $statusText.text('BUZÓN DE VOZ');\n"
        "                } else {\n"
        "                    $statusText.text('EN LLAMADA');\n"
        "                }\n"
        "                stopRingtoneSound();\n"
        "                break;\n"
        "        }"
    )

    if js_switch_target not in js_content_norm:
        print("Error: State switch target not found in sip-phone.js")
        return 1
    
    js_content_norm = js_content_norm.replace(js_switch_target, js_switch_replace)

    # Insert setMute and toggleMute functions and add them to return API
    js_api_target = (
        "    function reconnect() {\n"
        "        log('Reconnecting...');\n"
        "        stopRingtoneSound();\n"
        "        registerAttempts = 0;\n"
        "        state.authFailed = false;\n"
        "        state.registered = false;\n"
        "        updateUI();\n"
        "        \n"
        "        if (userAgent) {\n"
        "            userAgent.stop().then(function() {\n"
        "                createUserAgent();\n"
        "            }).catch(function() {\n"
        "                createUserAgent();\n"
        "            });\n"
        "        } else {\n"
        "            createUserAgent();\n"
        "        }\n"
        "    }\n"
        "\n"
        "    // Public API\n"
        "    return {\n"
        "        init: init,\n"
        "        call: call,\n"
        "        answer: answer,\n"
        "        hangup: hangup,\n"
        "        disconnect: disconnect,\n"
        "        reconnect: reconnect,\n"
        "        setAutoAnswer: setAutoAnswer,\n"
        "        loadAutoAnswerPreference: loadAutoAnswerPreference,\n"
        "        isRegistered: function() { return state.registered; },\n"
        "        getState: function() { return state; },\n"
        "        isAutoAnswer: function() { return state.autoAnswer; }\n"
        "    };"
    )

    js_api_replace = (
        "    function reconnect() {\n"
        "        log('Reconnecting...');\n"
        "        stopRingtoneSound();\n"
        "        registerAttempts = 0;\n"
        "        state.authFailed = false;\n"
        "        state.registered = false;\n"
        "        updateUI();\n"
        "        \n"
        "        if (userAgent) {\n"
        "            userAgent.stop().then(function() {\n"
        "                createUserAgent();\n"
        "            }).catch(function() {\n"
        "                createUserAgent();\n"
        "            });\n"
        "        } else {\n"
        "            createUserAgent();\n"
        "        }\n"
        "    }\n"
        "\n"
        "    function toggleMute() {\n"
        "        setMute(!state.muted);\n"
        "    }\n"
        "\n"
        "    function setMute(muteVal) {\n"
        "        state.muted = muteVal;\n"
        "        \n"
        "        var $muteBtn = $('#webphone-btn-mute');\n"
        "        if (muteVal) {\n"
        "            $muteBtn.addClass('muted').text('Silenciado');\n"
        "        } else {\n"
        "            $muteBtn.removeClass('muted').text('Silenciar');\n"
        "        }\n"
        "\n"
        "        if (!currentSession) {\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        var sdh = currentSession.sessionDescriptionHandler;\n"
        "        if (!sdh) {\n"
        "            log('No sessionDescriptionHandler to set mute');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        var pc = sdh.peerConnection;\n"
        "        if (!pc) {\n"
        "            log('No peerConnection to set mute');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        if (typeof pc.getSenders === 'function') {\n"
        "            pc.getSenders().forEach(function(sender) {\n"
        "                if (sender.track && sender.track.kind === 'audio') {\n"
        "                    sender.track.enabled = !muteVal;\n"
        "                }\n"
        "            });\n"
        "            log('Call audio tracks ' + (muteVal ? 'disabled (muted)' : 'enabled (unmuted)'));\n"
        "        } else {\n"
        "            log('getSenders is not supported on peerConnection');\n"
        "        }\n"
        "    }\n"
        "\n"
        "    // Public API\n"
        "    return {\n"
        "        init: init,\n"
        "        call: call,\n"
        "        answer: answer,\n"
        "        hangup: hangup,\n"
        "        disconnect: disconnect,\n"
        "        reconnect: reconnect,\n"
        "        setAutoAnswer: setAutoAnswer,\n"
        "        loadAutoAnswerPreference: loadAutoAnswerPreference,\n"
        "        toggleMute: toggleMute,\n"
        "        setMute: setMute,\n"
        "        isRegistered: function() { return state.registered; },\n"
        "        getState: function() { return state; },\n"
        "        isAutoAnswer: function() { return state.autoAnswer; }\n"
        "    };"
    )

    if js_api_target not in js_content_norm:
        print("Error: API target not found in sip-phone.js")
        return 1
    
    js_content_norm = js_content_norm.replace(js_api_target, js_api_replace)

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
