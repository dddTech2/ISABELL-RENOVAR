import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")
    index_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")

    print(f"Modifying PHP library file: {php_file}")
    print(f"Modifying index controller file: {index_file}")

    # 1. Modify modules/agent_console/libs/paloSantoConsola.class.php
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    # We will normalize line endings to perform replacement safely
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
        print("Success: Updated esperarEventoSesionActiva signature in paloSantoConsola.class.php")
    else:
        if "esperarEventoSesionActiva($timeout = 30)" in php_content_norm:
            print("Notice: esperarEventoSesionActiva already updated in paloSantoConsola.class.php")
        else:
            print("Error: esperarEventoSesionActiva target block not found in paloSantoConsola.class.php")
            return 1

    # Change helper methods to public
    old_helpers_private = "    private function _obtenerCanalesActivosAsterisk()"
    new_helpers_public = "    public function _obtenerCanalesActivosAsterisk()"
    if old_helpers_private in php_content_norm:
        php_content_norm = php_content_norm.replace(old_helpers_private, new_helpers_public)
        print("Success: Changed _obtenerCanalesActivosAsterisk to public")

    old_detectar_private = "    private function _detectarLlamadaActivaAgente($agent, $activeChannels)"
    new_detectar_public = "    public function _detectarLlamadaActivaAgente($agent, $activeChannels)"
    if old_detectar_private in php_content_norm:
        php_content_norm = php_content_norm.replace(old_detectar_private, new_detectar_public)
        print("Success: Changed _detectarLlamadaActivaAgente to public")

    # Save php file preserving original line endings
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

    # Update loop call to esperarEventoSesionActiva
    old_loop_block = (
        "            session_commit();\n"
        "            $listaEventos = $oPaloConsola->esperarEventoSesionActiva();\n"
        "            if (is_null($listaEventos)) {"
    )
    new_loop_block = (
        "            session_commit();\n"
        "            $iTiempoRestante = $iTimeoutPoll - (time() - $iTimestampInicio);\n"
        "            $waitTimeout = min($iTiempoRestante, 3);\n"
        "            if ($waitTimeout <= 0) $waitTimeout = 1;\n"
        "            $listaEventos = $oPaloConsola->esperarEventoSesionActiva($waitTimeout);\n"
        "            if (is_null($listaEventos)) {"
    )

    if old_loop_block in index_content_norm:
        index_content_norm = index_content_norm.replace(old_loop_block, new_loop_block)
        print("Success: Updated loop wait_response timeout in index.php")
    else:
        if "esperarEventoSesionActiva($waitTimeout)" in index_content_norm:
            print("Notice: index.php wait_response timeout already updated")
        else:
            print("Error: index.php wait_response target block not found")
            return 1

    # Inject periodic active state check right after event processing
    # The end of the foreach loop is:
    #             foreach ($listaEventos as $evento) {
    #                 ...
    #             }
    #         }
    # 
    # Let's find exactly the block containing the end of the foreach loop.
    old_end_of_events = (
        "                }\n"
        "            }\n"
        "        }\n"
        "\n"
        "        $estadoHash = generarEstadoHash($module_name, $estadoCliente);"
    )

    new_end_of_events = (
        "                }\n"
        "            }\n"
        "\n"
        "            // Periodically check current server state (including Asterisk manual calls)\n"
        "            $estadoCampania = $oPaloConsola->leerEstadoCampania($estadoCliente['campaigntype'], $estadoCliente['campaignid']);\n"
        "            if (is_array($estadoCampania)) {\n"
        "                // Filter out offline agents with unregistered extensions\n"
        "                foreach ($estadoCampania['agents'] as $k_off => $agent_off) {\n"
        "                    if ($agent_off['status'] == 'offline' && !$oPaloConsola->extensionEstaRegistrada($agent_off['agentchannel'])) {\n"
        "                        unset($estadoCampania['agents'][$k_off]);\n"
        "                    }\n"
        "                }\n"
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
        "\n"
        "        $estadoHash = generarEstadoHash($module_name, $estadoCliente);"
    )

    if old_end_of_events in index_content_norm:
        index_content_norm = index_content_norm.replace(old_end_of_events, new_end_of_events)
        print("Success: Injected active state check in index.php")
    else:
        if "Periodically check current server state (including Asterisk manual calls)" in index_content_norm:
            print("Notice: Active state check already injected in index.php")
        else:
            print("Error: Active state check target block not found in index.php")
            return 1

    # Save index file preserving original line endings
    if '\r\n' in index_content:
        index_content_norm = index_content_norm.replace('\n', '\r\n')

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content_norm)

    print("All polling changes applied successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
