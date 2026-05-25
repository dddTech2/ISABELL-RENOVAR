import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    consola_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")
    php_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")
    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")

    print(f"Modifying Console class file: {consola_file}")
    print(f"Modifying PHP file: {php_file}")
    print(f"Modifying JS file: {js_file}")

    # ==========================================
    # 1. Modify Console Class File
    # ==========================================
    if not os.path.exists(consola_file):
        print(f"Error: Console class file not found at {consola_file}")
        return 1

    with open(consola_file, 'r', encoding='utf-8') as f:
        consola_content = f.read()

    consola_content_norm = consola_content.replace('\r\n', '\n')

    consola_target = (
        "                    if ($agent['status'] == 'online' || $agent['status'] == 'paused') {\n"
        "                        $callInfo = $this->_detectarLlamadaActivaAgente($agent, $activeChannels);\n"
        "                        if ($callInfo !== FALSE) {\n"
        "                            $agent['status'] = 'oncall';\n"
        "                            $agent['callinfo'] = $callInfo;\n"
        "                        }\n"
        "                    }"
    )

    consola_replace = (
        "                    if ($agent['status'] == 'online' || $agent['status'] == 'paused' || $agent['status'] == 'offline') {\n"
        "                        $callInfo = $this->_detectarLlamadaActivaAgente($agent, $activeChannels);\n"
        "                        if ($callInfo !== FALSE) {\n"
        "                            $agent['original_status'] = $agent['status'];\n"
        "                            $agent['status'] = 'oncall';\n"
        "                            $agent['callinfo'] = $callInfo;\n"
        "                        }\n"
        "                    }"
    )

    if consola_target not in consola_content_norm:
        print("Error: Console target not found in paloSantoConsola.class.php")
        return 1
    consola_content_norm = consola_content_norm.replace(consola_target, consola_replace)

    if '\r\n' in consola_content:
        consola_content_norm = consola_content_norm.replace('\n', '\r\n')

    with open(consola_file, 'w', encoding='utf-8') as f:
        f.write(consola_content_norm)
    print("Success: Updated paloSantoConsola.class.php")

    # ==========================================
    # 2. Modify PHP File
    # ==========================================
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    php_target = (
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        break;"
    )

    php_replace = (
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        if (isset($agent['original_status'])) {\n"
        "            if ($agent['original_status'] == 'paused') {\n"
        "                $sEtiquetaPause = _tr('paused');\n"
        "                if (!is_null($agent['pauseinfo'])) {\n"
        "                    $sEtiquetaPause .= ': '.$agent['pauseinfo']['pausename'];\n"
        "                }\n"
        "                $sEtiquetaStatus = _tr('oncall') . ' (' . $sEtiquetaPause . ')';\n"
        "            } elseif ($agent['original_status'] == 'offline') {\n"
        "                $sEtiquetaStatus = _tr('oncall') . ' (' . _tr('No logon') . ')';\n"
        "            }\n"
        "        }\n"
        "        break;"
    )

    if php_target not in php_content_norm:
        print("Error: PHP target not found in modules/campaign_monitoring/index.php")
        return 1
    php_content_norm = php_content_norm.replace(php_target, php_replace)

    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)
    print("Success: Updated index.php")

    # ==========================================
    # 3. Modify JS File
    # ==========================================
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Replace agentColor condition
    js_color_target = (
        "  if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
        "    color = 'orange';\n"
        "  } else {"
    )

    js_color_replace = (
        "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
        "    color = 'yellow';\n"
        "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
        "    color = 'orange';\n"
        "  } else {"
    )

    if js_color_target not in js_content_norm:
        print("Error: Color priority target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_color_target, js_color_replace)

    # Replace agentUpdateColor condition
    js_update_color_target = (
        "  if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
        "    color = 'orange';\n"
        "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-break.png\" alt=\"En Break\" style=\"padding-right:1px;\"/>';\n"
        "  } else {"
    )

    js_update_color_replace = (
        "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
        "    color = 'yellow';\n"
        "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-busy.png\" alt=\"Ocupado\" style=\"padding-right:1px;\"/>';\n"
        "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
        "    color = 'orange';\n"
        "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-break.png\" alt=\"En Break\" style=\"padding-right:1px;\"/>';\n"
        "  } else {"
    )

    if js_update_color_target not in js_content_norm:
        print("Error: Update color priority target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_update_color_target, js_update_color_replace)

    # Replace context menu handler click block
    js_menu_target = (
        "\t\tvar isBusy = statusLower.indexOf('busy') !== -1 || \n"
        "\t\t             statusLower.indexOf('ocupado') !== -1 || \n"
        "\t\t             statusLower.indexOf('oncall') !== -1 || \n"
        "\t\t             statusLower.indexOf('on call') !== -1 || \n"
        "\t\t             statusLower.indexOf('occupé') !== -1;\n"
        "\t\t\n"
        "\t\tif (isPaused) {\n"
        "\t\t\t$('#btnUnbreakAgent').show().text('🔓 Finalizar Descanso');\n"
        "\t\t\t$('#btnForceLoginAgent').hide();\n"
        "\t\t\t$('#btnSpyAgent').hide();\n"
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
        "\t\t\t$('#btnSpyAgent').hide();\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').css({\n"
        "\t\t\t\ttop: event.pageY + 'px',\n"
        "\t\t\t\tleft: event.pageX + 'px'\n"
        "\t\t\t}).fadeIn(150);\n"
        "\t\t\t\n"
        "\t\t\t$('#agentContextMenu').data('agentChannel', agentChannel);\n"
        "\t\t\tevent.stopPropagation();\n"
        "\t\t} else if (isBusy) {\n"
        "\t\t\t$('#btnUnbreakAgent').hide();\n"
        "\t\t\t$('#btnForceLoginAgent').hide();\n"
        "\t\t\t$('#btnSpyAgent').show().text('👂 Escuchar Llamada');\n"
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
        "\t\t}"
    )

    js_menu_replace = (
        "\t\tvar hasPaused = statusLower.indexOf('break') !== -1 || \n"
        "\t\t                statusLower.indexOf('descanso') !== -1 || \n"
        "\t\t                statusLower.indexOf('pause') !== -1 || \n"
        "\t\t                statusLower.indexOf('paused') !== -1;\n"
        "\t\t\n"
        "\t\tvar hasLoggedOut = statusLower.indexOf('no logon') !== -1 || \n"
        "\t\t                   statusLower.indexOf('logged out') !== -1 || \n"
        "\t\t                   statusLower.indexOf('no logoneado') !== -1;\n"
        "\t\t\n"
        "\t\tvar hasBusy = statusLower.indexOf('busy') !== -1 || \n"
        "\t\t              statusLower.indexOf('ocupado') !== -1 || \n"
        "\t\t              statusLower.indexOf('oncall') !== -1 || \n"
        "\t\t              statusLower.indexOf('on call') !== -1 || \n"
        "\t\t              statusLower.indexOf('occupé') !== -1;\n"
        "\t\t\n"
        "\t\tif (hasPaused || hasLoggedOut || hasBusy) {\n"
        "\t\t\tif (hasPaused) {\n"
        "\t\t\t\t$('#btnUnbreakAgent').show().text('🔓 Finalizar Descanso');\n"
        "\t\t\t} else {\n"
        "\t\t\t\t$('#btnUnbreakAgent').hide();\n"
        "\t\t\t}\n"
        "\t\t\t\n"
        "\t\t\tif (hasLoggedOut) {\n"
        "\t\t\t\t$('#btnForceLoginAgent').show().text('🔑 Iniciar Sesión');\n"
        "\t\t\t} else {\n"
        "\t\t\t\t$('#btnForceLoginAgent').hide();\n"
        "\t\t\t}\n"
        "\t\t\t\n"
        "\t\t\tif (hasBusy) {\n"
        "\t\t\t\tvar callNumberTd = $(this).find('td').eq(2).text().trim();\n"
        "\t\t\t\tif (callNumberTd !== '' && callNumberTd !== '-') {\n"
        "\t\t\t\t\t$('#btnSpyAgent').show().text('👂 Escuchar Llamada');\n"
        "\t\t\t\t} else {\n"
        "\t\t\t\t\t$('#btnSpyAgent').hide();\n"
        "\t\t\t\t}\n"
        "\t\t\t} else {\n"
        "\t\t\t\t$('#btnSpyAgent').hide();\n"
        "\t\t\t}\n"
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
        "\t\t}"
    )

    if js_menu_target not in js_content_norm:
        print("Error: Context menu logic target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_menu_target, js_menu_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Updated javascript.js")

    print("Agent active call prioritization updates applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
