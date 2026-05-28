import os
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    print("Starting patch process...")

    # 1. Patch modules/campaign_monitoring/themes/default/informacion_campania.tpl
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")
    if os.path.exists(tpl_file):
        with open(tpl_file, 'r', encoding='utf-8') as f:
            tpl_content = f.read()
        
        tpl_old = (
            '  <a href="#" id="btnSpyAgent">👂 Escuchar Llamada</a>\n'
            '</div>'
        )
        tpl_new = (
            '  <a href="#" id="btnSpyAgent">👂 Escuchar Llamada</a>\n'
            '  <a href="#" id="btnReregisterWebphone" style="display: none;">🔄 Re-registrar WebPhone</a>\n'
            '</div>'
        )
        if tpl_old in tpl_content:
            tpl_content = tpl_content.replace(tpl_old, tpl_new)
            with open(tpl_file, 'w', encoding='utf-8') as f:
                f.write(tpl_content)
            print("Successfully patched informacion_campania.tpl")
        else:
            print("Warning: Context menu buttons pattern not found or already modified in informacion_campania.tpl")
    else:
        print(f"Error: Template file not found at {tpl_file}")

    # 2. Patch modules/campaign_monitoring/themes/default/js/javascript.js
    cm_js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")
    if os.path.exists(cm_js_file):
        with open(cm_js_file, 'r', encoding='utf-8') as f:
            cm_js_content = f.read()

        # We need to change:
        # hasLoggedOut || hasBusy) {
        # ...
        # to support hasPhoneOff
        js_old_check = "var hasBusy = statusLower.indexOf('busy') !== -1 || \n\t\t              statusLower.indexOf('ocupado') !== -1 || \n\t\t              statusLower.indexOf('oncall') !== -1 || \n\t\t              statusLower.indexOf('on call') !== -1 || \n\t\t              statusLower.indexOf('occupé') !== -1;"
        js_new_check = (
            "var hasBusy = statusLower.indexOf('busy') !== -1 || \n"
            "\t\t              statusLower.indexOf('ocupado') !== -1 || \n"
            "\t\t              statusLower.indexOf('oncall') !== -1 || \n"
            "\t\t              statusLower.indexOf('on call') !== -1 || \n"
            "\t\t              statusLower.indexOf('occupé') !== -1;\n\n"
            "\t\tvar hasPhoneOff = statusLower.indexOf('phone off') !== -1 || statusLower.indexOf('phoneoff') !== -1;"
        )

        if js_old_check in cm_js_content and "var hasPhoneOff" not in cm_js_content:
            cm_js_content = cm_js_content.replace(js_old_check, js_new_check)
            print("Injected hasPhoneOff check variable.")
        else:
            # Try alternate formatting
            js_old_check_alt = "var hasBusy = statusLower.indexOf('busy') !== -1 ||"
            if js_old_check_alt in cm_js_content and "var hasPhoneOff" not in cm_js_content:
                print("Using regex to find and inject hasPhoneOff variable...")
                pattern = r"(var hasBusy =.*?;)"
                cm_js_content = re.sub(pattern, r"\1\n\n\t\tvar hasPhoneOff = statusLower.indexOf('phone off') !== -1 || statusLower.indexOf('phoneoff') !== -1;", cm_js_content, flags=re.DOTALL)

        # Update context menu display condition
        old_menu_show = "if (hasPaused || hasLoggedOut || hasBusy) {"
        new_menu_show = "if (hasPaused || hasLoggedOut || hasBusy || hasPhoneOff) {"
        if old_menu_show in cm_js_content and "hasPhoneOff) {" not in cm_js_content:
            cm_js_content = cm_js_content.replace(old_menu_show, new_menu_show)
            print("Updated context menu display condition.")
        
        # Inject button display logic inside menu display
        old_spy_logic = (
            "\t\t\t} else {\n"
            "\t\t\t\t$('#btnSpyAgent').hide();\n"
            "\t\t\t}\n"
            "\t\t\t\n"
            "\t\t\t$('#agentContextMenu').css({"
        )
        new_spy_logic = (
            "\t\t\t} else {\n"
            "\t\t\t\t$('#btnSpyAgent').hide();\n"
            "\t\t\t}\n"
            "\t\t\t\n"
            "\t\t\tif (hasPhoneOff) {\n"
            "\t\t\t\t$('#btnReregisterWebphone').show().text('🔄 Re-registrar WebPhone');\n"
            "\t\t\t} else {\n"
            "\t\t\t\t$('#btnReregisterWebphone').hide();\n"
            "\t\t\t}\n"
            "\t\t\t\n"
            "\t\t\t$('#agentContextMenu').css({"
        )
        if old_spy_logic in cm_js_content and "btnReregisterWebphone').show().text" not in cm_js_content:
            cm_js_content = cm_js_content.replace(old_spy_logic, new_spy_logic)
            print("Injected btnReregisterWebphone visibility logic.")
        else:
            # Fallback check
            # Look for the last $(this).find('td') block or similar
            pattern_spy = r"(\t\t\t\}\n\t\t\t\n\t\t\t\$\('#agentContextMenu'\)\.css\(\{)"
            if "btnReregisterWebphone').show().text" not in cm_js_content:
                cm_js_content = re.sub(pattern_spy, r"}\n\t\t\t\n\t\t\tif (hasPhoneOff) {\n\t\t\t\t$('#btnReregisterWebphone').show().text('🔄 Re-registrar WebPhone');\n\t\t\t} else {\n\t\t\t\t$('#btnReregisterWebphone').hide();\n\t\t\t}\n\t\t\t\n\t\t\t$('#agentContextMenu').css({", cm_js_content)
                print("Injected btnReregisterWebphone visibility logic via fallback regex.")

        # Bind click handler for btnReregisterWebphone before the end of $(document).ready/document logic
        # We can append it at the end of the file or next to btnSpyAgent click
        old_spy_click = (
            "\t\t\t}, function(response) {\n"
            "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
            "\t\t\t\tbtn.text('👂 Escuchar Llamada');\n"
            "\t\t\t\n"
            "\t\t\t\tif (response.status !== 'success') {\n"
            "\t\t\t\t\talert('Error al escuchar llamada: ' + response.message);\n"
            "\t\t\t\t} else {\n"
            "\t\t\t\t\talert('Llamada de escucha iniciada hacia su extensión.');\n"
            "\t\t\t\t}\n"
            "\t\t\t}, 'json');\n"
            "\t\t}\n"
            "\t});"
        )
        new_spy_click = (
            "\t\t\t}, function(response) {\n"
            "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
            "\t\t\t\tbtn.text('👂 Escuchar Llamada');\n"
            "\t\t\t\n"
            "\t\t\t\tif (response.status !== 'success') {\n"
            "\t\t\t\t\talert('Error al escuchar llamada: ' + response.message);\n"
            "\t\t\t\t} else {\n"
            "\t\t\t\t\talert('Llamada de escucha iniciada hacia su extensión.');\n"
            "\t\t\t\t}\n"
            "\t\t\t}, 'json');\n"
            "\t\t}\n"
            "\t});\n\n"
            "\t$(document).on('click', '#btnReregisterWebphone', function(e) {\n"
            "\t\te.preventDefault();\n"
            "\t\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
            "\t\tif (agentChannel) {\n"
            "\t\t\tvar btn = $(this);\n"
            "\t\t\tbtn.text('Procesando...');\n"
            "\t\t\t\n"
            "\t\t\t$.post('index.php', {\n"
            "\t\t\t\tmenu: module_name,\n"
            "\t\t\t\trawmode: 'yes',\n"
            "\t\t\t\taction: 'reregisterWebphone',\n"
            "\t\t\t\tagentchannel: agentChannel\n"
            "\t\t\t}, function(response) {\n"
            "\t\t\t\t$('#agentContextMenu').fadeOut(100);\n"
            "\t\t\t\tbtn.text('🔄 Re-registrar WebPhone');\n"
            "\t\t\t\t\n"
            "\t\t\t\tif (response.status !== 'success') {\n"
            "\t\t\t\t\talert('Error al re-registrar: ' + response.message);\n"
            "\t\t\t\t} else {\n"
            "\t\t\t\t\talert('Se envió la señal de re-registro al WebPhone.');\n"
            "\t\t\t\t}\n"
            "\t\t\t}, 'json');\n"
            "\t\t}\n"
            "\t});"
        )
        if old_spy_click in cm_js_content and "btnReregisterWebphone', function(e)" not in cm_js_content:
            cm_js_content = cm_js_content.replace(old_spy_click, new_spy_click)
            print("Successfully bound click handler in javascript.js.")
        else:
            # Fallback search
            if "btnReregisterWebphone', function(e)" not in cm_js_content:
                print("Warning: btnSpyAgent click block not found exactly. Appending at the end of the file.")
                cm_js_content += (
                    "\n\n$(document).on('click', '#btnReregisterWebphone', function(e) {\n"
                    "\te.preventDefault();\n"
                    "\tvar agentChannel = $('#agentContextMenu').data('agentChannel');\n"
                    "\tif (agentChannel) {\n"
                    "\t\tvar btn = $(this);\n"
                    "\t\tbtn.text('Procesando...');\n"
                    "\t\t$.post('index.php', {\n"
                    "\t\t\tmenu: module_name,\n"
                    "\t\t\trawmode: 'yes',\n"
                    "\t\t\taction: 'reregisterWebphone',\n"
                    "\t\t\tagentchannel: agentChannel\n"
                    "\t\t}, function(response) {\n"
                    "\t\t\t$('#agentContextMenu').fadeOut(100);\n"
                    "\t\t\tbtn.text('🔄 Re-registrar WebPhone');\n"
                    "\t\t\tif (response.status !== 'success') {\n"
                    "\t\t\t\talert('Error al re-registrar: ' + response.message);\n"
                    "\t\t\t} else {\n"
                    "\t\t\t\talert('Se envió la señal de re-registro al WebPhone.');\n"
                    "\t\t\t}\n"
                    "\t\t}, 'json');\n"
                    "\t}\n"
                    "});\n"
                )

        with open(cm_js_file, 'w', encoding='utf-8') as f:
            f.write(cm_js_content)
        print("Successfully updated campaign_monitoring javascript.js")
    else:
        print(f"Error: js file not found at {cm_js_file}")

    # 3. Patch modules/campaign_monitoring/index.php
    cm_index_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")
    if os.path.exists(cm_index_file):
        with open(cm_index_file, 'r', encoding='utf-8') as f:
            cm_index_content = f.read()

        # Add switch action
        old_switch = (
            "    case 'forceLoginAgent':\n"
            "        $sContenido = manejarMonitoreo_forceLoginAgent($module_name, $smarty, $local_templates_dir);\n"
            "        break;"
        )
        new_switch = (
            "    case 'forceLoginAgent':\n"
            "        $sContenido = manejarMonitoreo_forceLoginAgent($module_name, $smarty, $local_templates_dir);\n"
            "        break;\n"
            "    case 'reregisterWebphone':\n"
            "        $sContenido = manejarMonitoreo_reregisterWebphone($module_name, $smarty, $local_templates_dir);\n"
            "        break;"
        )
        if old_switch in cm_index_content and "reregisterWebphone" not in cm_index_content:
            cm_index_content = cm_index_content.replace(old_switch, new_switch)
            print("Successfully added reregisterWebphone case to AJAX switch.")
        
        # Inject helper function before spyAgent
        old_spy_fn = "function manejarMonitoreo_spyAgent("
        new_reregister_fn = (
            "function manejarMonitoreo_reregisterWebphone($module_name, $smarty, $sDirLocalPlantillas)\n"
            "{\n"
            "    $respuesta = array(\n"
            "        'status'    =>  'success',\n"
            "        'message'   =>  '(no message)',\n"
            "    );\n\n"
            "    $sAgentChannel = getParameter('agentchannel');\n"
            "    if (is_null($sAgentChannel) || $sAgentChannel == '') {\n"
            "        $respuesta['status'] = 'error';\n"
            "        $respuesta['message'] = 'Canal de agente no válido';\n"
            "    } else {\n"
            "        $agentExt = null;\n"
            "        if (preg_match('/(?:Agent|SIP|PJSIP|IAX2)\\/(\\d+)/i', $sAgentChannel, $matches)) {\n"
            "            $agentExt = $matches[1];\n"
            "        } elseif (preg_match('/^(\\d+)$/', $sAgentChannel, $matches)) {\n"
            "            $agentExt = $matches[1];\n"
            "        }\n\n"
            "        if (is_null($agentExt)) {\n"
            "            $respuesta['status'] = 'error';\n"
            "            $respuesta['message'] = 'No se pudo obtener la extensión del agente del canal: ' . $sAgentChannel;\n"
            "        } else {\n"
            "            $flagFile = \"/tmp/webphone_register_\" . $agentExt . \".flag\";\n"
            "            if (@file_put_contents($flagFile, \"1\") === FALSE) {\n"
            "                $respuesta['status'] = 'error';\n"
            "                $respuesta['message'] = 'No se pudo crear la señal de re-registro';\n"
            "            } else {\n"
            "                $respuesta['status'] = 'success';\n"
            "                $respuesta['message'] = 'Señal enviada a la extensión ' . $agentExt;\n"
            "            }\n"
            "        }\n"
            "    }\n\n"
            "    $json = new Services_JSON();\n"
            "    Header('Content-Type: application/json');\n"
            "    return $json->encode($respuesta);\n"
            "}\n\n"
            "function manejarMonitoreo_spyAgent("
        )
        if old_spy_fn in cm_index_content and "function manejarMonitoreo_reregisterWebphone" not in cm_index_content:
            cm_index_content = cm_index_content.replace(old_spy_fn, new_reregister_fn)
            print("Successfully injected manejarMonitoreo_reregisterWebphone function.")

        with open(cm_index_file, 'w', encoding='utf-8') as f:
            f.write(cm_index_content)
        print("Successfully updated campaign_monitoring index.php")
    else:
        print(f"Error: index.php not found at {cm_index_file}")

    # 4. Patch modules/agent_console/index.php
    ac_index_file = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    if os.path.exists(ac_index_file):
        with open(ac_index_file, 'r', encoding='utf-8') as f:
            ac_index_content = f.read()

        # Add check flag to checkStatus polling loop
        old_loop_start = (
            "        while (connection_status() == CONNECTION_NORMAL &&\n"
            "            count($respuestaEventos) <= 0 && count($respuesta) <= 0\n"
            "            && time() - $iTimestampInicio <  $iTimeoutPoll) {"
        )
        new_loop_start = (
            "        while (connection_status() == CONNECTION_NORMAL &&\n"
            "            count($respuestaEventos) <= 0 && count($respuesta) <= 0\n"
            "            && time() - $iTimestampInicio <  $iTimeoutPoll) {\n\n"
            "            // Check for force-webphone-register flag\n"
            "            if (!empty($sExtension)) {\n"
            "                $flagFile = \"/tmp/webphone_register_\" . $sExtension . \".flag\";\n"
            "                if (file_exists($flagFile)) {\n"
            "                    @unlink($flagFile);\n"
            "                    $respuesta[] = array(\n"
            "                        'event' => 'force-webphone-register'\n"
            "                    );\n"
            "                    break;\n"
            "                }\n"
            "            }"
        )
        if old_loop_start in ac_index_content and "force-webphone-register" not in ac_index_content:
            ac_index_content = ac_index_content.replace(old_loop_start, new_loop_start)
            print("Successfully added force-webphone-register check to agent_console index.php loop.")
        else:
            # Try alternate formatting
            print("Warning: Loop starting pattern not found exactly in agent_console index.php. Doing regex match.")
            pattern_loop = r"(while\s*\(\s*connection_status\(\)\s*==\s*CONNECTION_NORMAL\s*&&\s*count\(\$respuestaEventos\)\s*<=\s*0\s*&&\s*count\(\$respuesta\)\s*<=\s*0\s*&&\s*time\(\)\s*-\s*\$iTimestampInicio\s*<\s*\$iTimeoutPoll\s*\)\s*\{)"
            if "force-webphone-register" not in ac_index_content:
                ac_index_content = re.sub(pattern_loop, r"\1\n\n            // Check for force-webphone-register flag\n            if (!empty($sExtension)) {\n                $flagFile = \"/tmp/webphone_register_\" . $sExtension . \".flag\";\n                if (file_exists($flagFile)) {\n                    @unlink($flagFile);\n                    $respuesta[] = array(\n                        'event' => 'force-webphone-register'\n                    );\n                    break;\n                }\n            }", ac_index_content)
                print("Injected via regex fallback.")

        with open(ac_index_file, 'w', encoding='utf-8') as f:
            f.write(ac_index_content)
        print("Successfully updated agent_console index.php")
    else:
        print(f"Error: agent_console index.php not found at {ac_index_file}")

    # 5. Patch modules/agent_console/themes/default/js/javascript.js
    ac_js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "javascript.js")
    if os.path.exists(ac_js_file):
        with open(ac_js_file, 'r', encoding='utf-8') as f:
            ac_js_content = f.read()

        # Add event case in manejarRespuestaStatus
        old_event_case = (
            "\t\tcase 'logged-out':\n"
            "\t\t\t// El refresco debería conducir a la página de login"
        )
        new_event_case = (
            "\t\tcase 'force-webphone-register':\n"
            "\t\t\tif (typeof WebPhone !== 'undefined') {\n"
            "\t\t\t\tWebPhone.reconnect();\n"
            "\t\t\t} else {\n"
            "\t\t\t\twindow.location.reload();\n"
            "\t\t\t}\n"
            "\t\t\tbreak;\n"
            "\t\tcase 'logged-out':\n"
            "\t\t\t// El refresco debería conducir a la página de login"
        )
        if old_event_case in ac_js_content and "force-webphone-register" not in ac_js_content:
            ac_js_content = ac_js_content.replace(old_event_case, new_event_case)
            print("Successfully added force-webphone-register handler in agent_console javascript.js")
        else:
            pattern_case = r"(case\s+'logged-out'\s*:)"
            if "force-webphone-register" not in ac_js_content:
                ac_js_content = re.sub(pattern_case, r"case 'force-webphone-register':\n\t\t\tif (typeof WebPhone !== 'undefined') {\n\t\t\t\tWebPhone.reconnect();\n\t\t\t} else {\n\t\t\t\twindow.location.reload();\n\t\t\t}\n\t\t\tbreak;\n\t\tcase 'logged-out':", ac_js_content)
                print("Injected force-webphone-register handler via regex fallback.")

        with open(ac_js_file, 'w', encoding='utf-8') as f:
            f.write(ac_js_content)
        print("Successfully updated agent_console javascript.js")
    else:
        print(f"Error: agent_console javascript.js not found at {ac_js_file}")

    print("Patch process completed successfully!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
