import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Modifying JS file: {js_file}")

    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    target_code = (
        "                    if (session === currentSession) {\n"
        "                        currentSession = null;\n"
        "                        \n"
        "                        // Auto-resume held session if it exists when active call is hung up\n"
        "                        if (heldSession) {\n"
        "                            log('Active call terminated. Auto-resuming held session.');\n"
        "                            resume();\n"
        "                        } else {\n"
        "                            updateCallState('idle');\n"
        "                        }\n"
        "                    }"
    )

    replace_code = (
        "                    if (session === currentSession) {\n"
        "                        currentSession = null;\n"
        "                        \n"
        "                        // Auto-resume disabled: keep held session, update call state to idle\n"
        "                        if (heldSession) {\n"
        "                            log('Active call terminated. Keeping held session.');\n"
        "                        }\n"
        "                        updateCallState('idle');\n"
        "                    }"
    )

    if target_code not in content_norm:
        print("Error: Target code block not found in sip-phone.js")
        return 1

    content_norm = content_norm.replace(target_code, replace_code)

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("Success: sip-phone.js updated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
