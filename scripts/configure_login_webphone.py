import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    login_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "login_agent.tpl")
    console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    css_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Modifying login template: {login_tpl}")
    print(f"Modifying console template: {console_tpl}")
    print(f"Modifying CSS file: {css_file}")
    print(f"Modifying JS file: {js_file}")

    # 1. Modify login_agent.tpl (add mute button HTML and JS click binding)
    if not os.path.exists(login_tpl):
        print(f"Error: {login_tpl} not found")
        return 1
    
    with open(login_tpl, 'r', encoding='utf-8') as f:
        login_content = f.read()

    login_content_norm = login_content.replace('\r\n', '\n')

    # Add HTML button
    html_target = '            <button id="webphone-btn-hangup" class="webphone-btn webphone-btn-hangup" style="display:none;">Colgar</button>'
    html_insert = '            <button id="webphone-btn-mute" class="webphone-btn webphone-btn-mute" style="display:none;">Silenciar</button>'
    
    if html_target not in login_content_norm:
        print("Error: hangup button target not found in login_agent.tpl")
        return 1
    
    if html_insert not in login_content_norm:
        login_content_norm = login_content_norm.replace(html_target, f"{html_target}\n{html_insert}")
        print("Mute button HTML added to login_agent.tpl")

    # Add click event binding
    js_bind_target = (
        "    $('#webphone-btn-hangup').on('click', function() {\n"
        "        WebPhone.hangup();\n"
        "    });"
    )
    js_bind_insert = (
        "    $('#webphone-btn-mute').on('click', function() {\n"
        "        WebPhone.toggleMute();\n"
        "    });"
    )

    if js_bind_target not in login_content_norm:
        print("Error: hangup click binding target not found in login_agent.tpl")
        return 1

    if js_bind_insert not in login_content_norm:
        login_content_norm = login_content_norm.replace(js_bind_target, f"{js_bind_target}\n\n{js_bind_insert}")
        print("Mute button click listener added to login_agent.tpl")

    if '\r\n' in login_content:
        login_content_norm = login_content_norm.replace('\n', '\r\n')

    with open(login_tpl, 'w', encoding='utf-8') as f:
        f.write(login_content_norm)

    # 2. Modify agent_console.tpl (force auto-answer to true post-login)
    if not os.path.exists(console_tpl):
        print(f"Error: {console_tpl} not found")
        return 1

    with open(console_tpl, 'r', encoding='utf-8') as f:
        console_content = f.read()

    console_content_norm = console_content.replace('\r\n', '\n')

    console_pref_target = (
        "        // Load saved auto-answer preference\n"
        "        WebPhone.loadAutoAnswerPreference();"
    )
    console_pref_replace = (
        "        // Load saved auto-answer preference\n"
        "        WebPhone.loadAutoAnswerPreference();\n\n"
        "        // Force auto-answer to true for logged in agent console\n"
        "        WebPhone.setAutoAnswer(true);\n"
        "        $('#webphone-autoanswer').prop('checked', true);"
    )

    if console_pref_target not in console_content_norm:
        print("Error: loadAutoAnswerPreference target not found in agent_console.tpl")
        return 1

    if "Force auto-answer to true for logged in agent console" not in console_content_norm:
        console_content_norm = console_content_norm.replace(console_pref_target, console_pref_replace)
        print("Forced auto-answer enabled post-login in agent_console.tpl")

    if '\r\n' in console_content:
        console_content_norm = console_content_norm.replace('\n', '\r\n')

    with open(console_tpl, 'w', encoding='utf-8') as f:
        f.write(console_content_norm)

    # 3. Modify sip-phone.js (restore loadAutoAnswerPreference loading logic)
    if not os.path.exists(js_file):
        print(f"Error: {js_file} not found")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    js_pref_target = (
        "    function loadAutoAnswerPreference() {\n"
        "        // Force auto-answer to true on login/initial load\n"
        "        setAutoAnswer(true);\n"
        "        $('#webphone-autoanswer').prop('checked', true);\n"
        "    }"
    )

    js_pref_replace = (
        "    function loadAutoAnswerPreference() {\n"
        "        try {\n"
        "            var saved = localStorage.getItem('webphone_autoanswer');\n"
        "            if (saved === '1') {\n"
        "                setAutoAnswer(true);\n"
        "                $('#webphone-autoanswer').prop('checked', true);\n"
        "            } else {\n"
        "                setAutoAnswer(false);\n"
        "                $('#webphone-autoanswer').prop('checked', false);\n"
        "            }\n"
        "        } catch (e) {\n"
        "            setAutoAnswer(false);\n"
        "            $('#webphone-autoanswer').prop('checked', false);\n"
        "        }\n"
    )

    # Note: wait, let's match the closing brace of loadAutoAnswerPreference
    # Let's inspect js_pref_target exactly to be sure we match properly.
    if js_pref_target not in js_content_norm:
        print("Error: loadAutoAnswerPreference target function not found in sip-phone.js")
        return 1

    # Replace the target
    js_content_norm = js_content_norm.replace(
        js_pref_target,
        "    function loadAutoAnswerPreference() {\n"
        "        try {\n"
        "            var saved = localStorage.getItem('webphone_autoanswer');\n"
        "            if (saved === '1') {\n"
        "                setAutoAnswer(true);\n"
        "                $('#webphone-autoanswer').prop('checked', true);\n"
        "            } else {\n"
        "                setAutoAnswer(false);\n"
        "                $('#webphone-autoanswer').prop('checked', false);\n"
        "            }\n"
        "        } catch (e) {\n"
        "            setAutoAnswer(false);\n"
        "            $('#webphone-autoanswer').prop('checked', false);\n"
        "        }\n"
        "    }"
    )
    print("Restored preference loading logic in sip-phone.js")

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)

    # 4. Modify webphone.css (restrict pointer-events to disabled toggle slider only)
    if not os.path.exists(css_file):
        print(f"Error: {css_file} not found")
        return 1

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_old_rules = (
        "/* Locked auto-answer toggle styles */\n"
        ".webphone-toggle input:disabled + .webphone-toggle-slider {\n"
        "    cursor: not-allowed;\n"
        "    opacity: 0.8;\n"
        "}\n"
        "\n"
        ".webphone-toggle-slider {\n"
        "    pointer-events: none; /* Disables click interactions on the toggle label */\n"
        "}"
    )

    css_new_rules = (
        "/* Locked auto-answer toggle styles */\n"
        ".webphone-toggle input:disabled + .webphone-toggle-slider {\n"
        "    cursor: not-allowed;\n"
        "    opacity: 0.8;\n"
        "    pointer-events: none; /* Disables click interactions on the toggle slider when disabled */\n"
        "}"
    )

    if css_old_rules not in css_content_norm:
        # Fallback to search-and-replace of the global pointer-events block
        global_target = (
            ".webphone-toggle-slider {\n"
            "    pointer-events: none; /* Disables click interactions on the toggle label */\n"
            "}"
        )
        if global_target in css_content_norm:
            css_content_norm = css_content_norm.replace(global_target, "")
            print("Removed global pointer-events block from webphone.css")
        
        # Now add pointer-events to input:disabled rule
        disabled_target = (
            ".webphone-toggle input:disabled + .webphone-toggle-slider {\n"
            "    cursor: not-allowed;\n"
            "    opacity: 0.8;\n"
            "}"
        )
        disabled_replace = (
            ".webphone-toggle input:disabled + .webphone-toggle-slider {\n"
            "    cursor: not-allowed;\n"
            "    opacity: 0.8;\n"
            "    pointer-events: none;\n"
            "}"
        )
        if disabled_target in css_content_norm:
            css_content_norm = css_content_norm.replace(disabled_target, disabled_replace)
            print("Updated input:disabled rule in webphone.css")
    else:
        css_content_norm = css_content_norm.replace(css_old_rules, css_new_rules)
        print("Updated toggle CSS rules in webphone.css")

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)

    print("All configurations updated successfully!")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
