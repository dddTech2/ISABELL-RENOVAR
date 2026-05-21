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
        "        autoAnswer: false\n"
        "    };"
    )

    replacement_state = (
        "    var state = {\n"
        "        registered: false,\n"
        "        callState: 'idle', // idle, calling, ringing, connected\n"
        "        authFailed: false,\n"
        "        autoAnswer: false,\n"
        "        lastCallError: '' // Stores temporary call rejection errors (e.g. 404, 486)\n"
        "    };"
    )

    # 2. Target block for updateUI()
    target_update_ui = (
        "        if (state.authFailed) {\n"
        "            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');\n"
        "            $statusText.text('Error de autenticacion');\n"
        "        } else if (state.registered) {\n"
        "            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');\n"
        "            $statusText.text('Registrado');\n"
        "        } else {\n"
        "            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');\n"
        "            $statusText.text('No registrado');\n"
        "        }"
    )

    replacement_update_ui = (
        "        if (state.authFailed) {\n"
        "            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');\n"
        "            $statusText.text('Error de autenticacion');\n"
        "        } else if (state.lastCallError) {\n"
        "            $status.removeClass('webphone-registered webphone-connected').addClass('webphone-unregistered');\n"
        "            $statusText.text(state.lastCallError);\n"
        "        } else if (state.registered) {\n"
        "            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');\n"
        "            $statusText.text('Registrado');\n"
        "        } else {\n"
        "            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');\n"
        "            $statusText.text('No registrado');\n"
        "        }"
    )

    # 3. Target block for call() function
    target_call = (
        "    function call(number) {\n"
        "        if (!userAgent || !state.registered) {\n"
        "            log('Cannot call: not registered');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        if (!number || number.trim() === '') {\n"
        "            log('Cannot call: no number provided');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        // If already in a call, don't start a new one\n"
        "        if (currentSession) {\n"
        "            log('Already in a call, cannot dial');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        log('Calling: ' + number);\n"
        "\n"
        "        var target = SIP.UserAgent.makeURI('sip:' + number + '@' + config.domain);\n"
        "        if (!target) {\n"
        "            log('Invalid target URI');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        updateCallState('calling');\n"
        "\n"
        "        var inviterOptions = {\n"
        "            sessionDescriptionHandlerOptions: {\n"
        "                constraints: {\n"
        "                    audio: true,\n"
        "                    video: false\n"
        "                }\n"
        "            }\n"
        "        };\n"
        "\n"
        "        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);\n"
        "\n"
        "        currentSession.stateChange.addListener(function(newState) {\n"
        "            log('Outgoing session state: ' + newState);\n"
        "            switch(newState) {\n"
        "                case SIP.SessionState.Established:\n"
        "                    updateCallState('connected');\n"
        "                    attachMedia();\n"
        "                    break;\n"
        "                case SIP.SessionState.Terminated:\n"
        "                    log('Outgoing call terminated');\n"
        "                    stopRingtoneSound();\n"
        "                    currentSession = null;\n"
        "                    updateCallState('idle');\n"
        "                    break;\n"
        "            }\n"
        "        });\n"
        "\n"
        "        currentSession.invite().then(function() {\n"
        "            log('INVITE sent successfully');\n"
        "        }).catch(function(e) {\n"
        "            log('INVITE failed: ' + (e.message || e));\n"
        "            stopRingtoneSound();\n"
        "            currentSession = null;\n"
        "            updateCallState('idle');\n"
        "        });\n"
        "    }"
    )

    replacement_call = (
        "    function call(number) {\n"
        "        if (!userAgent || !state.registered) {\n"
        "            log('Cannot call: not registered');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        if (!number || number.trim() === '') {\n"
        "            log('Cannot call: no number provided');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        // If already in a call, don't start a new one\n"
        "        if (currentSession) {\n"
        "            log('Already in a call, cannot dial');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        log('Calling: ' + number);\n"
        "        state.lastCallError = ''; // Clear previous error\n"
        "\n"
        "        var target = SIP.UserAgent.makeURI('sip:' + number + '@' + config.domain);\n"
        "        if (!target) {\n"
        "            log('Invalid target URI');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        updateCallState('calling');\n"
        "\n"
        "        var inviterOptions = {\n"
        "            sessionDescriptionHandlerOptions: {\n"
        "                constraints: {\n"
        "                    audio: true,\n"
        "                    video: false\n"
        "                }\n"
        "            }\n"
        "        };\n"
        "\n"
        "        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);\n"
        "\n"
        "        currentSession.stateChange.addListener(function(newState) {\n"
        "            log('Outgoing session state: ' + newState);\n"
        "            switch(newState) {\n"
        "                case SIP.SessionState.Established:\n"
        "                    updateCallState('connected');\n"
        "                    attachMedia();\n"
        "                    break;\n"
        "                case SIP.SessionState.Terminated:\n"
        "                    log('Outgoing call terminated');\n"
        "                    stopRingtoneSound();\n"
        "                    currentSession = null;\n"
        "                    updateCallState('idle');\n"
        "                    break;\n"
        "            }\n"
        "        });\n"
        "\n"
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
        "        };\n"
        "\n"
        "        currentSession.invite(inviteOptions).then(function() {\n"
        "            log('INVITE sent successfully');\n"
        "        }).catch(function(e) {\n"
        "            log('INVITE failed: ' + (e.message || e));\n"
        "            stopRingtoneSound();\n"
        "            currentSession = null;\n"
        "            updateCallState('idle');\n"
        "        });\n"
        "    }"
    )

    # Normalize line endings to avoid mismatch issues
    content_norm = content.replace('\r\n', '\n')
    target_state_norm = target_state.replace('\r\n', '\n')
    replacement_state_norm = replacement_state.replace('\r\n', '\n')
    target_update_ui_norm = target_update_ui.replace('\r\n', '\n')
    replacement_update_ui_norm = replacement_update_ui.replace('\r\n', '\n')
    target_call_norm = target_call.replace('\r\n', '\n')
    replacement_call_norm = replacement_call.replace('\r\n', '\n')

    # Apply changes
    if target_state_norm not in content_norm:
        print("Error: Target state block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_state_norm, replacement_state_norm)

    if target_update_ui_norm not in content_norm:
        print("Error: Target updateUI block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_update_ui_norm, replacement_update_ui_norm)

    if target_call_norm not in content_norm:
        print("Error: Target call block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_call_norm, replacement_call_norm)

    # Keep original file line endings (detect if it used CRLF)
    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("Success: sip-phone.js has been successfully updated with SIP error code mappings.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
