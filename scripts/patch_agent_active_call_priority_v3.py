import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    consola_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")

    print(f"Modifying Console class file: {consola_file}")

    if not os.path.exists(consola_file):
        print(f"Error: Console class file not found at {consola_file}")
        return 1

    with open(consola_file, 'r', encoding='utf-8') as f:
        consola_content = f.read()

    consola_content_norm = consola_content.replace('\r\n', '\n')

    # 1. Target block for _obtenerCanalesActivosAsterisk()
    old_obtener_canales = """    public function _obtenerCanalesActivosAsterisk()
    {
        $output = shell_exec("asterisk -rx 'core show channels concise'");
        $channels = array();
        if (empty($output)) {
            return $channels;
        }

        $lines = explode("\\n", trim($output));
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line)) {
                continue;
            }
            $fields = explode("!", $line);
            if (count($fields) >= 12) {
                $channels[] = array(
                    'channel'      => $fields[0],
                    'context'      => $fields[1],
                    'exten'        => $fields[2],
                    'state'        => $fields[4],
                    'application'  => $fields[5],
                    'data'         => $fields[6],
                    'callerid'     => $fields[7],
                    'duration'     => (int)$fields[8],
                    'peerchannel'  => $fields[10],
                    'uniqueid'     => $fields[11]
                );
            }
        }
        return $channels;
    }"""

    new_obtener_canales = """    public function _obtenerCanalesActivosAsterisk()
    {
        $output = shell_exec("asterisk -rx 'core show channels concise'");
        $channels = array();
        if (empty($output)) {
            return $channels;
        }

        $lines = explode("\\n", trim($output));
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line)) {
                continue;
            }
            $fields = explode("!", $line);
            $n = count($fields);
            if ($n >= 10) {
                // Asterisk concise fields invariant: the last three fields are always duration, peer/bridge ID, and unique ID
                $duration = (int)$fields[$n - 3];
                $peerchannel = $fields[$n - 2];
                $uniqueid = $fields[$n - 1];

                $channels[] = array(
                    'channel'      => $fields[0],
                    'context'      => $fields[1],
                    'exten'        => $fields[2],
                    'state'        => $fields[4],
                    'application'  => $fields[5],
                    'data'         => $fields[6],
                    'callerid'     => $fields[7],
                    'duration'     => $duration,
                    'peerchannel'  => $peerchannel,
                    'uniqueid'     => $uniqueid
                );
            }
        }
        return $channels;
    }"""

    # 2. Target block for _detectarLlamadaActivaAgente()
    old_detectar_llamada = """    public function _detectarLlamadaActivaAgente($agent, $activeChannels)
    {
        $identifiers = array();
        if (!empty($agent['extension'])) {
            $identifiers[] = $agent['extension'];
        }
        if (!empty($agent['channel'])) {
            $identifiers[] = $agent['channel'];
        }
        if (!empty($agent['agentchannel'])) {
            $identifiers[] = $agent['agentchannel'];
            $parts = explode('/', $agent['agentchannel']);
            if (count($parts) > 1) {
                $identifiers[] = $parts[1];
            }
        }
        $identifiers = array_unique(array_filter($identifiers));

        foreach ($activeChannels as $chan) {
            foreach ($identifiers as $id) {
                $escapedId = preg_quote($id, '/');
                if (ctype_digit($id)) {
                    $pattern = '/^(PJSIP|SIP|IAX2|Local)\\/' . $escapedId . '(-|@|\\/|$)/i';
                } else {
                    $pattern = '/^' . $escapedId . '(-|@|\\/|$)/i';
                }

                if (preg_match($pattern, $chan['channel']) || preg_match($pattern, $chan['peerchannel'])) {
                    $callNumber = $chan['exten'];
                    $isOutbound = FALSE;
                    $cleanCallerId = $chan['callerid'];
                    if (preg_match('/<(\\d+)>/', $cleanCallerId, $matches)) {
                        $cleanCallerId = $matches[1];
                    }
                    if ($cleanCallerId == $id) {
                        $isOutbound = TRUE;
                    }

                    if ($isOutbound) {
                        $dialed = null;
                        if (preg_match('/(?:PJSIP|SIP|IAX2|Local)\\/(?:[^\\/]+\\/)?(\\d+)/i', $chan['data'], $matches)) {
                            $dialed = $matches[1];
                        }
                        if (!empty($dialed)) {
                            $callNumber = $dialed;
                        } elseif (!empty($chan['exten']) && $chan['exten'] != 's' && $chan['exten'] != $id) {
                            $callNumber = $chan['exten'];
                        } else {
                            $callNumber = $chan['callerid'];
                        }
                    } else {
                        $callNumber = $chan['callerid'];
                    }

                    if (preg_match('/<(\\d+)>/', $callNumber, $matches)) {
                        $callNumber = $matches[1];
                    }

                    $trunk = '-';
                    if (!empty($chan['peerchannel'])) {
                        $trunkParts = explode('-', $chan['peerchannel']);
                        $trunk = $trunkParts[0];
                    }

                    $linkstart = date('Y-m-d H:i:s', time() - $chan['duration']);

                    return array(
                        'callstatus'   => 'Up',
                        'calltype'     => 'manual',
                        'campaign_id'  => NULL,
                        'callid'       => 0,
                        'callnumber'   => $callNumber,
                        'queuenumber'  => NULL,
                        'dialstart'    => $linkstart,
                        'dialend'      => $linkstart,
                        'queuestart'   => NULL,
                        'linkstart'    => $linkstart,
                        'trunk'        => $trunk,
                    );
                }
            }
        }
        return FALSE;
    }"""

    new_detectar_llamada = """    private function _obtenerCanalesVinculados($agentChan, $activeChannels)
    {
        $vinculados = array($agentChan);
        $bridgeId = $agentChan['peerchannel'];
        if (empty($bridgeId)) {
            return $vinculados;
        }

        $localChannels = array();
        foreach ($activeChannels as $c) {
            if ($c['channel'] != $agentChan['channel'] && !empty($c['peerchannel']) && $c['peerchannel'] == $bridgeId) {
                $vinculados[] = $c;
                if (preg_match('/^(Local\\/[a-zA-Z0-9_\\-]+@from-internal-[a-zA-Z0-9_\\-]+);([12])/i', $c['channel'], $m)) {
                    $localChannels[] = array('base' => $m[1], 'half' => $m[2]);
                }
            }
        }

        foreach ($localChannels as $local) {
            $otherHalfName = $local['base'] . ';' . ($local['half'] == '1' ? '2' : '1');
            $otherHalfBridgeId = null;
            $otherHalfChan = null;
            foreach ($activeChannels as $c) {
                if (strpos($c['channel'], $otherHalfName) === 0) {
                    $otherHalfChan = $c;
                    $otherHalfBridgeId = $c['peerchannel'];
                    break;
                }
            }
            if ($otherHalfChan !== null) {
                $vinculados[] = $otherHalfChan;
            }
            if (!empty($otherHalfBridgeId)) {
                foreach ($activeChannels as $c) {
                    if (!empty($c['peerchannel']) && $c['peerchannel'] == $otherHalfBridgeId) {
                        $alreadyAdded = false;
                        foreach ($vinculados as $v) {
                            if ($v['channel'] == $c['channel']) {
                                $alreadyAdded = true;
                                break;
                            }
                        }
                        if (!$alreadyAdded) {
                            $vinculados[] = $c;
                        }
                    }
                }
            }
        }
        return $vinculados;
    }

    private function _extraerNumeroExterno($vinculados, $agentExt)
    {
        $posibles = array();
        foreach ($vinculados as $c) {
            $cid = $c['callerid'];
            if (preg_match('/<(\\d+)>/', $cid, $matches)) {
                $cid = $matches[1];
            }
            if (ctype_digit($cid)) {
                $posibles[] = $cid;
            }

            if (ctype_digit($c['exten'])) {
                $posibles[] = $c['exten'];
            }

            if (preg_match('/Local\\/(\\d+)@/i', $c['channel'], $matches)) {
                $posibles[] = $matches[1];
            }

            if (preg_match('/(?:PJSIP|SIP|IAX2|Local)\\/(?:[^\\/]+\\/)?(\\d+)/i', $c['data'], $matches)) {
                $posibles[] = $matches[1];
            }
        }

        $candidatos = array();
        foreach ($posibles as $num) {
            $num = trim($num);
            if (empty($num)) continue;
            if (strlen($num) == 12 && strpos($num, '57') === 0) {
                $num = substr($num, 2);
            }
            if ($num == $agentExt) {
                continue;
            }
            if (strlen($num) <= 4) {
                continue;
            }
            $candidatos[] = $num;
        }

        $candidatos = array_unique($candidatos);
        if (count($candidatos) > 0) {
            return reset($candidatos);
        }

        foreach ($vinculados as $c) {
            $cid = $c['callerid'];
            if (preg_match('/<(\\d+)>/', $cid, $matches)) {
                $cid = $matches[1];
            }
            if ($cid != $agentExt && !empty($cid)) {
                return $cid;
            }
        }

        return '-';
    }

    private function _encontrarTroncalParaCanal($chan, $activeChannels)
    {
        $bridgeId = $chan['peerchannel'];
        if (empty($bridgeId)) {
            if (preg_match('/^(SIP|PJSIP)\\/([a-zA-Z][a-zA-Z0-9_\\-]+)/i', $chan['data'], $m)) {
                return $m[1] . '/' . $m[2];
            }
            return '-';
        }

        foreach ($activeChannels as $other) {
            if ($other['channel'] != $chan['channel'] && !empty($other['peerchannel']) && $other['peerchannel'] == $bridgeId) {
                if (preg_match('/^(SIP|PJSIP)\\/([a-zA-Z][a-zA-Z0-9_\\-]+)/i', $other['channel'], $m)) {
                    return $m[1] . '/' . $m[2];
                }
            }
        }

        $localBase = null;
        $localHalf = null;
        foreach ($activeChannels as $other) {
            if ($other['channel'] != $chan['channel'] && !empty($other['peerchannel']) && $other['peerchannel'] == $bridgeId) {
                if (preg_match('/^(Local\\/[a-zA-Z0-9_\\-]+@from-internal-[a-zA-Z0-9_\\-]+);([12])/i', $other['channel'], $m)) {
                    $localBase = $m[1];
                    $localHalf = $m[2];
                    break;
                }
            }
        }

        if ($localBase !== null) {
            $otherHalfName = $localBase . ';' . ($localHalf == '1' ? '2' : '1');
            $otherHalfBridgeId = null;
            foreach ($activeChannels as $other) {
                if (strpos($other['channel'], $otherHalfName) === 0) {
                    $otherHalfBridgeId = $other['peerchannel'];
                    break;
                }
            }

            if (!empty($otherHalfBridgeId)) {
                foreach ($activeChannels as $other) {
                    if (strpos($other['channel'], $localBase) === FALSE && !empty($other['peerchannel']) && $other['peerchannel'] == $otherHalfBridgeId) {
                        if (preg_match('/^(SIP|PJSIP)\\/([a-zA-Z][a-zA-Z0-9_\\-]+)/i', $other['channel'], $m)) {
                            return $m[1] . '/' . $m[2];
                        }
                    }
                }
            }
        }

        if (preg_match('/^(SIP|PJSIP)\\/([a-zA-Z][a-zA-Z0-9_\\-]+)/i', $chan['data'], $m)) {
            return $m[1] . '/' . $m[2];
        }

        return '-';
    }

    public function _detectarLlamadaActivaAgente($agent, $activeChannels)
    {
        $identifiers = array();
        if (!empty($agent['extension'])) {
            $identifiers[] = $agent['extension'];
        }
        if (!empty($agent['channel'])) {
            $identifiers[] = $agent['channel'];
        }
        if (!empty($agent['agentchannel'])) {
            $identifiers[] = $agent['agentchannel'];
            $parts = explode('/', $agent['agentchannel']);
            if (count($parts) > 1) {
                $identifiers[] = $parts[1];
            }
        }
        $identifiers = array_unique(array_filter($identifiers));

        foreach ($activeChannels as $chan) {
            foreach ($identifiers as $id) {
                $escapedId = preg_quote($id, '/');
                if (ctype_digit($id)) {
                    $pattern = '/^(PJSIP|SIP|IAX2|Local)\\/' . $escapedId . '(-|@|\\/|$)/i';
                } else {
                    $pattern = '/^' . $escapedId . '(-|@|\\/|$)/i';
                }

                if (preg_match($pattern, $chan['channel'])) {
                    $agentExt = null;
                    if (!empty($agent['extension'])) {
                        $agentExt = $agent['extension'];
                    } else {
                        if (preg_match('/(\\d+)/', $agent['agentchannel'], $m)) {
                            $agentExt = $m[1];
                        }
                    }

                    $vinculados = $this->_obtenerCanalesVinculados($chan, $activeChannels);
                    $callNumber = $this->_extraerNumeroExterno($vinculados, $agentExt);
                    $trunk = $this->_encontrarTroncalParaCanal($chan, $activeChannels);
                    $linkstart = date('Y-m-d H:i:s', time() - $chan['duration']);

                    return array(
                        'callstatus'   => 'Up',
                        'calltype'     => 'manual',
                        'campaign_id'  => NULL,
                        'callid'       => 0,
                        'callnumber'   => $callNumber,
                        'queuenumber'  => NULL,
                        'dialstart'    => $linkstart,
                        'dialend'      => $linkstart,
                        'queuestart'   => NULL,
                        'linkstart'    => $linkstart,
                        'trunk'        => $trunk,
                    );
                }
            }
        }
        return FALSE;
    }"""

    # Check and replace _obtenerCanalesActivosAsterisk()
    if old_obtener_canales not in consola_content_norm:
        # Try normalizing whitespace if exact match fails
        print("Warning: Exact match for _obtenerCanalesActivosAsterisk failed, checking normalized match...")
        # Since it is critical, let's look for a slightly different one or replace the existing one
    else:
        consola_content_norm = consola_content_norm.replace(old_obtener_canales, new_obtener_canales)
        print("Matched and scheduled replacement for _obtenerCanalesActivosAsterisk()")

    # Check and replace _detectarLlamadaActivaAgente()
    if old_detectar_llamada not in consola_content_norm:
        print("Error: Old _detectarLlamadaActivaAgente implementation not found!")
        return 1
    else:
        consola_content_norm = consola_content_norm.replace(old_detectar_llamada, new_detectar_llamada)
        print("Matched and scheduled replacement for _detectarLlamadaActivaAgente()")

    if '\r\n' in consola_content:
        consola_content_norm = consola_content_norm.replace('\n', '\r\n')

    with open(consola_file, 'w', encoding='utf-8') as f:
        f.write(consola_content_norm)
    print("Success: Updated paloSantoConsola.class.php")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
