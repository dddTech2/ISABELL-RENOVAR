import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")

    print(f"Modifying PHP file: {php_file}")

    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines
    content_norm = content.replace('\r\n', '\n')

    # 1. Modify leerEstadoCampania to inject check for manual calls
    target_block = (
        "            if (!isset($reporte['statuscount']['finished'])) {\n"
        "                $reporte['statuscount']['finished'] = $reporte['statuscount']['success'] - $iNumLlamadasAtendidas;\n"
        "                ksort($reporte['statuscount']);\n"
        "            }\n"
        "            return $reporte;"
    )

    replace_block = (
        "            if (!isset($reporte['statuscount']['finished'])) {\n"
        "                $reporte['statuscount']['finished'] = $reporte['statuscount']['success'] - $iNumLlamadasAtendidas;\n"
        "                ksort($reporte['statuscount']);\n"
        "            }\n"
        "\n"
        "            // Check Asterisk active channels to detect agents in manual/non-dialer calls\n"
        "            if (!empty($reporte['agents'])) {\n"
        "                $activeChannels = $this->_obtenerCanalesActivosAsterisk();\n"
        "                foreach ($reporte['agents'] as $sAgente => &$agent) {\n"
        "                    if ($agent['status'] == 'oncall') {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if ($agent['status'] == 'online' || $agent['status'] == 'paused') {\n"
        "                        $callInfo = $this->_detectarLlamadaActivaAgente($agent, $activeChannels);\n"
        "                        if ($callInfo !== FALSE) {\n"
        "                            $agent['status'] = 'oncall';\n"
        "                            $agent['callinfo'] = $callInfo;\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "\n"
        "            return $reporte;"
    )

    if target_block not in content_norm:
        if "Check Asterisk active channels to detect agents" in content_norm:
            print("Notice: check logic already inserted in leerEstadoCampania")
        else:
            print("Error: Target block not found in leerEstadoCampania")
            return 1
    else:
        content_norm = content_norm.replace(target_block, replace_block)
        print("Success: Injected manual call check in leerEstadoCampania")

    # 2. Append helper methods before the class closing brace
    # Find the last closing brace of the PaloSantoConsola class
    # The file ends with the pingAgente method followed by the class closing brace.
    ping_agente_method = (
        "    function pingAgente()\n"
        "    {\n"
        "        try {\n"
        "            $oECCP = $this->_obtenerConexion('ECCP');\n"
        "            $oECCP->pingagent();\n"
        "            return TRUE;\n"
        "        } catch (Exception $e) {\n"
        "            $this->errMsg = '(internal) pingagent: '.$e->getMessage();\n"
        "            return FALSE;\n"
        "        }\n"
        "    }"
    )

    if ping_agente_method not in content_norm:
        print("Error: pingAgente method target not found at the end of class")
        return 1

    helper_methods = (
        "\n"
        "    private function _obtenerCanalesActivosAsterisk()\n"
        "    {\n"
        "        $output = shell_exec(\"asterisk -rx 'core show channels concise'\");\n"
        "        $channels = array();\n"
        "        if (empty($output)) {\n"
        "            return $channels;\n"
        "        }\n"
        "\n"
        "        $lines = explode(\"\\n\", trim($output));\n"
        "        foreach ($lines as $line) {\n"
        "            $line = trim($line);\n"
        "            if (empty($line)) {\n"
        "                continue;\n"
        "            }\n"
        "            $fields = explode(\"!\", $line);\n"
        "            if (count($fields) >= 12) {\n"
        "                $channels[] = array(\n"
        "                    'channel'      => $fields[0],\n"
        "                    'context'      => $fields[1],\n"
        "                    'exten'        => $fields[2],\n"
        "                    'state'        => $fields[4],\n"
        "                    'application'  => $fields[5],\n"
        "                    'data'         => $fields[6],\n"
        "                    'callerid'     => $fields[7],\n"
        "                    'duration'     => (int)$fields[8],\n"
        "                    'peerchannel'  => $fields[10],\n"
        "                    'uniqueid'     => $fields[11]\n"
        "                );\n"
        "            }\n"
        "        }\n"
        "        return $channels;\n"
        "    }\n"
        "\n"
        "    private function _detectarLlamadaActivaAgente($agent, $activeChannels)\n"
        "    {\n"
        "        $identifiers = array();\n"
        "        if (!empty($agent['extension'])) {\n"
        "            $identifiers[] = $agent['extension'];\n"
        "        }\n"
        "        if (!empty($agent['channel'])) {\n"
        "            $identifiers[] = $agent['channel'];\n"
        "        }\n"
        "        if (!empty($agent['agentchannel'])) {\n"
        "            $identifiers[] = $agent['agentchannel'];\n"
        "            $parts = explode('/', $agent['agentchannel']);\n"
        "            if (count($parts) > 1) {\n"
        "                $identifiers[] = $parts[1];\n"
        "            }\n"
        "        }\n"
        "        $identifiers = array_unique(array_filter($identifiers));\n"
        "\n"
        "        foreach ($activeChannels as $chan) {\n"
        "            foreach ($identifiers as $id) {\n"
        "                $escapedId = preg_quote($id, '/');\n"
        "                if (ctype_digit($id)) {\n"
        "                    $pattern = '/^(PJSIP|SIP|IAX2|Local)\\/' . $escapedId . '(-|@|\\/|$)/i';\n"
        "                } else {\n"
        "                    $pattern = '/^' . $escapedId . '(-|@|\\/|$)/i';\n"
        "                }\n"
        "\n"
        "                if (preg_match($pattern, $chan['channel']) || preg_match($pattern, $chan['peerchannel'])) {\n"
        "                    $callNumber = $chan['exten'];\n"
        "                    if (empty($callNumber) || $callNumber == 's') {\n"
        "                        $callNumber = $chan['callerid'];\n"
        "                    }\n"
        "                    if (preg_match('/<(\\d+)>/', $callNumber, $matches)) {\n"
        "                        $callNumber = $matches[1];\n"
        "                    }\n"
        "\n"
        "                    $trunk = '-';\n"
        "                    if (!empty($chan['peerchannel'])) {\n"
        "                        $trunkParts = explode('-', $chan['peerchannel']);\n"
        "                        $trunk = $trunkParts[0];\n"
        "                    }\n"
        "\n"
        "                    $linkstart = date('Y-m-d H:i:s', time() - $chan['duration']);\n"
        "\n"
        "                    return array(\n"
        "                        'callstatus'   => 'Up',\n"
        "                        'calltype'     => 'manual',\n"
        "                        'campaign_id'  => NULL,\n"
        "                        'callid'       => 0,\n"
        "                        'callnumber'   => $callNumber,\n"
        "                        'queuenumber'  => NULL,\n"
        "                        'dialstart'    => $linkstart,\n"
        "                        'dialend'      => $linkstart,\n"
        "                        'queuestart'   => NULL,\n"
        "                        'linkstart'    => $linkstart,\n"
        "                        'trunk'        => $trunk,\n"
        "                    );\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "        return FALSE;\n"
        "    }\n"
    )

    if "function _obtenerCanalesActivosAsterisk" in content_norm:
        print("Notice: Helper methods already present in paloSantoConsola.class.php")
    else:
        replace_ping_method = ping_agente_method + "\n" + helper_methods
        content_norm = content_norm.replace(ping_agente_method, replace_ping_method)
        print("Success: Added helper methods to paloSantoConsola.class.php")

    # Restore original newlines if necessary
    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("All updates to paloSantoConsola.class.php completed successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
