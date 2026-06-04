import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")

    print("=== WebPhone Login Screen Directory Fix ===")

    # 1. Update index.php to bypass console login check for getExtensionsList
    if os.path.exists(index_php):
        with open(index_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_str = """    /* Al iniciar la sesión del agente, se asignan las variables elastix_agent_user y elastix_extension  */
    if ($_SESSION['callcenter']['estado_consola'] == 'logged-in') {"""

        replacement_str = """    // Allow extensions directory AJAX loading regardless of console state
    if (isset($_REQUEST['action']) && $_REQUEST['action'] == 'getExtensionsList') {
        return manejarSesionActiva_getExtensionsList($module_name, $smarty, $sDirLocalPlantillas, null, null);
    }

    /* Al iniciar la sesión del agente, se asignan las variables elastix_agent_user y elastix_extension  */
    if ($_SESSION['callcenter']['estado_consola'] == 'logged-in') {"""

        if target_str in content:
            content = content.replace(target_str, replacement_str)
            # Bump cache versions to v=9
            content = content.replace("webphone.css?v=8", "webphone.css?v=9")
            content = content.replace("sip-phone.js?v=8", "sip-phone.js?v=9")
            
            with open(index_php, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully patched index.php to allow getExtensionsList from login screen, and bumped cache to v=9.")
        else:
            print("Target pattern for session check not found in index.php or already patched.")
    else:
        print(f"Error: index.php not found at {index_php}")
        return 1

    # 2. Update agent_console.tpl to bump cache version to v=9
    if os.path.exists(agent_console_tpl):
        with open(agent_console_tpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("webphone.css?v=8", "webphone.css?v=9")
        content = content.replace("sip-phone.js?v=8", "sip-phone.js?v=9")
        
        with open(agent_console_tpl, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated agent_console.tpl cache strings to v=9")
    else:
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    print("Login directory fix applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
