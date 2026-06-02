#!/usr/bin/env python3
import os
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Modify webphone.css
    css_path = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'webphone.css')
    if os.path.exists(css_path):
        print(f"Modifying {css_path}...")
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace .webphone-buttons rule
        # We target the display: grid rule block
        buttons_pattern = r'\.webphone-buttons\s*\{([^}]+)\}'
        match_buttons = re.search(buttons_pattern, content)
        if match_buttons:
            old_body = match_buttons.group(1)
            new_body = """
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 8px;
    grid-column-gap: 8px;
    row-gap: 8px;
    grid-row-gap: 8px;
    width: 100%;
"""
            content = content.replace(match_buttons.group(0), f".webphone-buttons {{{new_body}}}")
            print("Updated .webphone-buttons styles with row-gap and 8px gaps.")
        else:
            print("Warning: Could not find .webphone-buttons block in CSS.")

        # Replace margin: 4px 0 or margin: 0 in .webphone-btn rule
        btn_pattern = r'\.webphone-btn\s*\{([^}]+)\}'
        match_btn = re.search(btn_pattern, content)
        if match_btn:
            btn_body = match_btn.group(1)
            # Replace any margin rule to margin: 0 !important; to avoid overrides
            if 'margin:' in btn_body:
                updated_body = re.sub(r'margin:[^;]+;', 'margin: 0 !important;', btn_body)
                content = content.replace(btn_body, updated_body)
                print("Updated .webphone-btn margin to 0 !important.")
            else:
                # Add margin: 0 !important;
                updated_body = "    margin: 0 !important;\n" + btn_body
                content = content.replace(btn_body, updated_body)
                print("Added margin: 0 !important to .webphone-btn.")
        else:
            print("Warning: Could not find .webphone-btn block in CSS.")

        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"Error: {css_path} not found.")

    # 2. Modify agent_console.tpl to bump version to v=4
    tpl_path = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    if os.path.exists(tpl_path):
        print(f"Modifying {tpl_path}...")
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace v=3 with v=4
        content = content.replace('webphone.css?v=3', 'webphone.css?v=4')
        content = content.replace('sip-phone.js?v=3', 'sip-phone.js?v=4')
        
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated cache busters in agent_console.tpl.")
    else:
        print(f"Error: {tpl_path} not found.")

    # 3. Modify index.php to bump version to v=4
    php_path = os.path.join(base_dir, 'modules', 'agent_console', 'index.php')
    if os.path.exists(php_path):
        print(f"Modifying {php_path}...")
        with open(php_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace v=3 with v=4
        content = content.replace('webphone.css?v=3', 'webphone.css?v=4')
        content = content.replace('sip-phone.js?v=3', 'sip-phone.js?v=4')
        
        with open(php_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated cache busters in index.php.")
    else:
        print(f"Error: {php_path} not found.")

if __name__ == '__main__':
    main()
