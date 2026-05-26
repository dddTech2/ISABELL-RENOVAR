#!/usr/bin/env python3
import os
import re

def update_template(filepath, indent):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if we already inserted the paste handler
    if 'Global paste handler to route pasted number' in content:
        print(f"WebPhone shortcuts already present in {filepath}")
        return True

    # Pattern to search for keypress event on #webphone-number
    # agent_console.tpl has 8 spaces, login_agent.tpl has 4 spaces of indentation
    pattern = r"(\$\('#webphone-number'\)\.on\('keypress',[\s\S]*?\}\);)"
    
    # We want to insert the shortcut scripts after this block
    js_code = f"""

{indent}// Global paste handler to route pasted number to WebPhone input field
{indent}$(document).on('paste', function(e) {{
{indent}    var $numInput = $('#webphone-number');
{indent}    if ($numInput.length === 0 || $numInput.prop('disabled')) {{
{indent}        return;
{indent}    }}

{indent}    // Allow standard paste if focused on another input/textarea
{indent}    var activeEl = document.activeElement;
{indent}    if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'SELECT' || activeEl.isContentEditable)) {{
{indent}        if (activeEl.id !== 'webphone-number') {{
{indent}            return;
{indent}        }}
{indent}    }}

{indent}    var clipboardData = e.originalEvent ? e.originalEvent.clipboardData : e.clipboardData;
{indent}    if (clipboardData) {{
{indent}        var pastedText = clipboardData.getData('text');
{indent}        if (pastedText) {{
{indent}            $numInput.val(pastedText.trim());
{indent}            $numInput.focus();
{indent}            e.preventDefault();
{indent}        }}
{indent}    }}
{indent}}});

{indent}// Global Escape key handler to hangup/cancel calls
{indent}$(document).on('keydown', function(e) {{
{indent}    if (e.key === 'Escape' || e.key === 'Esc' || e.keyCode === 27) {{
{indent}        var phoneState = WebPhone.getState();
{indent}        if (phoneState && phoneState.callState !== 'idle') {{
{indent}            WebPhone.hangup();
{indent}            e.preventDefault();
{indent}        }}
{indent}    }}
{indent}}});"""

    match = re.search(pattern, content)
    if not match:
        print(f"Error: Could not find keypress handler pattern in {filepath}")
        return False
        
    # Replace first occurrence of the match with itself plus our code
    target = match.group(1)
    new_content = content.replace(target, target + js_code, 1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully added WebPhone shortcuts to {filepath}")
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_console_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    login_agent_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'login_agent.tpl')
    
    success = True
    success &= update_template(agent_console_tpl, '        ')
    success &= update_template(login_agent_tpl, '    ')
    
    if success:
        print("All templates updated successfully.")
    else:
        print("Some templates failed to update.")

if __name__ == '__main__':
    main()
