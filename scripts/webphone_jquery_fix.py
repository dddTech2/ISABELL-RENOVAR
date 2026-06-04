import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    sip_phone_js = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone JQuery and Cache Fix ===")

    # 1. Update sip-phone.js
    if os.path.exists(sip_phone_js):
        with open(sip_phone_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_str = "$.getJSON('index.php?menu=' + menu + '&action=getExtensionsList'"
        replacement_str = "window.jQuery.getJSON('index.php?menu=' + menu + '&action=getExtensionsList'"
        
        if target_str in content:
            content = content.replace(target_str, replacement_str)
            with open(sip_phone_js, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully updated sip-phone.js: replaced $.getJSON with window.jQuery.getJSON")
        else:
            print("Target $.getJSON pattern not found in sip-phone.js or already replaced.")
    else:
        print(f"Error: sip-phone.js not found at {sip_phone_js}")
        return 1

    # 2. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=7", "webphone.css?v=8")
        content = content.replace("sip-phone.js?v=7", "sip-phone.js?v=8")
        
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php cache strings to v=8")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 3. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=7", "webphone.css?v=8")
        content = content.replace("sip-phone.js?v=7", "sip-phone.js?v=8")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=8")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
