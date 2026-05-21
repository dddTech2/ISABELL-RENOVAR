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

    # 1. Modify agent_console.tpl to disable the autoanswer input
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1
    
    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_target = '<input type="checkbox" id="webphone-autoanswer" />'
    tpl_replace = '<input type="checkbox" id="webphone-autoanswer" disabled="disabled" />'

    if tpl_target not in tpl_content_norm:
        print("Error: Target autoanswer input not found in agent_console.tpl")
        return 1

    tpl_content_norm = tpl_content_norm.replace(tpl_target, tpl_replace)

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: Disabled autoanswer checkbox in agent_console.tpl")

    # 2. Modify webphone.css to prevent pointer events and show not-allowed cursor
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_rules = (
        "\n"
        "/* Locked auto-answer toggle styles */\n"
        ".webphone-toggle input:disabled + .webphone-toggle-slider {\n"
        "    cursor: not-allowed;\n"
        "    opacity: 0.8;\n"
        "}\n"
        "\n"
        ".webphone-toggle-slider {\n"
        "    pointer-events: none; /* Disables click interactions on the toggle label */\n"
        "}\n"
    )

    css_content_norm += css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: Added disabled toggle CSS in webphone.css")

    # 3. Modify sip-phone.js to set delay to 1000ms and force auto-answer
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    js_delay_target = "        autoAnswerDelay: 500 // milliseconds before auto-answering"
    js_delay_replace = "        autoAnswerDelay: 1000 // milliseconds before auto-answering"

    if js_delay_target not in js_content_norm:
        print("Error: autoAnswerDelay target not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(js_delay_target, js_delay_replace)

    js_pref_target = (
        "    function loadAutoAnswerPreference() {\n"
        "        try {\n"
        "            var saved = localStorage.getItem('webphone_autoanswer');\n"
        "            if (saved === '1') {\n"
        "                setAutoAnswer(true);\n"
        "                $('#webphone-autoanswer').prop('checked', true);\n"
        "            }\n"
        "        } catch (e) {}\n"
        "    }"
    )
    js_pref_replace = (
        "    function loadAutoAnswerPreference() {\n"
        "        // Force auto-answer to true on login/initial load\n"
        "        setAutoAnswer(true);\n"
        "        $('#webphone-autoanswer').prop('checked', true);\n"
        "    }"
    )

    if js_pref_target not in js_content_norm:
        print("Error: loadAutoAnswerPreference function not found in sip-phone.js")
        return 1

    js_content_norm = js_content_norm.replace(js_pref_target, js_pref_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Forced auto-answer and updated delay in sip-phone.js")

    print("All auto-answer configurations applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
