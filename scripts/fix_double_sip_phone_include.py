import os
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    agent_console_tpl = os.path.join(
        workspace_dir, 
        "modules", 
        "agent_console", 
        "themes", 
        "default", 
        "agent_console.tpl"
    )

    if not os.path.exists(agent_console_tpl):
        print(f"Error: Template file not found at {agent_console_tpl}")
        return 1

    print(f"Reading {agent_console_tpl}...")
    with open(agent_console_tpl, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex pattern to match the redundant webphone includes
    # Matches:
    # {* WebPhone includes *}
    # <link rel="stylesheet" href="modules/agent_console/themes/default/js/webphone/webphone.css?v=..." />
    # <script type="text/javascript" src="modules/agent_console/themes/default/js/webphone/sip-0.20.0.min.js"></script>
    # <script type="text/javascript" src="modules/agent_console/themes/default/js/webphone/sip-phone.js?v=..."></script>
    pattern = (
        r'\{\*\s*WebPhone\s+includes\s*\*\}\s*\n'
        r'<link\s+rel="stylesheet"\s+href="modules/agent_console/themes/default/js/webphone/webphone\.css(?:\?v=\d+)?"\s*/>\s*\n'
        r'<script\s+type="text/javascript"\s+src="modules/agent_console/themes/default/js/webphone/sip-0\.20\.0\.min\.js"></script>\s*\n'
        r'<script\s+type="text/javascript"\s+src="modules/agent_console/themes/default/js/webphone/sip-phone\.js(?:\?v=\d+)?"></script>\s*\n?'
    )

    if re.search(pattern, content):
        new_content = re.sub(pattern, '', content)
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Success: Redundant WebPhone includes removed from agent_console.tpl")
    else:
        # Check if they are already removed
        if 'sip-phone.js' in content and 'sip-0.20.0.min.js' in content:
            print("Warning: WebPhone includes found but they did not match the exact pattern. Doing a strict string replace instead.")
            # Let's try to remove lines 33-36 if they are exact
            lines = content.splitlines(keepends=True)
            if len(lines) > 36 and "sip-phone.js" in lines[35] and "sip-0.20.0.min.js" in lines[34]:
                del lines[32:36]  # Lines 33, 34, 35, 36 (0-indexed: 32, 33, 34, 35)
                with open(agent_console_tpl, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print("Success: Removed lines 33-36 from agent_console.tpl")
            else:
                print("Error: Could not locate includes to remove.")
                return 1
        else:
            print("Success: Redundant WebPhone includes already removed (idempotent check passed).")

    return 0

if __name__ == "__main__":
    exit(main())
