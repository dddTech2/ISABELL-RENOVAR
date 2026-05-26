#!/usr/bin/env python3
import os

def patch_sip_phone(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Shadow $ selector at the top of IIFE
    target_iife = "var WebPhone = (function() {\n    var userAgent = null;"
    replacement_iife = """var WebPhone = (function() {
    function $(selector) {
        var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
        return window.jQuery(selector, context);
    }
    var userAgent = null;"""

    if 'function $(selector)' not in content:
        content = content.replace(target_iife, replacement_iife, 1)
        print(f"Shadowed $ in {filepath}")
    else:
        print(f"Local $ shadowing already present in {filepath}")

    # 2. Expose getAudioElements in public API
    target_api = """        setMute: setMute,
        isRegistered: function() { return state.registered; }"""
        
    replacement_api = """        setMute: setMute,
        getAudioElements: function() { return audioElements; },
        isRegistered: function() { return state.registered; }"""

    if 'getAudioElements' not in content:
        content = content.replace(target_api, replacement_api, 1)
        print(f"Exposed getAudioElements in public API of {filepath}")
    else:
        print(f"getAudioElements already exposed in public API of {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True

def patch_template(filepath, indent):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Define $wp helper before Bind UI events
    target_bind = f"{indent}// Bind UI events"
    replacement_bind = """{indent}var $wp = function(selector) {
{indent}    var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
{indent}    return $(selector, context);
{indent}};

{indent}// Bind UI events""".replace('{indent}', indent)

    if '$wp' not in content:
        content = content.replace(target_bind, replacement_bind, 1)
        print(f"Injected $wp helper in {filepath}")
    else:
        print(f"$wp helper already present in {filepath}")

    # 2. Replace $('#webphone-number').val() in click
    target_val = f"{indent}    var number = $('#webphone-number').val().trim();"
    replacement_val = f"{indent}    var number = $wp('#webphone-number').val().trim();"
    content = content.replace(target_val, replacement_val, 1)

    # 3. Replace $('.dialpad-btn[data-tone="' + tone + '"]') in keydown
    target_btn = f"{indent}                    var $btn = $('.dialpad-btn[data-tone=\"' + tone + '\"]');"
    replacement_btn = f"{indent}                    var $btn = $wp('.dialpad-btn[data-tone=\"' + tone + '\"]');"
    content = content.replace(target_btn, replacement_btn, 1)

    # 4. Integrate audio elements migration inside PiP click handler
    target_pip_append = f"{indent}        pipWindow.document.body.append($webphone[0]);"
    replacement_pip_append = """{indent}        pipWindow.document.body.append($webphone[0]);

{indent}        // Move audio elements to PiP window body to prevent background throttling
{indent}        if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
{indent}            const audios = WebPhone.getAudioElements();
{indent}            if (audios.remote) pipWindow.document.body.append(audios.remote);
{indent}            if (audios.local) pipWindow.document.body.append(audios.local);
{indent}        }""".replace('{indent}', indent)

    if 'Move audio elements to PiP window body' not in content:
        content = content.replace(target_pip_append, replacement_pip_append, 1)
        print(f"Added audio elements migration to PiP opening in {filepath}")

    # 5. Restore audio elements inside pagehide
    target_pip_restore = """{indent}        pipWindow.addEventListener("pagehide", (event) => {
{indent}            window.pipWindow = null;
{indent}            $originalParent.append($webphone[0]);""".replace('{indent}', indent)

    replacement_pip_restore = """{indent}        pipWindow.addEventListener("pagehide", (event) => {
{indent}            window.pipWindow = null;
{indent}            $originalParent.append($webphone[0]);

{indent}            // Restore audio elements to main body on PiP close
{indent}            if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
{indent}                const audios = WebPhone.getAudioElements();
{indent}                if (audios.remote) document.body.append(audios.remote);
{indent}                if (audios.local) document.body.append(audios.local);
{indent}            }""".replace('{indent}', indent)

    if 'Restore audio elements to main body' not in content:
        content = content.replace(target_pip_restore, replacement_pip_restore, 1)
        print(f"Added audio elements restoration on PiP close in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sip_phone_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'sip-phone.js')
    agent_console_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    login_agent_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'login_agent.tpl')
    
    success = True
    success &= patch_sip_phone(sip_phone_js)
    success &= patch_template(agent_console_tpl, '        ')
    success &= patch_template(login_agent_tpl, '    ')
    
    if success:
        print("All scoping and audio migration fixes applied successfully.")
    else:
        print("Failed to apply some fixes.")

if __name__ == '__main__':
    main()
