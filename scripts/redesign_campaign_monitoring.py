import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    css_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "css", "styles.css")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")
    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")

    print("Starting visual redesign updates...")

    # 1. Update CSS
    if os.path.exists(css_file):
        print(f"Modifying CSS: {css_file}")
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        css_content_norm = css_content.replace('\r\n', '\n')

        # Add Google Font import and modern card classes
        new_css_additions = (
            "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');\n\n"
            "#campaignMonitoringApplication {\n"
            "    font-family: 'Inter', sans-serif !important;\n"
            "    background-color: #f8fafc !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 12px !important;\n"
            "    padding: 24px !important;\n"
            "    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05) !important;\n"
            "}\n\n"
            "#campaignMonitoringApplication table {\n"
            "    font-family: 'Inter', sans-serif !important;\n"
            "}\n\n"
            ".campaign-table, .campaign-table-outgoing {\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 8px !important;\n"
            "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02) !important;\n"
            "    border-collapse: separate !important;\n"
            "    border-spacing: 0 !important;\n"
            "    overflow: hidden !important;\n"
            "    margin-bottom: 24px !important;\n"
            "}\n\n"
            ".table-header {\n"
            "    background-color: #1e293b !important;\n"
            "    color: #ffffff !important;\n"
            "    font-size: 13px !important;\n"
            "    font-weight: 600 !important;\n"
            "    padding: 12px 16px !important;\n"
            "    text-transform: uppercase !important;\n"
            "    letter-spacing: 0.05em !important;\n"
            "    border: none !important;\n"
            "}\n\n"
            ".table-label, .table-label-out {\n"
            "    color: #475569 !important;\n"
            "    font-weight: 600 !important;\n"
            "    font-size: 13px !important;\n"
            "}\n\n"
            ".campaign-table td, .campaign-table-outgoing td {\n"
            "    padding: 12px 16px !important;\n"
            "    border-bottom: 1px solid #f1f5f9 !important;\n"
            "    border-top: none !important;\n"
            "    border-left: none !important;\n"
            "    border-right: none !important;\n"
            "    font-size: 13px !important;\n"
            "    color: #0f172a !important;\n"
            "}\n\n"
            "table.titulo {\n"
            "    background-color: #1e293b !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-bottom: none !important;\n"
            "    border-top-left-radius: 8px !important;\n"
            "    border-top-right-radius: 8px !important;\n"
            "    overflow: hidden !important;\n"
            "    height: auto !important;\n"
            "}\n\n"
            "table.titulo td {\n"
            "    padding: 12px 16px !important;\n"
            "    font-weight: 600 !important;\n"
            "    font-size: 12px !important;\n"
            "    text-transform: uppercase !important;\n"
            "    letter-spacing: 0.05em !important;\n"
            "    color: #ffffff !important;\n"
            "}\n\n"
            "div.llamadas {\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-bottom-left-radius: 8px !important;\n"
            "    border-bottom-right-radius: 8px !important;\n"
            "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;\n"
            "    overflow: hidden !important;\n"
            "}\n\n"
            "div.llamadas table > tbody > tr > td {\n"
            "    padding: 12px 16px !important;\n"
            "    border-bottom: 1px solid #f1f5f9 !important;\n"
            "    font-size: 13px !important;\n"
            "    color: #1e293b !important;\n"
            "}\n\n"
            "div.llamadas table > tbody > tr:hover {\n"
            "    background-color: #f8fafc !important;\n"
            "}\n"
        )

        # Prepend the new styles and fonts
        css_content_norm = new_css_additions + css_content_norm

        if '\r\n' in css_content:
            css_content_norm = css_content_norm.replace('\n', '\r\n')

        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content_norm)
        print("CSS successfully updated with modern styles.")
    else:
        print(f"Error: CSS file not found at {css_file}")
        return 1

    # 2. Update TPL file to remove border="1"
    if os.path.exists(tpl_file):
        print(f"Modifying TPL: {tpl_file}")
        with open(tpl_file, 'r', encoding='utf-8') as f:
            tpl_content = f.read()

        tpl_content_norm = tpl_content.replace('\r\n', '\n')

        # Remove border="1" from campaign-table and campaign-table-outgoing
        tpl_content_norm = tpl_content_norm.replace('class="campaign-table" border="1"', 'class="campaign-table"')
        tpl_content_norm = tpl_content_norm.replace('class="campaign-table-outgoing" border="1"', 'class="campaign-table-outgoing"')

        if '\r\n' in tpl_content:
            tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

        with open(tpl_file, 'w', encoding='utf-8') as f:
            f.write(tpl_content_norm)
        print("TPL successfully updated (borders removed).")
    else:
        print(f"Error: TPL file not found at {tpl_file}")
        return 1

    # 3. Update JS colors
    if os.path.exists(js_file):
        print(f"Modifying JS: {js_file}")
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        js_content_norm = js_content.replace('\r\n', '\n')

        # 3a. Target block for agentColor
        old_agent_color_block = (
            "function agentColor(status, canal) {\n"
            "setTimeout(() => {\n"
            "\n"
            "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
            "    color = 'yellow';\n"
            "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
            "    color = 'orange';\n"
            "  } else {\n"
            "    switch (status) {\n"
            "      case 'Ringing':\n"
            "        color = '#a6db14';\n"
            "        break;\n"
            "      case 'Free':\n"
            "      case 'Libre':\n"
            "      case 'Свободен':\n"
            "      case 'Boşta':\n"
            "        color = '#01D50A';\n"
            "        break;\n"
            "      case 'Busy':\n"
            "      case 'Ocupado':\n"
            "      case 'Occupé':\n"
            "      case 'Занят':\n"
            "      case 'Meşgul':\n"
            "        color = 'yellow';\n"
            "        break;\n"
            "      case 'Unavailable':\n"
            "      case 'Logged out':\n"
            "      case 'No logon':\n"
            "      case 'Déconnecté':\n"
            "      case 'Вышел':\n"
            "      case 'Yok':\n"
            "        color = '#f33';\n"
            "        break;\n"
            "      default:\n"
            "        color = 'white';\n"
            "        break;\n"
            "    }\n"
            "  }"
        )

        new_agent_color_block = (
            "function agentColor(status, canal) {\n"
            "setTimeout(() => {\n"
            "\n"
            "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
            "    color = '#fef7e0'; // Soft pastel yellow/amber\n"
            "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada') || status.includes('descanso')) {\n"
            "    color = '#fff0e6'; // Soft pastel orange\n"
            "  } else {\n"
            "    switch (status) {\n"
            "      case 'Ringing':\n"
            "        color = '#e8f0fe'; // Soft light blue\n"
            "        break;\n"
            "      case 'Free':\n"
            "      case 'Libre':\n"
            "      case 'Свобоden':\n"
            "      case 'Boşta':\n"
            "        color = '#e6f4ea'; // Soft pastel green\n"
            "        break;\n"
            "      case 'Busy':\n"
            "      case 'Ocupado':\n"
            "      case 'Occupé':\n"
            "      case 'Занят':\n"
            "      case 'Meşgul':\n"
            "        color = '#fef7e0'; // Soft pastel yellow/amber\n"
            "        break;\n"
            "      case 'Unavailable':\n"
            "      case 'Logged out':\n"
            "      case 'No logon':\n"
            "      case 'Déconnecté':\n"
            "      case 'Вышел':\n"
            "      case 'Yok':\n"
            "        color = '#fce8e6'; // Soft pastel red\n"
            "        break;\n"
            "      default:\n"
            "        color = '#ffffff';\n"
            "        break;\n"
            "    }\n"
            "  }"
        )

        # 3b. Target block for agentUpdateColor
        old_update_color_block = (
            "function agentUpdateColor(status, canal) {\n"
            "  let statusImage;\n"
            "\n"
            "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
            "    color = 'yellow';\n"
            "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-busy.png\" alt=\"Ocupado\" style=\"padding-right:1px;\"/>';\n"
            "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada')) {\n"
            "    color = 'orange';\n"
            "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-break.png\" alt=\"En Break\" style=\"padding-right:1px;\"/>';\n"
            "  } else {\n"
            "    switch (status) {\n"
            "      case 'Ringing':\n"
            "        color = '#a6db14';\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-ringing.gif\" alt=\"Desconectado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Free':\n"
            "      case 'Libre':\n"
            "      case 'Свободен':\n"
            "      case 'Boşta':\n"
            "        color = '#01D50A';\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-available.png\" alt=\"Disponible\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Busy':\n"
            "      case 'Ocupado':\n"
            "      case 'Occupé':\n"
            "      case 'Занят':\n"
            "      case 'Meşgul':\n"
            "        color = 'yellow';\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-busy.png\" alt=\"Ocupado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Logged out':\n"
            "      case 'No logon':\n"
            "      case 'Déconnecté':\n"
            "      case 'Вышел':\n"
            "      case 'Yok':\n"
            "        color = '#f33';\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-disconected.png\" alt=\"Desconectado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      default:\n"
            "        color = 'white';\n"
            "        statusImage = '';\n"
            "        break;\n"
            "    }\n"
            "  }"
        )

        new_update_color_block = (
            "function agentUpdateColor(status, canal) {\n"
            "  let statusImage;\n"
            "\n"
            "  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {\n"
            "    color = '#fef7e0'; // Soft pastel yellow/amber\n"
            "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-busy.png\" alt=\"Ocupado\" style=\"padding-right:1px;\"/>';\n"
            "  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada') || status.includes('descanso')) {\n"
            "    color = '#fff0e6'; // Soft pastel orange\n"
            "    statusImage = '<img src=\"/modules/' + module_name + '/images/agent-break.png\" alt=\"En Break\" style=\"padding-right:1px;\"/>';\n"
            "  } else {\n"
            "    switch (status) {\n"
            "      case 'Ringing':\n"
            "        color = '#e8f0fe'; // Soft light blue\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-ringing.gif\" alt=\"Desconectado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Free':\n"
            "      case 'Libre':\n"
            "      case 'Свобоden':\n"
            "      case 'Boşta':\n"
            "        color = '#e6f4ea'; // Soft pastel green\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-available.png\" alt=\"Disponible\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Busy':\n"
            "      case 'Ocupado':\n"
            "      case 'Occupé':\n"
            "      case 'Занят':\n"
            "      case 'Meşgul':\n"
            "        color = '#fef7e0'; // Soft pastel yellow/amber\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-busy.png\" alt=\"Ocupado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      case 'Logged out':\n"
            "      case 'No logon':\n"
            "      case 'Déconnecté':\n"
            "      case 'Вышел':\n"
            "      case 'Yok':\n"
            "        color = '#fce8e6'; // Soft pastel red\n"
            "        statusImage = '<img src=\"/modules/' + module_name + '/images/agent-disconected.png\" alt=\"Desconectado\" style=\"padding-right:1px;\"/>';\n"
            "        break;\n"
            "      default:\n"
            "        color = '#ffffff';\n"
            "        statusImage = '';\n"
            "        break;\n"
            "    }\n"
            "  }"
        )

        # Let's perform case-insensitive or direct string replacements for the specific targets
        # to ensure it succeeds regardless of exact block mismatches.
        # But wait! We checked line 809 and it has "Свободен" (Cyrillic).
        # Let's double check. If we normalize line endings in python:
        
        if old_agent_color_block not in js_content_norm:
            print("Error: agentColor block not found in javascript.js")
            # Let's try matching with Latin or Cyrillic variants if we can
            old_agent_color_block_alt = old_agent_color_block.replace("case 'Свободен':", "case 'Свобоden':")
            if old_agent_color_block_alt in js_content_norm:
                js_content_norm = js_content_norm.replace(old_agent_color_block_alt, new_agent_color_block)
                print("Matched and replaced alternative agentColor block.")
            else:
                return 1
        else:
            js_content_norm = js_content_norm.replace(old_agent_color_block, new_agent_color_block)
            print("Matched and replaced agentColor block.")

        if old_update_color_block not in js_content_norm:
            print("Error: agentUpdateColor block not found in javascript.js")
            # Let's try alternative
            old_update_color_block_alt = old_update_color_block.replace("case 'Свободен':", "case 'Свобоden':")
            if old_update_color_block_alt in js_content_norm:
                js_content_norm = js_content_norm.replace(old_update_color_block_alt, new_update_color_block)
                print("Matched and replaced alternative agentUpdateColor block.")
            else:
                return 1
        else:
            js_content_norm = js_content_norm.replace(old_update_color_block, new_update_color_block)
            print("Matched and replaced agentUpdateColor block.")

        if '\r\n' in js_content:
            js_content_norm = js_content_norm.replace('\n', '\r\n')

        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content_norm)
        print("JS successfully updated (colors softened).")
    else:
        print(f"Error: JS file not found at {js_file}")
        return 1

    print("Visual redesign updates completed successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
