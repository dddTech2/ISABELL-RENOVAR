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

    # Target block to replace (normalizing spacing and line endings just in case)
    target_block = (
        "    function attachMedia() {\n"
        "        if (!currentSession) return;\n"
        "\n"
        "        var pc = currentSession.sessionDescriptionHandler.peerConnection;\n"
        "        if (!pc) {\n"
        "            log('No peerConnection available');\n"
        "            return;\n"
        "        }\n"
        "\n"
        "        // Get remote stream\n"
        "        var remoteStream = new MediaStream();\n"
        "        pc.getReceivers().forEach(function(receiver) {\n"
        "            if (receiver.track) {\n"
        "                remoteStream.addTrack(receiver.track);\n"
        "            }\n"
        "        });\n"
        "\n"
        "        audioElements.remote.srcObject = remoteStream;\n"
        "        audioElements.remote.play().catch(function(e) {\n"
        "            log('Audio play failed: ' + e.message);\n"
        "        });\n"
        "\n"
        "        log('Remote media attached');\n"
        "    }"
    )

    replacement_block = (
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

    # Normalize line endings to avoid mismatch issues
    content_norm = content.replace('\r\n', '\n')
    target_norm = target_block.replace('\r\n', '\n')
    replacement_norm = replacement_block.replace('\r\n', '\n')

    if target_norm not in content_norm:
        print("Error: Target attachMedia block was not found in the file.")
        return 1

    content_modified = content_norm.replace(target_norm, replacement_norm)

    # Keep original file line endings (detect if it used CRLF)
    if '\r\n' in content:
        content_modified = content_modified.replace('\n', '\r\n')

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content_modified)

    print("Success: sip-phone.js has been successfully updated.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
