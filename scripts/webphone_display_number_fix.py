import os
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    login_agent_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "login_agent.tpl")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Modifying template files:\n - {agent_console_tpl}\n - {login_agent_tpl}")
    print(f"Modifying JS file: {js_file}")

    # 1. Fix agent_console.tpl duplicates and add timer div
    with open(agent_console_tpl, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicates
    duplicate_pattern = r'(<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\s*<div class="caller-id"></div>\s*</div>\s*){2,}'
    single_block = '<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n                        <div class="caller-id"></div>\n                        <div class="call-timer" style="font-size: 1.1em; font-weight: bold; margin-top: 5px; display: none;">00:00</div>\n                    </div>\n'
    
    if re.search(duplicate_pattern, content):
        content = re.sub(duplicate_pattern, single_block, content)
        print("Fixed duplicates in agent_console.tpl")
    else:
        # If not duplicated but just old block, replace it
        old_block = '<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n                        <div class="caller-id"></div>\n                    </div>'
        if old_block in content and '<div class="call-timer"' not in content:
            content = content.replace(old_block, single_block.strip())
            print("Updated block in agent_console.tpl")

    with open(agent_console_tpl, 'w', encoding='utf-8') as f:
        f.write(content)

    # 2. Fix login_agent.tpl
    with open(login_agent_tpl, 'r', encoding='utf-8') as f:
        content = f.read()
    
    duplicate_pattern_login = r'(<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\s*<div class="caller-id"></div>\s*</div>\s*){2,}'
    single_block_login = '<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n            <div class="caller-id"></div>\n            <div class="call-timer" style="font-size: 1.1em; font-weight: bold; margin-top: 5px; display: none;">00:00</div>\n        </div>\n'
    
    if re.search(duplicate_pattern_login, content):
        content = re.sub(duplicate_pattern_login, single_block_login, content)
        print("Fixed duplicates in login_agent.tpl")
    else:
        old_block_login = '<div id="webphone-call-info" class="webphone-call-info" style="display: none;">\n            <div class="caller-id"></div>\n        </div>'
        if old_block_login in content and '<div class="call-timer"' not in content:
            content = content.replace(old_block_login, single_block_login.strip())
            print("Updated block in login_agent.tpl")

    with open(login_agent_tpl, 'w', encoding='utf-8') as f:
        f.write(content)

    # 3. Update sip-phone.js
    with open(js_file, 'r', encoding='utf-8') as f:
        js = f.read()

    js = js.replace('\r\n', '\n')

    # a. add timerInterval var
    if 'var callTimerInterval = null;' not in js:
        js = js.replace('var ringtoneGain = null;', 'var ringtoneGain = null;\n    var callTimerInterval = null;')

    # b. add state variables
    state_target = (
        "        muted: false, // Track mute state\n"
        "        activeNumber: '' // Active call number/identifier\n"
        "    };"
    )
    state_replace = (
        "        muted: false, // Track mute state\n"
        "        activeNumber: '', // Active call number/identifier\n"
        "        callStartTime: null\n"
        "    };"
    )
    if state_target in js:
        js = js.replace(state_target, state_replace)
        print("Updated state in sip-phone.js")

    # c. update updateCallState
    update_state_target = (
        "    function updateCallState(newState) {\n"
        "        state.callState = newState;\n"
        "        if (callbacks.onCallStateChange) {\n"
        "            callbacks.onCallStateChange(newState);\n"
        "        }\n"
        "        updateUI();\n"
        "    }"
    )
    update_state_replace = (
        "    function updateCallState(newState) {\n"
        "        state.callState = newState;\n"
        "        if (newState === 'connected') {\n"
        "            state.callStartTime = new Date().getTime();\n"
        "        }\n"
        "        if (callbacks.onCallStateChange) {\n"
        "            callbacks.onCallStateChange(newState);\n"
        "        }\n"
        "        updateUI();\n"
        "    }"
    )
    if update_state_target in js:
        js = js.replace(update_state_target, update_state_replace)
        print("Updated updateCallState in sip-phone.js")

    # d. ui update
    ui_target = (
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
        "        }"
    )
    ui_replace = (
        "        // Show/hide call info panel based on active number\n"
        "        if ($callInfo.length) {\n"
        "            var $callTimer = $callInfo.find('.call-timer');\n"
        "            if (state.callState !== 'idle' && state.activeNumber) {\n"
        "                var infoLabel = 'Llamada';\n"
        "                if (state.callState === 'calling') {\n"
        "                    infoLabel = 'Llamando a';\n"
        "                    $callTimer.hide();\n"
        "                } else if (state.callState === 'ringing') {\n"
        "                    infoLabel = 'Llamada de';\n"
        "                    $callTimer.hide();\n"
        "                } else if (state.callState === 'connected') {\n"
        "                    infoLabel = 'En llamada con';\n"
        "                    $callTimer.show();\n"
        "                    if (!callTimerInterval) {\n"
        "                        callTimerInterval = setInterval(function() {\n"
        "                            if (state.callState !== 'connected') return;\n"
        "                            var now = new Date().getTime();\n"
        "                            var diff = Math.floor((now - state.callStartTime) / 1000);\n"
        "                            var m = Math.floor(diff / 60);\n"
        "                            var s = diff % 60;\n"
        "                            m = m < 10 ? '0' + m : m;\n"
        "                            s = s < 10 ? '0' + s : s;\n"
        "                            $callTimer.text(m + ':' + s);\n"
        "                        }, 1000);\n"
        "                    }\n"
        "                }\n"
        "                $callInfo.find('.caller-id').text(infoLabel + ': ' + state.activeNumber);\n"
        "                $callInfo.addClass('active').show();\n"
        "            } else {\n"
        "                $callInfo.removeClass('active').hide();\n"
        "                $callInfo.find('.caller-id').text('');\n"
        "                $callTimer.hide().text('00:00');\n"
        "                if (callTimerInterval) {\n"
        "                    clearInterval(callTimerInterval);\n"
        "                    callTimerInterval = null;\n"
        "                }\n"
        "            }\n"
        "        }"
    )
    if ui_target in js:
        js = js.replace(ui_target, ui_replace)
        print("Updated UI logic in sip-phone.js")
    else:
        print("Warning: ui_target not found in sip-phone.js")

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js)

if __name__ == "__main__":
    main()
