import os

def main():
    # Get workspace root directory (parent of scripts directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(current_dir)
    
    print(f"Workspace root: {workspace_dir}")
    
    # 1. Modify configs/default.conf.php
    config_path = os.path.join(workspace_dir, "modules", "dash_agent_journey", "configs", "default.conf.php")
    if os.path.exists(config_path):
        print(f"Modifying config at {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        target_conf = "$arrConfModule['module_name'] = 'agent_journey';"
        repl_conf = "$arrConfModule['module_name'] = 'dash_agent_journey';"
        
        if target_conf in config_content:
            config_content = config_content.replace(target_conf, repl_conf)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            print("Config file updated successfully.")
        else:
            print("Target module_name config line not found or already modified.")
    else:
        print(f"Config file not found at {config_path}")

    # 2. Modify themes/default/dash_agent_journey.tpl
    tpl_path = os.path.join(workspace_dir, "modules", "dash_agent_journey", "themes", "default", "dash_agent_journey.tpl")
    if os.path.exists(tpl_path):
        print(f"Modifying template at {tpl_path}")
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl_content = f.read()
        
        # Escaping style tag
        if "<style>" in tpl_content and "</style>" in tpl_content:
            if "{literal}" not in tpl_content[tpl_content.find("<style>"):tpl_content.find("</style>")]:
                tpl_content = tpl_content.replace("<style>", "<style>\n{literal}")
                tpl_content = tpl_content.replace("</style>", "{/literal}\n</style>")
                print("Style tag escaped with {literal}.")
        
        # Escaping script tag and passing Smarty MODULE_NAME variable to JS
        if "<script>" in tpl_content and "</script>" in tpl_content:
            script_start = tpl_content.find("<script>")
            script_end = tpl_content.find("</script>")
            script_block = tpl_content[script_start:script_end]
            
            if "var moduleName =" not in script_block:
                # We do the replacement
                target_script = "<script>\nvar activityChartInstance = null;"
                repl_script = "<script>\nvar moduleName = '{$MODULE_NAME}';\n{literal}\nvar activityChartInstance = null;"
                
                target_url_params = "menu: '{$MODULE_NAME}',"
                repl_url_params = "menu: moduleName,"
                
                target_script_end = "</script>"
                repl_script_end = "{/literal}\n</script>"
                
                tpl_content = tpl_content.replace(target_script, repl_script)
                tpl_content = tpl_content.replace(target_url_params, repl_url_params)
                tpl_content = tpl_content.replace(target_script_end, repl_script_end)
                
                print("Script tag escaped with {literal} and moduleName variable exposed.")
            else:
                print("Script block already modified.")
                
        with open(tpl_path, "w", encoding="utf-8") as f:
            f.write(tpl_content)
    else:
        print(f"Template file not found at {tpl_path}")

    # 3. Modify language files (es.lang and en.lang)
    es_lang_path = os.path.join(workspace_dir, "modules", "dash_agent_journey", "lang", "es.lang")
    en_lang_path = os.path.join(workspace_dir, "modules", "dash_agent_journey", "lang", "en.lang")
    
    # Update es.lang
    if os.path.exists(es_lang_path):
        print(f"Modifying es.lang at {es_lang_path}")
        with open(es_lang_path, "r", encoding="utf-8") as f:
            es_content = f.read()
        
        if "Dash Agent Journey" not in es_content:
            es_content = es_content.replace(");\n?>", "    \"Dash Agent Journey\" => \"Dashboard de Jornada de Agente\",\n);\n?>")
            es_content = es_content.replace(");\r\n?>", "    \"Dash Agent Journey\" => \"Dashboard de Jornada de Agente\",\r\n);\r\n?>")
            with open(es_lang_path, "w", encoding="utf-8") as f:
                f.write(es_content)
            print("es.lang updated.")
        else:
            print("es.lang already has translation.")
            
    # Update en.lang
    if os.path.exists(en_lang_path):
        print(f"Modifying en.lang at {en_lang_path}")
        with open(en_lang_path, "r", encoding="utf-8") as f:
            en_content = f.read()
            
        if "Dash Agent Journey" not in en_content:
            en_content = en_content.replace(");\n?>", "    \"Dash Agent Journey\" => \"Dash Agent Journey\",\n);\n?>")
            en_content = en_content.replace(");\r\n?>", "    \"Dash Agent Journey\" => \"Dash Agent Journey\",\r\n);\r\n?>")
            with open(en_lang_path, "w", encoding="utf-8") as f:
                f.write(en_content)
            print("en.lang updated.")
        else:
            print("en.lang already has translation.")

if __name__ == "__main__":
    main()
