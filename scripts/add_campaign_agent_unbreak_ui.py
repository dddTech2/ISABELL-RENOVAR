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

    # Add AJAX case to switch
    ajax_switch_target = "    switch (getParameter('action')) {"
    ajax_switch_replace = (
        "    switch (getParameter('action')) {\n"
        "    case 'forceUnbreakAgent':\n"
        "        $sContenido = manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;"
    )

    if ajax_switch_target not in php_content_norm:
        print("Error: AJAX switch action target not found in index.php")
        return 1

    php_content_norm = php_content_norm.replace(ajax_switch_target, ajax_switch_replace)

    # Append function at the end
    php_end_target = (
        "    $smarty->assign('HEADER_LIBS_JQUERY', implode(\"\\n\", $listaLibsJS_framework));\n"
        "}"
    )
    php_end_replace = (
        "    $smarty->assign('HEADER_LIBS_JQUERY', implode(\"\\n\", $listaLibsJS_framework));\n"
        "}\n\n"
        "function manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $sDirLocalPlantillas)\n"
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
        "        $exito = $oConsola->terminarBreak();\n"
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
        print("Error: End function target not found in index.php")
        return 1

    php_content_norm = php_content_norm.replace(php_end_target, php_end_replace)

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

    tpl_table_target = (
        "        <div class=\"llamadas\" {literal}{{bindAttr style=\"alturaLlamada\"}}{/literal}>\n"
        "            <table>\n"
        "                {literal}{{#view tagName=\"tbody\"}}\n"
        "                {{#each agentes}}\n"
        "                <tr  {{bindAttr class=\"canal\"}}>"
    )
    tpl_table_replace = (
        "        <div class=\"llamadas agent-table-wrapper\" {literal}{{bindAttr style=\"alturaLlamada\"}}{/literal}>\n"
        "            <table>\n"
        "                {literal}{{#view tagName=\"tbody\"}}\n"
        "                {{#each agentes}}\n"
        "                <tr  {{bindAttr class=\"canal\"}} {{bindAttr data-agent=\"canal\" data-status=\"estado\"}}>"
    )

    if tpl_table_target not in tpl_content_norm:
        # Try looser match
        tpl_table_target_alt = (
            "        <div class=\"llamadas\" {literal}{{bindAttr style=\"alturaLlamada\"}}{/literal}>\n"
            "            <table>\n"
            "                {literal}{{#view tagName=\"tbody\"}}\n"
            "                {{#each agentes}}\n"
            "                <tr  {{bindAttr class=\"canal\"}}>"
        )
        if tpl_table_target_alt not in tpl_content_norm:
            print("Error: Agent table target not found in informacion_campania.tpl")
            return 1
        else:
            tpl_content_norm = tpl_content_norm.replace(tpl_table_target_alt, tpl_table_replace)
    else:
        tpl_content_norm = tpl_content_norm.replace(tpl_table_target, tpl_table_replace)

    tpl_end_target = (
        "</script>\n"
        "</div>"
    )
    tpl_end_replace = (
        "</script>\n\n"
        "{* Context menu for agents on break *}\n"
        "<div id=\"agentContextMenu\" style=\"display: none;\">\n"
        "  <a href=\"#\" id=\"btnUnbreakAgent\">🔓 Finalizar Descanso</a>\n"
        "</div>\n"
        "</div>"
    )

    if tpl_end_target not in tpl_content_norm:
        print("Error: End script target not found in informacion_campania.tpl")
        return 1

    tpl_content_norm = tpl_content_norm.replace(tpl_end_target, tpl_end_replace)

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

    js_end_target = (
        "\t\tscroll: function() {\n"
        "\t\t\t// Forzar a mostrar el último registro\n"
        "\t\t\tvar r = this.$();\n"
        "\t\t\tr.scrollTop(r.prop('scrollHeight'));\n"
        "\t\t}\n"
        "\t});\n"
        "});"
    )

    js_end_replace = (
        "\t\tscroll: function() {\n"
        "\t\t\t// Forzar a mostrar el último registro\n"
        "\t\t\tvar r = this.$();\n"
        "\t\t\tr.scrollTop(r.prop('scrollHeight'));\n"
        "\t\t}\n"
        "\t});\n\n"
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
        "\t});\n"
        "\n"
        "\t$(document).on('click', function() {\n"
        "\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t});\n"
        "\n"
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
        "\t});\n"
        "});"
    )

    if js_end_target not in js_content_norm:
        print("Error: End script view target not found in javascript.js")
        return 1

    js_content_norm = js_content_norm.replace(js_end_target, js_end_replace)

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
        "/* Context menu popover */\n"
        "#agentContextMenu {\n"
        "  display: none;\n"
        "  position: absolute;\n"
        "  z-index: 10000;\n"
        "  background: rgba(255, 255, 255, 0.95);\n"
        "  backdrop-filter: blur(5px);\n"
        "  border: 1px solid rgba(0, 0, 0, 0.15);\n"
        "  box-shadow: 0 4px 12px rgba(0,0,0,0.15);\n"
        "  border-radius: 6px;\n"
        "  padding: 4px 0;\n"
        "  min-width: 180px;\n"
        "}\n"
        "\n"
        "#agentContextMenu a {\n"
        "  display: flex;\n"
        "  align-items: center;\n"
        "  padding: 10px 16px;\n"
        "  color: #333;\n"
        "  text-decoration: none;\n"
        "  font-weight: 600;\n"
        "  font-size: 13px;\n"
        "  transition: background-color 0.2s, color 0.2s;\n"
        "}\n"
        "\n"
        "#agentContextMenu a:hover {\n"
        "  background-color: #007bff;\n"
        "  color: white;\n"
        "}\n"
        "\n"
        "/* Hover indicator for interactive rows */\n"
        ".agent-table-wrapper table tbody tr {\n"
        "  transition: transform 0.1s ease;\n"
        "}\n"
        "\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"descanso\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Descanso\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"break\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Break\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"pause\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Pause\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"paused\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Paused\"] {\n"
        "  cursor: pointer;\n"
        "}\n"
        "\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"descanso\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Descanso\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"break\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Break\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"pause\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Pause\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"paused\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Paused\"]:hover {\n"
        "  filter: brightness(1.1);\n"
        "  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);\n"
        "}\n"
    )

    if "#agentContextMenu" not in css_content_norm:
        css_content_norm += css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: Updated styles.css")

    print("All agent unbreak contextual UI updates applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
