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
        
    # Check if patch is already applied
    if 'reconnectionDelay: 5' in content and 'logLevel: \'warn\'' in content:
        print("Warnings and logLevel patch already present in sip-phone.js")
        return

    # Replace reconnectionTimeout with reconnectionDelay
    target_options = """                reconnectionAttempts: 10,
                reconnectionTimeout: 5"""
                
    replacement_options = """                reconnectionAttempts: 10,
                reconnectionDelay: 5"""

    if target_options not in content:
        print("Error: Could not find target reconnectionAttempts/reconnectionTimeout pattern in sip-phone.js")
        return
    content = content.replace(target_options, replacement_options, 1)

    # Add logLevel: 'warn'
    target_loglevel = """            register: false,
            noAnswerTimeout: 60,"""
            
    replacement_loglevel = """            register: false,
            noAnswerTimeout: 60,
            logLevel: 'warn',"""

    if target_loglevel not in content:
        print("Error: Could not find target register/noAnswerTimeout pattern in sip-phone.js")
        return
    content = content.replace(target_loglevel, replacement_loglevel, 1)

    # Save changes
    with open(sip_phone_js, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Successfully patched reconnectionDelay and logLevel in sip-phone.js")

if __name__ == '__main__':
    main()
