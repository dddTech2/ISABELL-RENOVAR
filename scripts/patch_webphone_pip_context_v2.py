#!/usr/bin/env python3
import os

def patch_sip_phone(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content_norm = content.replace('\r\n', '\n')

    # Replace iceGatheringTimeout: 500 with iceGatheringTimeout: 2000
    target = "iceGatheringTimeout: 500"
    replacement = "iceGatheringTimeout: 2000"

    if target in content_norm:
        content_norm = content_norm.replace(target, replacement)
        print(f"Updated iceGatheringTimeout to 2000 in {filepath}")
    else:
        print(f"iceGatheringTimeout: 500 not found or already patched in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def patch_template(filepath, indent):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    # 1. Target block for setting up PiP window (where we insert the monkey patch)
    target_setup = """{indent}window.pipWindow = pipWindow;

{indent}const $webphone = $('.webphone-panel');
{indent}const $originalParent = $webphone.parent();

{indent}pipWindow.document.body.append($webphone[0]);""".replace('{indent}', indent)

    replacement_setup = """{indent}window.pipWindow = pipWindow;

{indent}const $webphone = $('.webphone-panel');
{indent}const $originalParent = $webphone.parent();

{indent}pipWindow.document.body.append($webphone[0]);

{indent}// Monkey patch WebRTC and audio APIs to execute in the context of the active PiP window
{indent}// This prevents background tab throttling/delays when the parent window is inactive
{indent}if (pipWindow.navigator && pipWindow.navigator.mediaDevices) {
{indent}    window.__originalGetUserMedia = navigator.mediaDevices.getUserMedia;
{indent}    navigator.mediaDevices.getUserMedia = function(constraints) {
{indent}        if (window.pipWindow && !window.pipWindow.closed && window.pipWindow.navigator && window.pipWindow.navigator.mediaDevices) {
{indent}            console.log('[WebPhone] Redirecting getUserMedia to PiP window context');
{indent}            return window.pipWindow.navigator.mediaDevices.getUserMedia(constraints);
{indent}        }
{indent}        return window.__originalGetUserMedia.call(navigator.mediaDevices, constraints);
{indent}    };
{indent}}

{indent}if (pipWindow.RTCPeerConnection) {
{indent}    window.__originalRTCPeerConnection = window.RTCPeerConnection;
{indent}    window.RTCPeerConnection = function(config) {
{indent}        if (window.pipWindow && !window.pipWindow.closed && window.pipWindow.RTCPeerConnection) {
{indent}            console.log('[WebPhone] Redirecting RTCPeerConnection to PiP window context');
{indent}            return new window.pipWindow.RTCPeerConnection(config);
{indent}        }
{indent}        return new window.__originalRTCPeerConnection(config);
{indent}    };
{indent}    window.RTCPeerConnection.prototype = window.__originalRTCPeerConnection.prototype;
{indent}}

{indent}const AudioCtxClass = pipWindow.AudioContext || pipWindow.webkitAudioContext;
{indent}if (AudioCtxClass) {
{indent}    window.__originalAudioContext = window.AudioContext;
{indent}    window.__originalWebkitAudioContext = window.webkitAudioContext;
{indent}    window.AudioContext = function() {
{indent}        if (window.pipWindow && !window.pipWindow.closed) {
{indent}            console.log('[WebPhone] Redirecting AudioContext to PiP window context');
{indent}            return new AudioCtxClass();
{indent}        }
{indent}        return new window.__originalAudioContext();
{indent}    };
{indent}    if (window.webkitAudioContext) {
{indent}        window.webkitAudioContext = window.AudioContext;
{indent}    }
{indent}}""".replace('{indent}', indent)

    # 2. Target block for closing PiP window (where we restore the original WebRTC APIs)
    target_close = """{indent}pipWindow.addEventListener("pagehide", (event) => {
{indent}    window.pipWindow = null;
{indent}    $originalParent.append($webphone[0]);

{indent}    // Restore audio elements to main body on PiP close
{indent}    if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
{indent}        const audios = WebPhone.getAudioElements();
{indent}        if (audios.remote) document.body.append(audios.remote);
{indent}        if (audios.local) document.body.append(audios.local);
{indent}    }""".replace('{indent}', indent)

    replacement_close = """{indent}pipWindow.addEventListener("pagehide", (event) => {
{indent}    window.pipWindow = null;
{indent}    $originalParent.append($webphone[0]);

{indent}    // Restore WebRTC and AudioContext APIs
{indent}    if (window.__originalGetUserMedia) {
{indent}        navigator.mediaDevices.getUserMedia = window.__originalGetUserMedia;
{indent}        delete window.__originalGetUserMedia;
{indent}    }
{indent}    if (window.__originalRTCPeerConnection) {
{indent}        window.RTCPeerConnection = window.__originalRTCPeerConnection;
{indent}        delete window.__originalRTCPeerConnection;
{indent}    }
{indent}    if (window.__originalAudioContext) {
{indent}        window.AudioContext = window.__originalAudioContext;
{indent}        delete window.__originalAudioContext;
{indent}    }
{indent}    if (window.__originalWebkitAudioContext) {
{indent}        window.webkitAudioContext = window.__originalWebkitAudioContext;
{indent}        delete window.__originalWebkitAudioContext;
{indent}    }

{indent}    // Restore audio elements to main body on PiP close
{indent}    if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
{indent}        const audios = WebPhone.getAudioElements();
{indent}        if (audios.remote) document.body.append(audios.remote);
{indent}        if (audios.local) document.body.append(audios.local);
{indent}    }""".replace('{indent}', indent)

    # Apply setup patch if not already present
    if 'Redirecting RTCPeerConnection to PiP window context' not in content_norm:
        if target_setup in content_norm:
            content_norm = content_norm.replace(target_setup, replacement_setup, 1)
            print(f"Applied WebRTC context redirection patch to {filepath}")
        else:
            print(f"Error: Could not find target setup block in {filepath}")
            return False
    else:
        print(f"WebRTC context redirection patch already present in {filepath}")

    # Apply close patch if not already present
    if 'Restore WebRTC and AudioContext APIs' not in content_norm:
        if target_close in content_norm:
            content_norm = content_norm.replace(target_close, replacement_close, 1)
            print(f"Applied WebRTC context restoration patch to {filepath}")
        else:
            print(f"Error: Could not find target close block in {filepath}")
            return False
    else:
        print(f"WebRTC context restoration patch already present in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sip_phone_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'sip-phone.js')
    agent_console_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    login_agent_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'login_agent.tpl')
    
    success = True
    success &= patch_sip_phone(sip_phone_js)
    success &= patch_template(agent_console_tpl, '                ') # 16 spaces
    success &= patch_template(login_agent_tpl, '            ') # 12 spaces
    
    if success:
        print("All WebRTC context redirection and ICE timeout modifications applied successfully.")
        return 0
    else:
        print("Failed to apply some modifications.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
