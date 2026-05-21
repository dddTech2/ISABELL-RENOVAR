import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    target_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")

    print(f"Target file: {target_file}")

    if not os.path.exists(target_file):
        print(f"Error: Target file not found at {target_file}")
        return 1

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Target block for state definition
    target_state = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '' // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "    };"
    )

    replacement_state = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '', // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "        isVoicemail: false // Track if call was answered by a voicemail system\n"
        "    };"
    )

    # 2. Target block for updateUI()
    target_update_ui = (
        "            case 'connected':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-connected');\n"
        "                $statusText.text('EN LLAMADA');\n"
        "                stopRingtoneSound();\n"
        "                break;"
    )

    replacement_update_ui = (
        "            case 'connected':\n"
        "                $callBtn.hide();\n"
        "                $hangupBtn.show().prop('disabled', false);\n"
        "                $answerBtn.hide();\n"
        "                $('#webphone-number').prop('disabled', true);\n"
        "                $status.addClass('webphone-connected');\n"
        "                if (state.isVoicemail) {\n"
        "                    $statusText.text('BUZÓN DE VOZ');\n"
        "                } else {\n"
        "                    $statusText.text('EN LLAMADA');\n"
        "                }\n"
        "                stopRingtoneSound();\n"
        "                break;"
    )

    # 3. Target block for resetting flag in call()
    target_call_reset = (
        "        log('Calling: ' + number);\n"
        "        state.lastCallError = ''; // Clear previous error"
    )

    replacement_call_reset = (
        "        log('Calling: ' + number);\n"
        "        state.lastCallError = ''; // Clear previous error\n"
        "        state.isVoicemail = false; // Reset voicemail flag"
    )

    # 4. Target block for inviteOptions
    target_invite_options = (
        "        var inviteOptions = {\n"
        "            requestDelegate: {\n"
        "                onReject: function(response) {\n"
        "                    var statusCode = response.message.statusCode;\n"
        "                    var reason = response.message.reasonPhrase || 'Rechazado';\n"
        "                    log('Call rejected, status code: ' + statusCode + ' reason: ' + reason);\n"
        "\n"
        "                    if (statusCode === 487) {\n"
        "                        return; // Normal cancellation when user hangs up before answering\n"
        "                    }\n"
        "\n"
        "                    var friendlyMessage = 'Llamada rechazada';\n"
        "                    if (statusCode === 404) {\n"
        "                        friendlyMessage = 'Número no existe (404)';\n"
        "                    } else if (statusCode === 486) {\n"
        "                        friendlyMessage = 'Línea ocupada (486)';\n"
        "                    } else if (statusCode === 480) {\n"
        "                        friendlyMessage = 'No disponible (480)';\n"
        "                    } else if (statusCode === 403) {\n"
        "                        friendlyMessage = 'Sin permisos (403)';\n"
        "                    } else if (statusCode === 400) {\n"
        "                        friendlyMessage = 'Número inválido (400)';\n"
        "                    } else if (statusCode === 503) {\n"
        "                        friendlyMessage = 'Congestión / Canales ocupados (503)';\n"
        "                    } else {\n"
        "                        friendlyMessage = 'Error ' + statusCode + ': ' + reason;\n"
        "                    }\n"
        "\n"
        "                    state.lastCallError = friendlyMessage;\n"
        "                    updateUI();\n"
        "\n"
        "                    // Clear error message after 5 seconds\n"
        "                    setTimeout(function() {\n"
        "                        if (state.lastCallError === friendlyMessage) {\n"
        "                            state.lastCallError = '';\n"
        "                            updateUI();\n"
        "                        }\n"
        "                    }, 5000);\n"
        "                }\n"
        "            }\n"
        "        };"
    )

    replacement_invite_options = (
        "        var inviteOptions = {\n"
        "            requestDelegate: {\n"
        "                onReject: function(response) {\n"
        "                    var statusCode = response.message.statusCode;\n"
        "                    var reason = response.message.reasonPhrase || 'Rechazado';\n"
        "                    log('Call rejected, status code: ' + statusCode + ' reason: ' + reason);\n"
        "\n"
        "                    if (statusCode === 487) {\n"
        "                        return; // Normal cancellation when user hangs up before answering\n"
        "                    }\n"
        "\n"
        "                    var friendlyMessage = 'Llamada rechazada';\n"
        "                    if (statusCode === 404) {\n"
        "                        friendlyMessage = 'Número no existe (404)';\n"
        "                    } else if (statusCode === 486) {\n"
        "                        friendlyMessage = 'Línea ocupada (486)';\n"
        "                    } else if (statusCode === 480) {\n"
        "                        friendlyMessage = 'No disponible (480)';\n"
        "                    } else if (statusCode === 403) {\n"
        "                        friendlyMessage = 'Sin permisos (403)';\n"
        "                    } else if (statusCode === 400) {\n"
        "                        friendlyMessage = 'Número inválido (400)';\n"
        "                    } else if (statusCode === 503) {\n"
        "                        friendlyMessage = 'Congestión / Canales ocupados (503)';\n"
        "                    } else {\n"
        "                        friendlyMessage = 'Error ' + statusCode + ': ' + reason;\n"
        "                    }\n"
        "\n"
        "                    state.lastCallError = friendlyMessage;\n"
        "                    updateUI();\n"
        "\n"
        "                    // Clear error message after 5 seconds\n"
        "                    setTimeout(function() {\n"
        "                        if (state.lastCallError === friendlyMessage) {\n"
        "                            state.lastCallError = '';\n"
        "                            updateUI();\n"
        "                        }\n"
        "                    }, 5000);\n"
        "                },\n"
        "                onAccept: function(response) {\n"
        "                    log('Call accepted (200 OK)');\n"
        "                    if (response && response.message) {\n"
        "                        var vmHeader = response.message.getHeader('X-Voicemail') || response.message.getHeader('X-Asterisk-Voicemail');\n"
        "                        if (vmHeader && (vmHeader.toLowerCase() === 'yes' || vmHeader.toLowerCase() === 'true')) {\n"
        "                            log('Detected voicemail answer via custom SIP header');\n"
        "                            state.isVoicemail = true;\n"
        "                            updateUI();\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        };"
    )

    # Normalize line endings
    content_norm = content.replace('\r\n', '\n')
    target_state_norm = target_state.replace('\r\n', '\n')
    replacement_state_norm = replacement_state.replace('\r\n', '\n')
    target_update_ui_norm = target_update_ui.replace('\r\n', '\n')
    replacement_update_ui_norm = replacement_update_ui.replace('\r\n', '\n')
    target_call_reset_norm = target_call_reset.replace('\r\n', '\n')
    replacement_call_reset_norm = replacement_call_reset.replace('\r\n', '\n')
    target_invite_options_norm = target_invite_options.replace('\r\n', '\n')
    replacement_invite_options_norm = replacement_invite_options.replace('\r\n', '\n')

    # Apply changes
    if target_state_norm not in content_norm:
        print("Error: Target state block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_state_norm, replacement_state_norm)

    if target_update_ui_norm not in content_norm:
        print("Error: Target updateUI block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_update_ui_norm, replacement_update_ui_norm)

    if target_call_reset_norm not in content_norm:
        print("Error: Target call reset block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_call_reset_norm, replacement_call_reset_norm)

    if target_invite_options_norm not in content_norm:
        print("Error: Target inviteOptions block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_invite_options_norm, replacement_invite_options_norm)

    # Keep original file line endings
    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("Success: sip-phone.js has been successfully updated with voicemail header detection.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
