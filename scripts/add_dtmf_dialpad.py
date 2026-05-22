import os
import re

# Paths relative to the repository root
PATH_LOGIN_TPL = 'modules/agent_console/themes/default/login_agent.tpl'
PATH_CONSOLE_TPL = 'modules/agent_console/themes/default/agent_console.tpl'
PATH_SIP_PHONE_JS = 'modules/agent_console/themes/default/js/webphone/sip-phone.js'
PATH_WEBPHONE_CSS = 'modules/agent_console/themes/default/js/webphone/webphone.css'

DIALPAD_HTML = """        <div id="webphone-dialpad" class="webphone-dialpad" style="display: none;">
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="1">1</button>
                <button type="button" class="dialpad-btn" data-tone="2">2</button>
                <button type="button" class="dialpad-btn" data-tone="3">3</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="4">4</button>
                <button type="button" class="dialpad-btn" data-tone="5">5</button>
                <button type="button" class="dialpad-btn" data-tone="6">6</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="7">7</button>
                <button type="button" class="dialpad-btn" data-tone="8">8</button>
                <button type="button" class="dialpad-btn" data-tone="9">9</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="*">*</button>
                <button type="button" class="dialpad-btn" data-tone="0">0</button>
                <button type="button" class="dialpad-btn" data-tone="#">#</button>
            </div>
        </div>"""

DIALPAD_CSS = """

/* ============================================ 
   DTMF DIALPAD STYLES
   ============================================ */
.webphone-dialpad {
    display: none;
    margin-bottom: 10px;
    padding: 8px;
    background: #eaeaea;
    border-radius: 4px;
    border: 1px solid #ccc;
    box-sizing: border-box;
}

.dialpad-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}

.dialpad-row:last-child {
    margin-bottom: 0;
}

.dialpad-btn {
    flex: 1;
    margin: 0 3px;
    padding: 8px 0;
    font-size: 14px;
    font-weight: bold;
    color: #333;
    background: #f8f9fa;
    border: 1px solid #ced4da;
    border-radius: 4px;
    cursor: pointer;
    text-align: center;
    transition: all 0.1s ease-in-out;
}

.dialpad-btn:first-child {
    margin-left: 0;
}

.dialpad-btn:last-child {
    margin-right: 0;
}

.dialpad-btn:hover:not(:disabled) {
    background: #e2e6ea;
    border-color: #dae0e5;
}

.dialpad-btn:active:not(:disabled),
.dialpad-btn.active:not(:disabled) {
    background: #007bff;
    color: white;
    border-color: #007bff;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}
"""

DIALPAD_JS_BINDINGS = """    // Bind DTMF Dialpad buttons click
    $('.dialpad-btn').on('click', function() {
        var tone = $(this).data('tone');
        if (tone !== undefined) {
            WebPhone.sendDTMF(String(tone));
        }
    });

    // Intercept physical keyboard keydowns for DTMF
    $(document).on('keydown', function(e) {
        var phoneState = WebPhone.getState();
        if (phoneState.callState !== 'connected') {
            return;
        }

        // Check if focused on input/textarea other than #webphone-number
        var activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'SELECT' || activeEl.isContentEditable)) {
            if (activeEl.id !== 'webphone-number') {
                return;
            }
        }

        var tone = e.key;
        if (tone === '*' || tone === '#' || (tone >= '0' && tone <= '9')) {
            WebPhone.sendDTMF(tone);

            var $btn = $('.dialpad-btn[data-tone="' + tone + '"]');
            if ($btn.length) {
                $btn.addClass('active');
                setTimeout(function() {
                    $btn.removeClass('active');
                }, 150);
            }
            e.preventDefault();
        }
    });
"""

def modify_tpl(path):
    print(f"Modifying {path}...")
    with open(path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    # Detect line endings
    line_ending = '\r\n' if '\r\n' in content else '\n'

    # 1. Insert HTML above .webphone-buttons
    pattern_html = re.compile(r'(\r?\n)([ \t]*)<div class="webphone-buttons">')
    match_html = pattern_html.search(content)
    if not match_html:
        raise ValueError(f"Could not find <div class=\"webphone-buttons\"> in {path}")
    
    newline_char = match_html.group(1)
    indent = match_html.group(2)
    
    if 'id="webphone-dialpad"' not in content:
        # Format HTML with proper indentation and correct line endings
        formatted_html = DIALPAD_HTML.replace('\n', newline_char).replace('        ', indent)
        content = content[:match_html.start()] + newline_char + formatted_html + content[match_html.start():]
        print(f"  Inserted dialpad HTML in {path}")
    else:
        print(f"  Dialpad HTML already exists in {path}")

    # 2. Insert JS Bindings inside document.ready block
    if 'Bind DTMF Dialpad buttons click' not in content:
        pattern_js = re.compile(r'(\r?\n)([ \t]*)\$\(\'#webphone-number\'\)\.on\(\'keypress\',')
        match_js = pattern_js.search(content)
        if not match_js:
            raise ValueError(f"Could not find keypress binding in {path}")
        
        js_newline = match_js.group(1)
        js_indent = match_js.group(2)
        
        formatted_js = DIALPAD_JS_BINDINGS.replace('\n', js_newline).replace('    ', js_indent)
        content = content[:match_js.start()] + js_newline + formatted_js + content[match_js.start():]
        print(f"  Inserted JS Bindings in {path}")
    else:
        print(f"  JS Bindings already exist in {path}")

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

def modify_js(path):
    print(f"Modifying {path}...")
    with open(path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    line_ending = '\r\n' if '\r\n' in content else '\n'

    # 1. Add/Update sendDTMF function before toggleMute
    send_dtmf_code = """    function sendDTMF(tone) {
        if (!currentSession) {
            log('Cannot send DTMF: no active call session');
            return false;
        }
        var sdh = currentSession.sessionDescriptionHandler;
        if (sdh && typeof sdh.sendDtmf === 'function') {
            log('Sending DTMF tone via SDH: ' + tone);
            try {
                sdh.sendDtmf(tone);
                return true;
            } catch (e) {
                log('SDH sendDtmf failed: ' + e.message);
            }
        }
        if (typeof currentSession.info === 'function') {
            log('Sending DTMF tone via SIP INFO: ' + tone);
            try {
                var options = {
                    requestOptions: {
                        body: {
                            contentDisposition: "render",
                            contentType: "application/dtmf-relay",
                            content: "Signal=" + tone + "\\\\r\\\\nDuration=160"
                        }
                    }
                };
                currentSession.info(options);
                return true;
            } catch (e) {
                log('SIP INFO send failed: ' + e.message);
            }
        }
        log('Cannot send DTMF: no supported DTMF sending method found on session');
        return false;
    }

"""
    if 'session.sessionDescriptionHandler.sendDtmf' not in content:
        # Check if the old sendDTMF implementation is present
        if 'session does not support sendDTMF method' in content:
            # Replace the old function with the new one
            old_func_pattern = r'    function sendDTMF\(tone\) \{[\s\S]*?return true;\s*\}'
            content, count = re.subn(old_func_pattern, send_dtmf_code.strip('\n').replace('\n', line_ending), content)
            if count > 0:
                print("  Updated old sendDTMF implementation to robust version")
            else:
                raise ValueError("Could not find the old sendDTMF implementation to replace")
        elif 'function sendDTMF(tone)' not in content:
            target_str = '    function toggleMute()'
            if target_str not in content:
                raise ValueError(f"Could not find {target_str} in {path}")
            content = content.replace(target_str, send_dtmf_code.replace('\n', line_ending) + target_str)
            print("  Added sendDTMF function")
        else:
            print("  sendDTMF function exists but cannot determine if it's updated or old. No changes made.")
    else:
        print("  Robust sendDTMF function already exists")

    # 2. Update updateUI() to show/hide dialpad
    if '$dialpad.show()' not in content:
        target_ui_vars = (
            "        var $reconnectBtn = $('#webphone-btn-reconnect');" + line_ending +
            "        var $muteBtn = $('#webphone-btn-mute');" + line_ending +
            "        var $statusText = $status.find('.status-text');"
        )
        
        replacement_ui_vars = (
            "        var $reconnectBtn = $('#webphone-btn-reconnect');" + line_ending +
            "        var $muteBtn = $('#webphone-btn-mute');" + line_ending +
            "        var $dialpad = $('#webphone-dialpad');" + line_ending +
            "        var $statusText = $status.find('.status-text');"
        )
        
        if target_ui_vars not in content:
            raise ValueError(f"Could not find exact target_ui_vars in {path}")
        
        content = content.replace(target_ui_vars, replacement_ui_vars)

        target_ui_end = (
            "                stopRingtoneSound();" + line_ending +
            "                break;" + line_ending +
            "        }" + line_ending +
            "    }"
        )
        
        replacement_ui_end = (
            "                stopRingtoneSound();" + line_ending +
            "                break;" + line_ending +
            "        }" + line_ending +
            line_ending +
            "        if (state.callState === 'connected') {" + line_ending +
            "            $dialpad.show();" + line_ending +
            "        } else {" + line_ending +
            "            $dialpad.hide();" + line_ending +
            "        }" + line_ending +
            "    }"
        )
        
        if target_ui_end not in content:
            raise ValueError(f"Could not find target updateUI end in {path}")
        
        content = content.replace(target_ui_end, replacement_ui_end)
        print("  Added dialpad show/hide logic to updateUI")
    else:
        print("  Dialpad show/hide logic already exists in updateUI")

    # 3. Export sendDTMF in returned WebPhone object
    if 'sendDTMF: sendDTMF' not in content:
        target_export = '        toggleMute: toggleMute,'
        if target_export not in content:
            raise ValueError(f"Could not find {target_export} in {path}")
        
        content = content.replace(target_export, target_export + line_ending + '        sendDTMF: sendDTMF,')
        print("  Exported sendDTMF method")
    else:
        print("  sendDTMF method already exported")

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

def modify_css(path):
    print(f"Modifying {path}...")
    with open(path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    line_ending = '\r\n' if '\r\n' in content else '\n'

    if 'DTMF DIALPAD STYLES' not in content:
        formatted_css = DIALPAD_CSS.replace('\n', line_ending)
        content += formatted_css
        print("  Appended DTMF CSS styles")
    else:
        print("  DTMF CSS styles already exist")

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

def main():
    modify_tpl(PATH_LOGIN_TPL)
    modify_tpl(PATH_CONSOLE_TPL)
    modify_js(PATH_SIP_PHONE_JS)
    modify_css(PATH_WEBPHONE_CSS)
    print("All files modified successfully!")

if __name__ == '__main__':
    main()
