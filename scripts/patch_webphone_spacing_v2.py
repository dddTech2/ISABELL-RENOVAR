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
        
        # Add gap and grid-gap to .webphone-buttons
        if 'grid-gap: 8px;' not in content:
            content = content.replace('column-gap: 8px;', 'gap: 8px;\n    grid-gap: 8px;\n    column-gap: 8px;')
            print("Added grid-gap to .webphone-buttons for legacy support.")

        # Remove width: 100%; from .webphone-btn to avoid overflow
        btn_pattern = r'(\.webphone-btn\s*\{[^}]*)width:\s*100%;([^}]*\})'
        if re.search(btn_pattern, content):
            content = re.sub(btn_pattern, r'\1\2', content)
            print("Removed width: 100%; from .webphone-btn.")

        # Change #webphone-btn-call to span 1 (remove from span 2 rule)
        call_reconnect_pattern = r'#webphone-btn-call,\s*#webphone-btn-reconnect\s*\{\s*grid-column:\s*span\s*2;\s*\}'
        if re.search(call_reconnect_pattern, content):
            content = re.sub(call_reconnect_pattern, r'#webphone-btn-reconnect {\n    grid-column: span 2;\n}', content)
            print("Removed #webphone-btn-call from span 2 rule.")

        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"Error: {css_path} not found.")

    # 2. Modify agent_console.tpl to bump version to v=5
    tpl_path = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    if os.path.exists(tpl_path):
        print(f"Modifying {tpl_path}...")
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace v=4 with v=5
        content = content.replace('webphone.css?v=4', 'webphone.css?v=5')
        content = content.replace('sip-phone.js?v=4', 'sip-phone.js?v=5')
        
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated cache busters in agent_console.tpl to v=5.")

    # 3. Modify index.php to bump version to v=5
    php_path = os.path.join(base_dir, 'modules', 'agent_console', 'index.php')
    if os.path.exists(php_path):
        print(f"Modifying {php_path}...")
        with open(php_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace v=4 with v=5
        content = content.replace('webphone.css?v=4', 'webphone.css?v=5')
        content = content.replace('sip-phone.js?v=4', 'sip-phone.js?v=5')
        
        with open(php_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated cache busters in index.php to v=5.")

if __name__ == '__main__':
    main()
