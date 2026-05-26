#!/usr/bin/env python3
import os
import re

def update_css(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '.webphone-pip-icon-btn' in content:
        print(f"CSS styling already present in {filepath}")
        return True
        
    css_rules = """

/* Picture-in-Picture float button */
.webphone-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.webphone-pip-icon-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
    color: #666;
    transition: color 0.2s;
    line-height: 1;
}
.webphone-pip-icon-btn:hover {
    color: #5cb85c;
}
"""
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(css_rules)
        
    print(f"Successfully appended CSS to {filepath}")
    return True

def update_template(filepath, indent):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update HTML header to include button
    header_pattern = r'<div class="webphone-header">WebPhone</div>'
    new_header = (
        '<div class="webphone-header">\n'
        f'{indent}        <span>WebPhone</span>\n'
        f'{indent}        <button type="button" id="webphone-btn-pip" class="webphone-pip-icon-btn" title="Flotar WebPhone (Picture-in-Picture)" style="display: none;">⧉</button>\n'
        f'{indent}    </div>'
    )
    
    if 'id="webphone-btn-pip"' not in content:
        content = content.replace(header_pattern, new_header, 1)
        print(f"Updated HTML header in {filepath}")
    else:
        print(f"HTML header already updated in {filepath}")

    # 2. Update JavaScript to implement PiP logic
    if 'documentPictureInPicture' in content:
        print(f"PiP JS logic already present in {filepath}")
        # Write back in case header was updated
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    # Search for the Escape key keydown block to append after it
    escape_pattern = r"""(\$\(document\)\.on\('keydown', function\(e\) \{[\s\S]*?e\.key === 'Escape'[\s\S]*?\}\);)"""
    
    match = re.search(escape_pattern, content)
    if not match:
        print(f"Error: Could not find Escape key keydown pattern in {filepath}")
        return False
        
    target_block = match.group(1)
    
    pip_js = f"""

{indent}// Check if Document Picture-in-Picture is supported
{indent}if ('documentPictureInPicture' in window) {{
{indent}    $('#webphone-btn-pip').show();
{indent}}}

{indent}$('#webphone-btn-pip').on('click', async function() {{
{indent}    if (!('documentPictureInPicture' in window)) {{
{indent}        return;
{indent}    }}

{indent}    if (window.pipWindow) {{
{indent}        window.pipWindow.focus();
{indent}        return;
{indent}    }}

{indent}    try {{
{indent}        const pipWindow = await window.documentPictureInPicture.requestWindow({{
{indent}            width: 280,
{indent}            height: 380
{indent}        }});
{indent}        window.pipWindow = pipWindow;

{indent}        const $webphone = $('.webphone-panel');
{indent}        const $originalParent = $webphone.parent();

{indent}        pipWindow.document.body.append($webphone[0]);
{indent}        pipWindow.document.body.style.margin = '0';
{indent}        pipWindow.document.body.style.padding = '0';
{indent}        pipWindow.document.body.style.overflow = 'hidden';
{indent}        pipWindow.document.body.style.backgroundColor = '#f5f5f5';

{indent}        // Copy styles
{indent}        [...document.styleSheets].forEach((styleSheet) => {{
{indent}            try {{
{indent}                const cssRules = [...styleSheet.cssRules].map((rule) => rule.cssText).join('');
{indent}                const style = document.createElement('style');
{indent}                style.textContent = cssRules;
{indent}                pipWindow.document.head.appendChild(style);
{indent}            }} catch (e) {{
{indent}                const link = document.createElement('link');
{indent}                link.rel = 'stylesheet';
{indent}                link.type = styleSheet.type || 'text/css';
{indent}                link.media = styleSheet.media.mediaText;
{indent}                link.href = styleSheet.href;
{indent}                pipWindow.document.head.appendChild(link);
{indent}            }}
{indent}        }});

{indent}        // Hide PiP button inside PiP window
{indent}        $(pipWindow.document.body).find('#webphone-btn-pip').hide();

{indent}        // Bind shortcuts inside the PiP document
{indent}        $(pipWindow.document).on('keydown', function(e) {{
{indent}            if (e.key === 'Escape' || e.key === 'Esc' || e.keyCode === 27) {{
{indent}                var phoneState = WebPhone.getState();
{indent}                if (phoneState && phoneState.callState !== 'idle') {{
{indent}                    WebPhone.hangup();
{indent}                    e.preventDefault();
{indent}                }}
{indent}            }}
{indent}        }});

{indent}        $(pipWindow.document).on('paste', function(e) {{
{indent}            var $numInput = $(pipWindow.document).find('#webphone-number');
{indent}            if ($numInput.length === 0 || $numInput.prop('disabled')) {{
{indent}                return;
{indent}            }}

{indent}            var clipboardData = e.originalEvent ? e.originalEvent.clipboardData : e.clipboardData;
{indent}            if (clipboardData) {{
{indent}                var pastedText = clipboardData.getData('text');
{indent}                if (pastedText) {{
{indent}                    $numInput.val(pastedText.trim());
{indent}                    $numInput.focus();
{indent}                    e.preventDefault();
{indent}                }}
{indent}            }}
{indent}        }});

{indent}        pipWindow.addEventListener("pagehide", (event) => {{
{indent}            window.pipWindow = null;
{indent}            $originalParent.append($webphone[0]);
{indent}            $('#webphone-btn-pip').show();
{indent}        }});

{indent}    }} catch (err) {{
{indent}        console.error('Failed to open PiP window:', err);
{indent}    }}
{indent}}});"""

    new_content = content.replace(target_block, target_block + pip_js, 1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully added WebPhone PiP logic to {filepath}")
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_console_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    login_agent_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'login_agent.tpl')
    webphone_css = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'webphone.css')
    
    success = True
    success &= update_css(webphone_css)
    success &= update_template(agent_console_tpl, '        ')
    success &= update_template(login_agent_tpl, '    ')
    
    if success:
        print("All elements updated with PiP support successfully.")
    else:
        print("Some elements failed to update.")

if __name__ == '__main__':
    main()
