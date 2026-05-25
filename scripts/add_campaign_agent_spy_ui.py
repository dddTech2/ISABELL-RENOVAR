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

    # Add spyAgent to switch
    php_switch_target = (
        "    case 'forceLoginAgent':\n"
        "        $sContenido = manejarMonitoreo_forceLoginAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;"
    )
    php_switch_replace = (
        "    case 'forceLoginAgent':\n"
        "        $sContenido = manejarMonitoreo_forceLoginAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;\n"
        "    case 'spyAgent':\n"
        "        $sContenido = manejarMonitoreo_spyAgent($module_name, $smarty, $local_templates_dir);\n"
        "        break;"
    )

    if php_switch_target not in php_content_norm:
        # Fallback to forceUnbreakAgent target
        php_switch_target_fb = (
            "    case 'forceUnbreakAgent':\n"
            "        $sContenido = manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $local_templates_dir);\n"
            "        break;"
        )
        php_switch_replace_fb = (
            "    case 'forceUnbreakAgent':\n"
            "        $sContenido = manejarMonitoreo_forceUnbreakAgent($module_name, $smarty, $local_templates_dir);\n"
            "        break;\n"
            "    case 'spyAgent':\n"
            "        $sContenido = manejarMonitoreo_spyAgent($module_name, $smarty, $local_templates_dir);\n"
            "        break;"
        )
        if php_switch_target_fb not in php_content_norm:
            print("Error: PHP switch target not found")
            return 1
        php_content_norm = php_content_norm.replace(php_switch_target_fb, php_switch_replace_fb)
    else:
        php_content_norm = php_content_norm.replace(php_switch_target, php_switch_replace)

    # Append manejarMonitoreo_spyAgent function before the closing PHP tag
    php_spy_function = """

function manejarMonitoreo_spyAgent($module_name, $smarty, $sDirLocalPlantillas)
{
    $respuesta = array(
        'status'    =>  'success',
        'message'   =>  '(no message)',
    );

    $sAgentChannel = getParameter('agentchannel');
    $sSupervisorExt = getParameter('supervisorext');

    if (is_null($sAgentChannel) || $sAgentChannel == '') {
        $respuesta['status'] = 'error';
        $respuesta['message'] = 'Canal de agente no válido';
    } elseif (is_null($sSupervisorExt) || $sSupervisorExt == '' || !ctype_digit($sSupervisorExt)) {
        $respuesta['status'] = 'error';
        $respuesta['message'] = 'Extensión del supervisor no válida';
    } else {
        // Extraer número de extensión del agente
        $agentExt = null;
        if (preg_match('/(?:Agent|SIP|PJSIP|IAX2)\\/(\\d+)/i', $sAgentChannel, $matches)) {
            $agentExt = $matches[1];
        } elseif (preg_match('/^(\\d+)$/', $sAgentChannel, $matches)) {
            $agentExt = $matches[1];
        }

        if (is_null($agentExt)) {
            $respuesta['status'] = 'error';
            $respuesta['message'] = 'No se pudo obtener la extensión del agente del canal: ' . $sAgentChannel;
        } else {
            // Obtener código ChanSpy
            $chanspyCode = '555';
            $dsnAsterisk = generarDSNSistema('asteriskuser', 'asterisk');
            $pDB_ast = new paloDB($dsnAsterisk);
            if (empty($pDB_ast->errMsg)) {
                $res = $pDB_ast->fetchTable("SELECT code FROM featurecodes WHERE modulename = 'core' AND feature = 'chanspy' AND active = 1", TRUE);
                if (is_array($res) && count($res) > 0 && !empty($res[0]['code'])) {
                    $chanspyCode = $res[0]['code'];
                }
            }

            require_once '/var/lib/asterisk/agi-bin/phpagi-asmanager.php';
            $astman = new AGI_AsteriskManager();
            if (!$astman->connect("127.0.0.1", 'admin', obtenerClaveAMIAdmin())) {
                $respuesta['status'] = 'error';
                $respuesta['message'] = 'No se pudo conectar a la AMI de Asterisk';
            } else {
                $origResult = $astman->Originate(array(
                    'Channel'  => "local/$sSupervisorExt@from-internal",
                    'Exten'    => "$chanspyCode$agentExt",
                    'Context'  => 'from-internal',
                    'Priority' => '1',
                    'Async'    => 'true',
                    'CallerID' => "Escucha: Agente $agentExt <$chanspyCode$agentExt>"
                ));
                $astman->disconnect();

                if (isset($origResult['Response']) && strtolower($origResult['Response']) == 'success') {
                    $respuesta['status'] = 'success';
                    $respuesta['message'] = 'Escucha iniciada con éxito';
                } else {
                    $respuesta['status'] = 'error';
                    $respuesta['message'] = isset($origResult['Message']) ? $origResult['Message'] : 'Respuesta fallida de Asterisk AMI';
                }
            }
        }
    }

    $json = new Services_JSON();
    Header('Content-Type: application/json');
    return $json->encode($respuesta);
}
"""

    if php_content_norm.endswith("?>\n"):
        php_content_norm = php_content_norm[:-3] + php_spy_function + "?>\n"
    elif php_content_norm.endswith("?>"):
        php_content_norm = php_content_norm[:-2] + php_spy_function + "?>"
    else:
        php_content_norm = php_content_norm + php_spy_function

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
        "  <a href=\"#\" id=\"btnForceLoginAgent\">🔑 Iniciar Sesión</a>\n"
        "</div>"
    )
    tpl_menu_replace = (
        "  <a href=\"#\" id=\"btnForceLoginAgent\">🔑 Iniciar Sesión</a>\n"
        "  <a href=\"#\" id=\"btnSpyAgent\">👂 Escuchar Llamada</a>\n"
        "</div>"
    )

    if tpl_menu_target not in tpl_content_norm:
        tpl_menu_target_fb = (
            "  <a href=\"#\" id=\"btnUnbreakAgent\">🔓 Finalizar Descanso</a>\n"
            "</div>"
        )
        tpl_menu_replace_fb = (
            "  <a href=\"#\" id=\"btnUnbreakAgent\">🔓 Finalizar Descanso</a>\n"
            "  <a href=\"#\" id=\"btnSpyAgent\">👂 Escuchar Llamada</a>\n"
            "</div>"
        )
        if tpl_menu_target_fb not in tpl_content_norm:
            print("Error: Context menu target not found in informacion_campania.tpl")
            return 1
        tpl_content_norm = tpl_content_norm.replace(tpl_menu_target_fb, tpl_menu_replace_fb)
    else:
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

    # Modify the context menu tr click handler to include isBusy and show/hide btnSpyAgent
    js_click_target = (
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
        "\t\t}"
    )

    js_click_replace = (
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

    if js_click_target not in js_content_norm:
        print("Error: Context menu click handler target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_click_target, js_click_replace)

    # Append spy agent handler
    js_spy_click_target = (
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

    js_spy_click_replace = (
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
        "\t});\n\n"
        "\t$(document).on('click', '#btnSpyAgent', function(e) {\n"
        "\t\te.preventDefault();\n"
        "\t\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
        "\t\tif (agentChannel) {\n"
        "\t\t\tvar savedExt = localStorage.getItem('supervisor_extension') || '';\n"
        "\t\t\tvar supervisorExt = prompt(\"Ingrese su número de extensión para escuchar la llamada:\", savedExt);\n"
        "\t\t\tif (supervisorExt === null) {\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\treturn;\n"
        "\t\t\t}\n"
        "\t\t\tsupervisorExt = supervisorExt.trim();\n"
        "\t\t\tif (supervisorExt === '' || !/^\\d+$/.test(supervisorExt)) {\n"
        "\t\t\t\talert(\"Debe ingresar una extensión numérica válida.\");\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\treturn;\n"
        "\t\t\t}\n"
        "\t\t\tlocalStorage.setItem('supervisor_extension', supervisorExt);\n"
        "\t\t\t\n"
        "\t\t\tvar btn = $(this);\n"
        "\t\t\tbtn.text('Conectando...');\n"
        "\t\t\t\n"
        "\t\t\t$.post('index.php', {\n"
        "\t\t\t\tmenu: module_name,\n"
        "\t\t\t\trawmode: 'yes',\n"
        "\t\t\t\taction: 'spyAgent',\n"
        "\t\t\t\tagentchannel: agentChannel,\n"
        "\t\t\t\tsupervisorext: supervisorExt\n"
        "\t\t\t}, function(response) {\n"
        "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
        "\t\t\t\tbtn.text('👂 Escuchar Llamada');\n"
        "\t\t\t\t\n"
        "\t\t\t\tif (response.status !== 'success') {\n"
        "\t\t\t\t\talert('Error al escuchar llamada: ' + response.message);\n"
        "\t\t\t\t} else {\n"
        "\t\t\t\t\talert('Llamada de escucha iniciada hacia la extensión ' + supervisorExt);\n"
        "\t\t\t\t}\n"
        "\t\t\t}, 'json');\n"
        "\t\t}\n"
        "\t});"
    )

    if js_spy_click_target not in js_content_norm:
        print("Error: Force login click handler target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_spy_click_target, js_spy_click_replace)

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
        "/* Hover and cursor pointer for busy/on call agents */\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"busy\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Busy\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"ocupado\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Ocupado\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"occupé\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Occupé\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"oncall\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Oncall\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"On Call\"],\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"on call\"] {\n"
        "  cursor: pointer;\n"
        "}\n"
        "\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"busy\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Busy\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"ocupado\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Ocupado\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"occupé\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Occupé\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"oncall\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"Oncall\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"On Call\"]:hover,\n"
        ".agent-table-wrapper table tbody tr[data-status*=\"on call\"]:hover {\n"
        "  filter: brightness(1.1);\n"
        "  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);\n"
        "}\n"
    )

    if "[data-status*=\"busy\"]" not in css_content_norm:
        css_content_norm += css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: Updated styles.css")

    print("Agent ChanSpy listening UI updates applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
