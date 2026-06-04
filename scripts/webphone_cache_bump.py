import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("Bumping assets cache version to force-reload...")

    # 1. Update index.php
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace("webphone.css?v=6", "webphone.css?v=7")
        content = content.replace("sip-phone.js?v=6", "sip-phone.js?v=7")
        with open(index_php, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.php to v=7")

    # 2. Update agent_console.tpl
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace("webphone.css?v=6", "webphone.css?v=7")
        content = content.replace("sip-phone.js?v=6", "sip-phone.js?v=7")
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl to v=7")

    print("Cache bump complete.")
    return 0

if __name__ == "__main__":
    main()
