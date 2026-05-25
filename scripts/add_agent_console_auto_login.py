import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "javascript.js")

    print(f"Modifying PHP file: {php_file}")
    print(f"Modifying JS file: {js_file}")

    # 1. Modify PHP file
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    # Add checkAutoLogin to allowed actions array
    allowed_actions_target = "if (!in_array($sAction, array('', 'doLogin', 'checkLogin')))"
    allowed_actions_replace = "if (!in_array($sAction, array('', 'doLogin', 'checkLogin', 'checkAutoLogin')))"

    if allowed_actions_target not in php_content_norm:
        print("Error: Allowed actions target not found in PHP file")
        return 1
    php_content_norm = php_content_norm.replace(allowed_actions_target, allowed_actions_replace)

    # Add auto-login check on empty action (initial load)
    auto_login_load_target = (
        "    if (!in_array($sAction, array('', 'doLogin', 'checkLogin', 'checkAutoLogin')))\n"
        "        $sAction = '';"
    )
    auto_login_load_replace = (
        "    if (!in_array($sAction, array('', 'doLogin', 'checkLogin', 'checkAutoLogin')))\n"
        "        $sAction = '';\n\n"
        "    // If the action is empty (initial page load), check if the agent is already logged in to auto-login\n"
        "    if ($sAction == '') {\n"
        "        if (_verificarYAutoLogonear($module_name, true)) {\n"
        "            Header('Location: index.php?menu=' . $module_name);\n"
        "            exit();\n"
        "        }\n"
        "    }"
    )

    if auto_login_load_target not in php_content_norm:
        print("Error: Auto-login load target not found in PHP file")
        return 1
    php_content_norm = php_content_norm.replace(auto_login_load_target, auto_login_load_replace)

    # Add case for checkAutoLogin in action switch
    switch_case_target = (
        "    case 'checkLogin':\n"
        "        $sContenido = manejarLogin_checkLogin();\n"
        "        break;"
    )
    switch_case_replace = (
        "    case 'checkLogin':\n"
        "        $sContenido = manejarLogin_checkLogin();\n"
        "        break;\n"
        "    case 'checkAutoLogin':\n"
        "        $sContenido = manejarLogin_checkAutoLogin($module_name);\n"
        "        break;"
    )

    if switch_case_target not in php_content_norm:
        print("Error: Switch case target not found in PHP file")
        return 1
    php_content_norm = php_content_norm.replace(switch_case_target, switch_case_replace)

    # Append helper functions after manejarLogin
    helper_funcs_target = (
        "    return $sContenido;\n"
        "}\n\n"
        "// Mostrar el formulario donde el agente ingresa su login"
    )
    helper_funcs_replace = (
        "    return $sContenido;\n"
        "}\n\n"
        "function _verificarYAutoLogonear($module_name, $autoStartSession = false)\n"
        "{\n"
        "    global $arrConf;\n\n"
        "    if (!isset($_SESSION['issabel_user'])) return false;\n\n"
        "    $pACL = new paloACL($arrConf['issabel_dsn']['acl']);\n"
        "    $idUser = $pACL->getIdUser($_SESSION['issabel_user']);\n"
        "    if ($idUser === FALSE) return false;\n\n"
        "    $tupla = $pACL->getUsers($idUser);\n"
        "    if (!is_array($tupla) || count($tupla) <= 0) return false;\n\n"
        "    $sipExtension = $tupla[0][3];\n"
        "    if (empty($sipExtension)) return false;\n\n"
        "    $oPaloConsola = new PaloSantoConsola();\n"
        "    $listaExtensionesCallback = $oPaloConsola->listarAgentes('dynamic');\n\n"
        "    $sSelectedAgent = 'PJSIP/' . $sipExtension;\n"
        "    foreach (array_keys($listaExtensionesCallback) as $k) {\n"
        "        $regs = NULL;\n"
        "        if (preg_match('|^(\\w+)/(\\d+)$|', $k, $regs) && $regs[2] == $sipExtension) {\n"
        "            $sSelectedAgent = $k;\n"
        "            break;\n"
        "        }\n"
        "    }\n\n"
        "    $oPaloConsolaCheck = new PaloSantoConsola($sSelectedAgent);\n"
        "    $estado = $oPaloConsolaCheck->estadoAgenteLogoneado($sipExtension);\n"
        "    $bIsLoggedIn = ($estado['estadofinal'] == 'logged-in');\n\n"
        "    if ($bIsLoggedIn && $autoStartSession) {\n"
        "        $_SESSION['callcenter']['estado_consola'] = 'logged-in';\n"
        "        $_SESSION['callcenter']['agente'] = $sSelectedAgent;\n"
        "        $_SESSION['callcenter']['agente_nombre'] = isset($listaExtensionesCallback[$sSelectedAgent]) ? $listaExtensionesCallback[$sSelectedAgent] : $sSelectedAgent;\n"
        "        $_SESSION['callcenter']['extension'] = $sipExtension;\n"
        "    }\n\n"
        "    $oPaloConsolaCheck->desconectarTodo();\n"
        "    $oPaloConsola->desconectarTodo();\n\n"
        "    return $bIsLoggedIn;\n"
        "}\n\n"
        "function manejarLogin_checkAutoLogin($module_name)\n"
        "{\n"
        "    $respuesta = array(\n"
        "        'status' => _verificarYAutoLogonear($module_name, true),\n"
        "    );\n"
        "    header('Content-Type: application/json');\n"
        "    echo json_encode($respuesta);\n"
        "    exit();\n"
        "}\n\n"
        "// Mostrar el formulario donde el agente ingresa su login"
    )

    if helper_funcs_target not in php_content_norm:
        print("Error: Helper functions insertion target not found in PHP file")
        return 1
    php_content_norm = php_content_norm.replace(helper_funcs_target, helper_funcs_replace)

    # Save PHP file
    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)
    print("Success: Updated modules/agent_console/index.php")


    # 2. Modify JS file
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Add start_check_autologin call inside $(document).ready
    js_ready_target = (
        "    // Operaciones que deben de repetirse al obtener formulario vía AJAX\n"
        "    apply_form_styles();\n\n"
        "    $('#submit_agent_login').click(do_login);"
    )
    js_ready_replace = (
        "    // Operaciones que deben de repetirse al obtener formulario vía AJAX\n"
        "    apply_form_styles();\n\n"
        "    $('#submit_agent_login').click(do_login);\n"
        "    if ($('#submit_agent_login').length > 0) {\n"
        "        start_check_autologin();\n"
        "    }"
    )

    if js_ready_target not in js_content_norm:
        print("Error: JS ready target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_ready_target, js_ready_replace)

    # Add start_check_autologin definition before do_login
    js_func_target = (
        "// El siguiente código se ejecutará cuando se presione el botón de login del agente\n"
        "function do_login()"
    )
    js_func_replace = (
        "function start_check_autologin()\n"
        "{\n"
        "    setTimeout(function check() {\n"
        "        if ($('#submit_agent_login').length === 0) return; // Parar si ya no está en login\n"
        "        \n"
        "        // Si ya está en espera del login, no hacer autologin\n"
        "        if ($('#login_icono_espera').css('visibility') === 'visible') {\n"
        "            setTimeout(check, 3000);\n"
        "            return;\n"
        "        }\n"
        "        \n"
        "        $.post('index.php?menu=' + module_name + '&rawmode=yes', {\n"
        "            menu:       module_name,\n"
        "            rawmode:    'yes',\n"
        "            action:     'checkAutoLogin'\n"
        "        }, function(response) {\n"
        "            if (response && response.status === true) {\n"
        "                window.location.reload();\n"
        "            } else {\n"
        "                setTimeout(check, 3000);\n"
        "            }\n"
        "        }, 'json').fail(function() {\n"
        "            setTimeout(check, 5000);\n"
        "        });\n"
        "    }, 3000);\n"
        "}\n\n"
        "// El siguiente código se ejecutará cuando se presione el botón de login del agente\n"
        "function do_login()"
    )

    if js_func_target not in js_content_norm:
        print("Error: JS function target not found in javascript.js")
        return 1
    js_content_norm = js_content_norm.replace(js_func_target, js_func_replace)

    # Save JS file
    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Updated modules/agent_console/themes/default/js/javascript.js")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
