import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")
    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")
    css_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "css", "styles.css")

    print(f"Modifying PHP file: {php_file}")
    print(f"Modifying template file: {tpl_file}")
    print(f"Modifying JS file: {js_file}")
    print(f"Modifying CSS file: {css_file}")

    # 1. Modify PHP file
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    # Add forceLoginAgent to switch
    php_switch_target = (
        "    switch (getParameter('action')) {\n"
        "    case 'forceUnbreakAgent':\n"
        "        $sContenido = manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;"
    )
    php_switch_replace = (
        "    switch (getParameter('action')) {\n"
        "    case 'forceUnbreakAgent':\n"
        "        $sContenido = manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;\n"
        "    case 'forceLoginAgent':\n"
        "        $sContenido = manejarMonitoreo_forceLoginAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;"
    )

    if php_switch_target not in php_content_norm:
        print("Error: PHP switch target not found")
        return 1
    php_content_norm = php_content_norm.replace(php_switch_target, php_switch_replace)

    # Add filtering to getCampaignDetail
    php_detail_target = (
        "        if ($respuesta['status'] == 'success') {\n"
        "            $estadoCampania = $oPaloConsola->leerEstadoCampania($sTipoCampania, $sIdCampania);\n"
        "            if (!is_array($estadoCampania)) {\n"
        "                $respuesta['status'] = 'error';\n"
        "                $respuesta['message'] = $oPaloConsola->errMsg;\n"
        "            }\n"
        "        }"
    )
    php_detail_replace = (
        "        if ($respuesta['status'] == 'success') {\n"
        "            $estadoCampania = $oPaloConsola->leerEstadoCampania($sTipoCampania, $sIdCampania);\n"
        "            if (!is_array($estadoCampania)) {\n"
        "                $respuesta['status'] = 'error';\n"
        "                $respuesta['message'] = $oPaloConsola->errMsg;\n"
        "            } else {\n"
        "                // Filter out offline agents with unregistered extensions\n"
        "                foreach ($estadoCampania['agents'] as $k => $agent) {\n"
        "                    if ($agent['status'] == 'offline' && !$oPaloConsola->extensionEstaRegistrada($agent['agentchannel'])) {\n"
        "                        unset($estadoCampania['agents'][$k]);\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }"
    )

    if php_detail_target not in php_content_norm:
        print("Error: PHP getCampaignDetail target not found")
        return 1
    php_content_norm = php_content_norm.replace(php_detail_target, php_detail_replace)

    # Add filtering to checkStatus
    php_status_target = (
        "    // Estado del lado del servidor\n"
        "    $estadoCampania = $oPaloConsola->leerEstadoCampania($estadoCliente['campaigntype'], $estadoCliente['campaignid']);\n"
        "    if (!is_array($estadoCampania)) {\n"
        "        $respuesta['error'] = $oPaloConsola->errMsg;\n"
        "        jsonflush($bSSE, $respuesta);\n"
        "        $oPaloConsola->desconectarTodo();\n"
        "        return;\n"
        "    }"
    )
    php_status_replace = (
        "    // Estado del lado del servidor\n"
        "    $estadoCampania = $oPaloConsola->leerEstadoCampania($estadoCliente['campaigntype'], $estadoCliente['campaignid']);\n"
        "    if (!is_array($estadoCampania)) {\n"
        "        $respuesta['error'] = $oPaloConsola->errMsg;\n"
        "        jsonflush($bSSE, $respuesta);\n"
        "        $oPaloConsola->desconectarTodo();\n"
        "        return;\n"
        "    } else {\n"
        "        // Filter out offline agents with unregistered extensions\n"
        "        foreach ($estadoCampania['agents'] as $k => $agent) {\n"
        "            if ($agent['status'] == 'offline' && !$oPaloConsola->extensionEstaRegistrada($agent['agentchannel'])) {\n"
        "                unset($estadoCampania['agents'][$k]);\n"
        "            }\n"
        "        }\n"
        "    }"
    )

    if php_status_target not in php_content_norm:
        print("Error: PHP checkStatus target not found")
        return 1
    php_content_norm = php_content_norm.replace(php_status_target, php_status_replace)

    # Add filtering to queuemembership
    php_qmember_target = (
        "                        // Este nuevo agente acaba de ingresar a la cola de campañas\n"
        "                        $estadoCliente['agents'][$sCanalAgente] = array_merge(\n"
        "                            array('agentchannel' => $sCanalAgente), $evento);\n"
        "                        unset($estadoCliente['agents'][$sCanalAgente]['queues']);\n"
        "\n"
        "                        $respuesta['agents']['add'][] = formatoAgente($estadoCliente['agents'][$sCanalAgente]);"
    )
    php_qmember_replace = (
        "                        // Este nuevo agente acaba de ingresar a la cola de campañas\n"
        "                        $estadoCliente['agents'][$sCanalAgente] = array_merge(\n"
        "                            array('agentchannel' => $sCanalAgente), $evento);\n"
        "                        unset($estadoCliente['agents'][$sCanalAgente]['queues']);\n"
        "\n"
        "                        if ($estadoCliente['agents'][$sCanalAgente]['status'] == 'offline' && \n"
        "                            !$oPaloConsola->extensionEstaRegistrada($sCanalAgente)) {\n"
        "                            unset($estadoCliente['agents'][$sCanalAgente]);\n"
        "                        } else {\n"
        "                            $respuesta['agents']['add'][] = formatoAgente($estadoCliente['agents'][$sCanalAgente]);\n"
        "                        }"
    )

    if php_qmember_target not in php_content_norm:
        print("Error: PHP queuemembership target not found")
        return 1
    php_content_norm = php_content_norm.replace(php_qmember_target, php_qmember_replace)

    # Append forceLoginAgent function at the end
    php_end_target = (
        "    $json = new Services_JSON();\n"
        "    Header('Content-Type: application/json');\n"
        "    return $json->encode($respuesta);\n"
        "}"
    )
    php_end_replace = (
        "    $json = new Services_JSON();\n"
        "    Header('Content-Type: application/json');\n"
        "    return $json->encode($respuesta);\n"
        "}\n\n"
        "function manejarMonitoreo_forceLoginAgent($module_name, $smarty, $sDirLocalPlantillas)\n"
        "{\n"
        "    $respuesta = array(\n"
        "        'status'    =>  'success',\n"
        "        'message'   =>  '(no message)',\n"
        "    );\n"
        "\n"
        "    $sAgentChannel = getParameter('agentchannel');\n"
        "    if (is_null($sAgentChannel) || $sAgentChannel == '') {\n"
        "        $respuesta['status'] = 'error';\n"
        "        $respuesta['message'] = 'Canal de agente no válido';\n"
        "    } else {\n"
        "        $oConsola = new PaloSantoConsola($sAgentChannel);\n"
        "        $exito = $oConsola->loginAgente($sAgentChannel);\n"
        "        if (!$exito) {\n"
        "            $respuesta['status'] = 'error';\n"
        "            $respuesta['message'] = $oConsola->errMsg;\n"
        "        }\n"
        "    }\n"
        "\n"
        "    $json = new Services_JSON();\n"
        "    Header('Content-Type: application/json');\n"
        "    return $json->encode($respuesta);\n"
        "}"
    )

    if php_end_target not in php_content_norm:
        print("Error: PHP end function target not found")
        return 1
    # Note: php_end_target appears multiple times (for forceUnbreakAgent too). Let's replace the last one.
    parts = php_content_norm.rsplit(php_end_target, 1)
    if len(parts) == 2:
        php_content_norm = parts[0] + php_end_replace + parts[1]
    else:
        print("Error: Split target failed for end function")
        return 1

    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)
    print("Success: Updated index.php")

    # 2. Modify template file
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1

    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_menu_target = (
        "<div id=\"agentContextMenu\" style=\"display: none;\">\n"
        "  <a href=\"#\" id=\"btnUnbreakAgent\">🔓 Finalizar Descanso</a>\n"
        "</div>"
    )
    tpl_menu_replace = (
        "<div id=\"agentContextMenu\" style=\"display: none;\">\n"
        "  <a href=\"#\" id=\"btnUnbreakAgent\">🔓 Finalizar Descanso</a>\n"
        "  <a href=\"#\" id=\"btnForceLoginAgent\">🔑 Iniciar Sesión</a>\n"
        "</div>"
    )

    if tpl_menu_target not in tpl_content_norm:
        print("Error: Context menu target not found in informacion_campania.tpl")
        return 1
    tpl_content_norm = tpl_content_norm.replace(tpl_menu_target, tpl_menu_replace)

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: Updated informacion_campania.tpl")

    # 3. Modify JS file
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    js_click_target = (
        "\t// Context menu handler for unbreaking agents\n"
        "\t$(document).on('click', '.agent-table-wrapper table tbody tr', function(event) {\n"
        "\t\tvar agentChannel = $(this).attr('data-agent');\n"
        "\t\tvar agentStatus = $(this).attr('data-status') || '';\n"
        "\t\t\n"
        "\t\tif (!agentChannel) return;\n"
        "\n"
        "\t\tvar statusLower = agentStatus.toLowerCase();\n"
        "\t\tvar isPaused = statusLower.indexOf('break') !== -1 || \n"
        "\t\t               statusLower.indexOf('descanso') !== -1 || \n"
        "\t\t               statusLower.indexOf('pause') !== -1 || \n"
        "\t\t               statusLower.indexOf('paused') !== -1;\n"
        "\t\t\n"
        "\t\tif (isPaused) {\n"
        "\t\t\t$('#agentContextMenu').css({\n"
        "\t\t\t\ttop: event.pageY + 'px',\n"
        "\t\t\t\tleft: event.pageX + 'px'\n"
        "\t\t\t}).fadeIn(150);\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').data('agentChannel', agentChannel);\n"
        "\t\t\tevent.stopPropagation();\n"
        "\t\t} else {\n"
        "\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t}\n"
        "\t});"
    )
    js_click_replace = (
        "\t// Context menu handler for unbreaking/logging in agents\n"
        "\t$(document).on('click', '.agent-table-wrapper table tbody tr', function(event) {\n"
        "\t\tvar agentChannel = $(this).attr('data-agent');\n"
        "\t\tvar agentStatus = $(this).attr('data-status') || '';\n"
        "\t\t\n"
        "\t\tif (!agentChannel) return;\n"
        "\n"
        "\t\tvar statusLower = agentStatus.toLowerCase();\n"
        "\t\tvar isPaused = statusLower.indexOf('break') !== -1 || \n"
        "\t\t               statusLower.indexOf('descanso') !== -1 || \n"
        "\t\t               statusLower.indexOf('pause') !== -1 || \n"
        "\t\t               statusLower.indexOf('paused') !== -1;\n"
        "\t\t\n"
        "\t\tvar isLoggedOut = statusLower.indexOf('no logon') !== -1 || \n"
        "\t\t                  statusLower.indexOf('logged out') !== -1 || \n"
        "\t\t                  statusLower.indexOf('no logoneado') !== -1;\n"
        "\t\t\n"
        "\t\tif (isPaused) {\n"
        "\t\t\t$('#btnUnbreakAgent').show().text('🔓 Finalizar Descanso');\n"
        "\t\t\t$('#btnForceLoginAgent').hide();\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').css({\n"
        "\t\t\t\ttop: event.pageY + 'px',\n"
        "\t\t\t\tleft: event.pageX + 'px'\n"
        "\t\t\t}).fadeIn(150);\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').data('agentChannel', agentChannel);\n"
        "\t\t\tevent.stopPropagation();\n"
        "\t\t} else if (isLoggedOut) {\n"
        "\t\t\t$('#btnUnbreakAgent').hide();\n"
        "\t\t\t$('#btnForceLoginAgent').show().text('🔑 Iniciar Sesión');\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').css({\n"
        "\t\t\t\ttop: event.pageY + 'px',\n"
        "\t\t\t\tleft: event.pageX + 'px'\n"
        "\t\t\t}).fadeIn(150);\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').data('agentChannel', agentChannel);\n"
        "\t\t\tevent.stopPropagation();\n"
        "\t\t} else {\n"
        "\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t}\n"
        "\t});"
    )

    if js_click_target not in js_content_norm:
        print("Error: Context menu click handler target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_click_target, js_click_replace)

    # Append login listener at the end
    js_post_target = (
        "\t$(document).on('click', '#btnUnbreakAgent', function(e) {\n"
        "\t\te.preventDefault();\n"
        "\t\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
        "\t\tif (agentChannel) {\n"
        "\t\t\tvar btn = $(this);\n"
        "\t\t\tbtn.text('Procesando...');\n"
        "\t\t\t\n"
        "\t\t\t$.post('index.php', {\n"
        "\t\t\t\tmenu: module_name,\n"
        "\t\t\t\trawmode: 'yes',\n"
        "\t\t\t\taction: 'forceUnbreakAgent',\n"
        "\t\t\t\tagentchannel: agentChannel\n"
        "\t\t\t}, function(response) {\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\tbtn.text('🔓 Finalizar Descanso');\n"
        "\t\t\t\t\n"
        "\t\t\t\tif (response.status !== 'success') {\n"
        "\t\t\t\t\talert('Error al finalizar descanso: ' + response.message);\n"
        "\t\t\t\t}\n"
        "\t\t\t}, 'json');\n"
        "\t\t}\n"
        "\t});"
    )
    js_post_replace = (
        "\t$(document).on('click', '#btnUnbreakAgent', function(e) {\n"
        "\t\te.preventDefault();\n"
        "\t\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
        "\t\tif (agentChannel) {\n"
        "\t\t\tvar btn = $(this);\n"
        "\t\t\tbtn.text('Procesando...');\n"
        "\t\t\t\n"
        "\t\t\t$.post('index.php', {\n"
        "\t\t\t\tmenu: module_name,\n"
        "\t\t\t\trawmode: 'yes',\n"
        "\t\t\t\taction: 'forceUnbreakAgent',\n"
        "\t\t\t\tagentchannel: agentChannel\n"
        "\t\t\t}, function(response) {\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\tbtn.text('🔓 Finalizar Descanso');\n"
        "\t\t\t\t\n"
        "\t\t\t\tif (response.status !== 'success') {\n"
        "\t\t\t\t\talert('Error al finalizar descanso: ' + response.message);\n"
        "\t\t\t\t}\n"
        "\t\t\t}, 'json');\n"
        "\t\t}\n"
        "\t});\n\n"
        "\t$(document).on('click', '#btnForceLoginAgent', function(e) {\n"
        "\t\te.preventDefault();\n"
        "\t\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
        "\t\tif (agentChannel) {\n"
        "\t\t\tvar btn = $(this);\n"
        "\t\t\tbtn.text('Procesando...');\n"
        "\t\t\t\n"
        "\t\t\t$.post('index.php', {\n"
        "\t\t\t\tmenu: module_name,\n"
        "\t\t\t\trawmode: 'yes',\n"
        "\t\t\t\taction: 'forceLoginAgent',\n"
        "\t\t\t\tagentchannel: agentChannel\n"
        "\t\t\t}, function(response) {\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\tbtn.text('🔑 Iniciar Sesión');\n"
        "\t\t\t\t\n"
        "\t\t\t\tif (response.status !== 'success') {\n"
        "\t\t\t\t\talert('Error al iniciar sesión: ' + response.message);\n"
        "\t\t\t\t}\n"
        "\t\t\t}, 'json');\n"
        "\t\t}\n"
        "\t});"
    )

    if js_post_target not in js_content_norm:
        print("Error: Context menu post handlers target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_post_target, js_post_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Updated javascript.js")

    # 4. Modify CSS file
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_rules = (
        "\n"
        "/* Hover and cursor pointer for unlogged available extensions */\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"logon\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Logon\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"logoneado\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Logoneado\"] {\n"
        "  cursor: pointer;\n"
        "}\n"
        "\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"logon\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Logon\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"logoneado\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Logoneado\"]:hover {\n"
        "  filter: brightness(1.1);\n"
        "  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);\n"
        "}\n"
    )

    if "[data-status*=\"logon\"]" not in css_content_norm:
        css_content_norm += css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: Updated styles.css")

    print("Agent filtering and force login UI updates applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
