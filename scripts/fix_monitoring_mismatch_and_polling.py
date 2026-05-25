import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")
    index_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")

    print(f"Modifying PHP library file: {php_file}")
    print(f"Modifying index controller file: {index_file}")
    print(f"Modifying template file: {tpl_file}")

    # 1. Modify modules/agent_console/libs/paloSantoConsola.class.php
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    # Change esperarEventoSesionActiva definition to accept $timeout
    old_esperar = (
        "    function esperarEventoSesionActiva()\n"
        "    {\n"
        "        $this->errMsg = '';\n"
        "        try {\n"
        "            $oECCP = $this->_obtenerConexion('ECCP');\n"
        "            $oECCP->wait_response(30);"
    )
    new_esperar = (
        "    function esperarEventoSesionActiva($timeout = 30)\n"
        "    {\n"
        "        $this->errMsg = '';\n"
        "        try {\n"
        "            $oECCP = $this->_obtenerConexion('ECCP');\n"
        "            $oECCP->wait_response($timeout);"
    )

    if old_esperar in php_content_norm:
        php_content_norm = php_content_norm.replace(old_esperar, new_esperar)
        print("Success: Updated esperarEventoSesionActiva in paloSantoConsola.class.php")
    else:
        if "esperarEventoSesionActiva($timeout = 30)" in php_content_norm:
            print("Notice: esperarEventoSesionActiva already updated")
        else:
            print("Error: esperarEventoSesionActiva target block not found")
            return 1

    # Change helper methods to public
    old_helpers_private = (
        "    private function _obtenerCanalesActivosAsterisk()\n"
    )
    new_helpers_public = (
        "    public function _obtenerCanalesActivosAsterisk()\n"
    )

    if old_helpers_private in php_content_norm:
        php_content_norm = php_content_norm.replace(old_helpers_private, new_helpers_public)
        print("Success: Changed _obtenerCanalesActivosAsterisk to public")

    old_detectar_private = (
        "    private function _detectarLlamadaActivaAgente($agent, $activeChannels)\n"
    )
    new_detectar_public = (
        "    public function _detectarLlamadaActivaAgente($agent, $activeChannels)\n"
    )

    if old_detectar_private in php_content_norm:
        php_content_norm = php_content_norm.replace(old_detectar_private, new_detectar_public)
        print("Success: Changed _detectarLlamadaActivaAgente to public")

    # Restore newlines for php file
    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)


    # 2. Modify modules/campaign_monitoring/index.php
    if not os.path.exists(index_file):
        print(f"Error: index.php not found at {index_file}")
        return 1

    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()

    index_content_norm = index_content.replace('\r\n', '\n')

    # Update loop call to esperarEventoSesionActiva and inject checkStatus logic
    old_loop_block = (
        "            session_commit();\n"
        "            $listaEventos = $oPaloConsola->esperarEventoSesionActiva();\n"
        "            if (is_null($listaEventos)) {\n"
        "                $respuesta['error'] = $oPaloConsola->errMsg;\n"
        "                jsonflush($bSSE, $respuesta);\n"
        "                $oPaloConsola->desconectarTodo();\n"
        "                return;\n"
        "            }\n"
        "            @session_start();"
    )
    new_loop_block = (
        "            session_commit();\n"
        "            $iTiempoRestante = $iTimeoutPoll - (time() - $iTimestampInicio);\n"
        "            $waitTimeout = min($iTiempoRestante, 3);\n"
        "            if ($waitTimeout <= 0) $waitTimeout = 1;\n"
        "            $listaEventos = $oPaloConsola->esperarEventoSesionActiva($waitTimeout);\n"
        "            if (is_null($listaEventos)) {\n"
        "                $respuesta['error'] = $oPaloConsola->errMsg;\n"
        "                jsonflush($bSSE, $respuesta);\n"
        "                $oPaloConsola->desconectarTodo();\n"
        "                return;\n"
        "            }\n"
        "            @session_start();"
    )

    if old_loop_block in index_content_norm:
        index_content_norm = index_content_norm.replace(old_loop_block, new_loop_block)
        print("Success: Updated loop block in index.php")
    else:
        if "esperarEventoSesionActiva($waitTimeout)" in index_content_norm:
            print("Notice: index.php loop block already updated")
        else:
            print("Error: index.php loop block target not found")
            return 1

    # Inject periodic active state check right after event processing
    old_event_end = (
        "            foreach ($listaEventos as $evento) {\n"
        "                $sCanalAgente = isset($evento['agent_number']) ? $evento['agent_number'] : NULL;\n"
        "                switch ($evento['event']) {\n"
    )
    # Let's find the end of the foreach loop.
    # Lines 741-746 in our view:
    # 741:                     }
    # 742:                     break;
    # 743:                 }
    # 744:             }
    # 745:         }

    target_loop_end = (
        "            foreach ($listaEventos as $evento) {\n"
        "                $sCanalAgente = isset($evento['agent_number']) ? $evento['agent_number'] : NULL;\n"
        "                switch ($evento['event']) {\n"
    )

    # Let's do a more robust search and replace for the end of loop.
    # Specifically, before the closing brace of `while (connection_status() == ...)`
    # The end of the while loop in index.php:
    #             }
    #         }
    #     }
    #     $estadoHash = generarEstadoHash($module_name, $estadoCliente);

    target_while_end = (
        "            }\n"
        "        }\n"
        "    }\n"
        "\n"
        "    $estadoHash = generarEstadoHash($module_name, $estadoCliente);"
    )
    replace_while_end = (
        "            }\n"
        "\n"
        "            // Periodically check current server state (including Asterisk manual calls)\n"
        "            $estadoCampania = $oPaloConsola->leerEstadoCampania($estadoCliente['campaigntype'], $estadoCliente['campaignid']);\n"
        "            if (is_array($estadoCampania)) {\n"
        "                foreach (array_keys($estadoCliente['agents']) as $k) {\n"
        "                    if (!isset($estadoCampania['agents'][$k])) {\n"
        "                        $respuesta['agents']['remove'][] = array('agent' => $estadoCliente['agents'][$k]['agentchannel']);\n"
        "                        unset($estadoCliente['agents'][$k]);\n"
        "                    } elseif ($estadoCliente['agents'][$k] != $estadoCampania['agents'][$k]) {\n"
        "                        $respuesta['agents']['update'][] = formatoAgente($estadoCampania['agents'][$k]);\n"
        "                        $estadoCliente['agents'][$k] = $estadoCampania['agents'][$k];\n"
        "                    }\n"
        "                }\n"
        "                foreach (array_keys($estadoCampania['agents']) as $k) {\n"
        "                    if (!isset($estadoCliente['agents'][$k])) {\n"
        "                        $respuesta['agents']['add'][] = formatoAgente($estadoCampania['agents'][$k]);\n"
        "                        $estadoCliente['agents'][$k] = $estadoCampania['agents'][$k];\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "\n"
        "    $estadoHash = generarEstadoHash($module_name, $estadoCliente);"
    )

    if target_while_end in index_content_norm:
        index_content_norm = index_content_norm.replace(target_while_end, replace_while_end)
        print("Success: Injected active check inside checkStatus loop in index.php")
    else:
        if "check current server state (including Asterisk manual calls)" in index_content_norm:
            print("Notice: checkStatus loop check already injected")
        else:
            print("Error: checkStatus loop target not found")
            return 1

    # Restore newlines for index file
    if '\r\n' in index_content:
        index_content_norm = index_content_norm.replace('\n', '\r\n')

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content_norm)


    # 3. Modify modules/campaign_monitoring/themes/default/informacion_campania.tpl
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1

    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    # Replace the cell class=trAgent to have width=20% and wrapping div
    old_tpl_td = (
        "                    <td class=\"trAgent\"nowrap=\"nowrap\">{{image}}{{estado}}</td>"
    )
    new_tpl_td = (
        "                    <td width=\"20%\" nowrap=\"nowrap\"><div class=\"trAgent\">{{image}}{{estado}}</div></td>"
    )

    if old_tpl_td in tpl_content_norm:
        tpl_content_norm = tpl_content_norm.replace(old_tpl_td, new_tpl_td)
        print("Success: Fixed trAgent cell in informacion_campania.tpl")
    else:
        if "div class=\"trAgent\"" in tpl_content_norm:
            print("Notice: trAgent cell already updated in template")
        else:
            print("Error: trAgent cell target not found in template")
            return 1

    # Restore newlines for template file
    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)

    print("All fixes applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
