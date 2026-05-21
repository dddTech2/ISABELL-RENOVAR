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

    # 1. Target block for attachMedia()
    target_attach_media = (
        "    function attachMedia() {\n"
        "        if (!currentSession) return;\n"
        "\n"
        "        var pc = currentSession.sessionDescriptionHandler.peerConnection;\n"
        "        if (!pc) {\n"
        "            log('No peerConnection available');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        log('Attaching media, setting up track listeners');\n"
        "\n"
        "        var remoteAudio = audioElements.remote;\n"
        "\n"
        "        // Function to assign stream/track to audio element\n"
        "        function setRemoteStream(stream) {\n"
        "            if (remoteAudio.srcObject !== stream) {\n"
        "                remoteAudio.srcObject = stream;\n"
        "                log('Remote media stream assigned');\n"
        "            }\n"
        "            remoteAudio.play().catch(function(e) {\n"
        "                log('Audio play failed: ' + e.message);\n"
        "            });\n"
        "        }\n"
        "\n"
        "        // Set up ontrack listener on the peer connection if not already set\n"
        "        if (!pc._mediaAttached) {\n"
        "            pc._mediaAttached = true;\n"
        "            pc.addEventListener('track', function(event) {\n"
        "                log('pc ontrack event received, kind: ' + event.track.kind);\n"
        "                if (event.streams && event.streams[0]) {\n"
        "                    setRemoteStream(event.streams[0]);\n"
        "                } else {\n"
        "                    var stream = remoteAudio.srcObject || new MediaStream();\n"
        "                    stream.addTrack(event.track);\n"
        "                    setRemoteStream(stream);\n"
        "                }\n"
        "            });\n"
        "        }\n"
        "\n"
        "        // Also check if receivers already have tracks\n"
        "        var remoteStream = null;\n"
        "        pc.getReceivers().forEach(function(receiver) {\n"
        "            if (receiver.track) {\n"
        "                log('Found existing receiver track: ' + receiver.track.kind);\n"
        "                if (!remoteStream) {\n"
        "                    remoteStream = new MediaStream();\n"
        "                }\n"
        "                remoteStream.addTrack(receiver.track);\n"
        "            }\n"
        "        });\n"
        "\n"
        "        if (remoteStream) {\n"
        "            setRemoteStream(remoteStream);\n"
        "        }\n"
        "    }"
    )

    replacement_attach_media = (
        "    function attachMedia(sdh) {\n"
        "        if (!currentSession) return;\n"
        "\n"
        "        var handler = sdh || currentSession.sessionDescriptionHandler;\n"
        "        if (!handler) {\n"
        "            log('No sessionDescriptionHandler available');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        var pc = handler.peerConnection;\n"
        "        if (!pc) {\n"
        "            log('No peerConnection available');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        log('Attaching media, setting up track listeners');\n"
        "\n"
        "        var remoteAudio = audioElements.remote;\n"
        "\n"
        "        // Function to assign stream/track to audio element\n"
        "        function setRemoteStream(stream) {\n"
        "            if (remoteAudio.srcObject !== stream) {\n"
        "                remoteAudio.srcObject = stream;\n"
        "                log('Remote media stream assigned');\n"
        "            }\n"
        "            remoteAudio.play().catch(function(e) {\n"
        "                log('Audio play failed: ' + e.message);\n"
        "            });\n"
        "        }\n"
        "\n"
        "        // Set up ontrack listener on the peer connection if not already set\n"
        "        if (!pc._mediaAttached) {\n"
        "            pc._mediaAttached = true;\n"
        "            pc.addEventListener('track', function(event) {\n"
        "                log('pc ontrack event received, kind: ' + event.track.kind);\n"
        "                stopRingtoneSound(); // Stop ringtone when remote audio track starts\n"
        "                if (event.streams && event.streams[0]) {\n"
        "                    setRemoteStream(event.streams[0]);\n"
        "                } else {\n"
        "                    var stream = remoteAudio.srcObject || new MediaStream();\n"
        "                    stream.addTrack(event.track);\n"
        "                    setRemoteStream(stream);\n"
        "                }\n"
        "            });\n"
        "        }\n"
        "\n"
        "        // Also check if receivers already have tracks\n"
        "        var remoteStream = null;\n"
        "        pc.getReceivers().forEach(function(receiver) {\n"
        "            if (receiver.track) {\n"
        "                log('Found existing receiver track: ' + receiver.track.kind);\n"
        "                stopRingtoneSound(); // Stop ringtone if we already have receiver tracks\n"
        "                if (!remoteStream) {\n"
        "                    remoteStream = new MediaStream();\n"
        "                }\n"
        "                remoteStream.addTrack(receiver.track);\n"
        "            }\n"
        "        });\n"
        "\n"
        "        if (remoteStream) {\n"
        "            setRemoteStream(remoteStream);\n"
        "        }\n"
        "    }"
    )

    # 2. Target block for handleIncomingCall()
    target_handle_incoming = (
        "        currentSession = session;\n"
        "        updateCallState('ringing');"
    )

    replacement_handle_incoming = (
        "        currentSession = session;\n"
        "        currentSession.delegate = {\n"
        "            onSessionDescriptionHandler: function(sdh, provisional) {\n"
        "                log('Incoming SessionDescriptionHandler created. Provisional: ' + provisional);\n"
        "                attachMedia(sdh);\n"
        "            }\n"
        "        };\n"
        "        updateCallState('ringing');"
    )

    # 3. Target block for call() function
    target_call_setup = (
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
        "        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);"
    )

    replacement_call_setup = (
        "        updateCallState('calling');\n"
        "\n"
        "        var inviterOptions = {\n"
        "            earlyMedia: true,\n"
        "            sessionDescriptionHandlerOptions: {\n"
        "                constraints: {\n"
        "                    audio: true,\n"
        "                    video: false\n"
        "                }\n"
        "            }\n"
        "        };\n"
        "\n"
        "        currentSession = new SIP.Inviter(userAgent, target, inviterOptions);\n"
        "        currentSession.delegate = {\n"
        "            onSessionDescriptionHandler: function(sdh, provisional) {\n"
        "                log('Outgoing SessionDescriptionHandler created. Provisional: ' + provisional);\n"
        "                attachMedia(sdh);\n"
        "            }\n"
        "        };"
    )

    # 4. Target block for inviteOptions in call()
    target_invite_options = (
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
        "                    }"
    )

    replacement_invite_options = (
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
        "                    }"
    )

    # Normalize line endings to avoid mismatch issues
    content_norm = content.replace('\r\n', '\n')
    target_attach_media_norm = target_attach_media.replace('\r\n', '\n')
    replacement_attach_media_norm = replacement_attach_media.replace('\r\n', '\n')
    target_handle_incoming_norm = target_handle_incoming.replace('\r\n', '\n')
    replacement_handle_incoming_norm = replacement_handle_incoming.replace('\r\n', '\n')
    target_call_setup_norm = target_call_setup.replace('\r\n', '\n')
    replacement_call_setup_norm = replacement_call_setup.replace('\r\n', '\n')
    target_invite_options_norm = target_invite_options.replace('\r\n', '\n')
    replacement_invite_options_norm = replacement_invite_options.replace('\r\n', '\n')

    # Apply changes
    if target_attach_media_norm not in content_norm:
        print("Error: Target attachMedia block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_attach_media_norm, replacement_attach_media_norm)

    if target_handle_incoming_norm not in content_norm:
        print("Error: Target handleIncomingCall block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_handle_incoming_norm, replacement_handle_incoming_norm)

    if target_call_setup_norm not in content_norm:
        print("Error: Target call setup block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_call_setup_norm, replacement_call_setup_norm)

    if target_invite_options_norm not in content_norm:
        print("Error: Target inviteOptions block was not found in the file.")
        return 1
    content_norm = content_norm.replace(target_invite_options_norm, replacement_invite_options_norm)

    # Keep original file line endings (detect if it used CRLF)
    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("Success: sip-phone.js has been successfully updated with early media support and additional SIP error mappings.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
