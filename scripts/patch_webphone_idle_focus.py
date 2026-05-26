#!/usr/bin/env python3
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sip_phone_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'sip-phone.js')
    
    if not os.path.exists(sip_phone_js):
        print(f"Error: File not found {sip_phone_js}")
        return
        
    with open(sip_phone_js, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'isTypingElsewhere' in content:
        print("Focus patch already present in sip-phone.js")
        return
        
    target_str = """                $('#webphone-number').prop('disabled', false);
                stopRingtoneSound();"""
                
    replacement_str = """                $('#webphone-number').prop('disabled', false);
                var activeEl = document.activeElement;
                var isTypingElsewhere = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable) && activeEl.id !== 'webphone-number';
                if (!isTypingElsewhere) {
                    $('#webphone-number').focus();
                }
                stopRingtoneSound();"""
                
    if target_str not in content:
        print("Error: Could not find target pattern in sip-phone.js")
        return
        
    new_content = content.replace(target_str, replacement_str, 1)
    
    with open(sip_phone_js, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Successfully patched focus behavior in sip-phone.js")

if __name__ == '__main__':
    main()
