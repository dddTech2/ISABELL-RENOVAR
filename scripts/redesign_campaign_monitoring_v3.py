import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    css_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "css", "styles.css")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")
    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")

    print("Starting visual improvements V3 (scrolling, filters, and summary cards)...")

    # 1. Update CSS with summary card and filter styles
    if os.path.exists(css_file):
        print(f"Modifying CSS: {css_file}")
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        css_content_norm = css_content.replace('\r\n', '\n')

        filter_css = (
            "\n/* Custom filters and summary styles */\n"
            ".summary-wrapper {\n"
            "    display: flex !important;\n"
            "    gap: 12px !important;\n"
            "    margin-bottom: 16px !important;\n"
            "    width: 100% !important;\n"
            "}\n\n"
            ".summary-card {\n"
            "    flex: 1 !important;\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 8px !important;\n"
            "    padding: 8px 12px !important;\n"
            "    display: flex !important;\n"
            "    flex-direction: column !important;\n"
            "    align-items: center !important;\n"
            "    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;\n"
            "}\n\n"
            ".summary-num {\n"
            "    font-size: 18px !important;\n"
            "    font-weight: 700 !important;\n"
            "    color: #0f172a !important;\n"
            "}\n\n"
            ".summary-lbl {\n"
            "    font-size: 11px !important;\n"
            "    color: #64748b !important;\n"
            "    font-weight: 500 !important;\n"
            "    text-transform: uppercase !important;\n"
            "    margin-top: 2px !important;\n"
            "}\n\n"
            ".summary-card.status-free {\n"
            "    border-left: 4px solid #137333 !important;\n"
            "}\n"
            ".summary-card.status-free .summary-num {\n"
            "    color: #137333 !important;\n"
            "}\n\n"
            ".summary-card.status-busy {\n"
            "    border-left: 4px solid #b06000 !important;\n"
            "}\n"
            ".summary-card.status-busy .summary-num {\n"
            "    color: #b06000 !important;\n"
            "}\n\n"
            ".summary-card.status-break {\n"
            "    border-left: 4px solid #a64d14 !important;\n"
            "}\n"
            ".summary-card.status-break .summary-num {\n"
            "    color: #a64d14 !important;\n"
            "}\n\n"
            ".summary-card.status-offline {\n"
            "    border-left: 4px solid #c5221f !important;\n"
            "}\n"
            ".summary-card.status-offline .summary-num {\n"
            "    color: #c5221f !important;\n"
            "}\n\n"
            ".filters-wrapper {\n"
            "    display: flex !important;\n"
            "    gap: 16px !important;\n"
            "    margin-bottom: 12px !important;\n"
            "    align-items: center !important;\n"
            "}\n\n"
            ".filter-item {\n"
            "    display: flex !important;\n"
            "    align-items: center !important;\n"
            "    gap: 8px !important;\n"
            "}\n\n"
            ".filter-item label {\n"
            "    font-size: 12px !important;\n"
            "    font-weight: 600 !important;\n"
            "    color: #475569 !important;\n"
            "}\n\n"
            ".filter-select {\n"
            "    padding: 6px 10px !important;\n"
            "    font-size: 12px !important;\n"
            "    border-radius: 6px !important;\n"
            "    border: 1px solid #cbd5e1 !important;\n"
            "    outline: none !important;\n"
            "}\n\n"
            ".filter-input {\n"
            "    padding: 6px 10px !important;\n"
            "    font-size: 12px !important;\n"
            "    border-radius: 6px !important;\n"
            "    border: 1px solid #cbd5e1 !important;\n"
            "    outline: none !important;\n"
            "    width: 100px !important;\n"
            "}\n"
        )

        css_content_norm += filter_css

        if '\r\n' in css_content:
            css_content_norm = css_content_norm.replace('\n', '\r\n')

        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content_norm)
        print("CSS successfully updated with filter and summary styles.")
    else:
        print(f"Error: CSS file not found at {css_file}")
        return 1

    # 2. Update TPL file to add summary cards and filters
    if os.path.exists(tpl_file):
        print(f"Modifying TPL: {tpl_file}")
        with open(tpl_file, 'r', encoding='utf-8') as f:
            tpl_content = f.read()

        tpl_content_norm = tpl_content.replace('\r\n', '\n')

        # Insert filter & summary panel before table.titulo inside agents column (td width="65%")
        old_agents_header = "    <td width=\"65%\" style=\"vertical-align: top;\">\n        <b>{$ETIQUETA_AGENTES}:</b>"
        new_agents_header = (
            "    <td width=\"65%\" style=\"vertical-align: top;\">\n"
            "        <b>{$ETIQUETA_AGENTES}:</b>\n"
            "        {literal}\n"
            "        <!-- Resumen de Agentes -->\n"
            "        <div class=\"summary-wrapper\">\n"
            "            <div class=\"summary-card\">\n"
            "                <span class=\"summary-num\">{{resumenAgentes.total}}</span>\n"
            "                <span class=\"summary-lbl\">Total</span>\n"
            "            </div>\n"
            "            <div class=\"summary-card status-free\">\n"
            "                <span class=\"summary-num\">{{resumenAgentes.libre}}</span>\n"
            "                <span class=\"summary-lbl\">Libres</span>\n"
            "            </div>\n"
            "            <div class=\"summary-card status-busy\">\n"
            "                <span class=\"summary-num\">{{resumenAgentes.ocupado}}</span>\n"
            "                <span class=\"summary-lbl\">Ocupados</span>\n"
            "            </div>\n"
            "            <div class=\"summary-card status-break\">\n"
            "                <span class=\"summary-num\">{{resumenAgentes.descanso}}</span>\n"
            "                <span class=\"summary-lbl\">Descanso</span>\n"
            "            </div>\n"
            "            <div class=\"summary-card status-offline\">\n"
            "                <span class=\"summary-num\">{{resumenAgentes.nologon}}</span>\n"
            "                <span class=\"summary-lbl\">No logon</span>\n"
            "            </div>\n"
            "        </div>\n"
            "\n"
            "        <!-- Filtros de Agentes -->\n"
            "        <div class=\"filters-wrapper\">\n"
            "            <div class=\"filter-item\">\n"
            "                <label>Estado:</label>\n"
            "                {{view Ember.Select\n"
            "                    contentBinding=\"App.estadosFiltro\"\n"
            "                    valueBinding=\"filtroEstado\"\n"
            "                    class=\"filter-select\" }}\n"
            "            </div>\n"
            "            <div class=\"filter-item\">\n"
            "                <label>Prefijo Extensión:</label>\n"
            "                {{view Ember.TextField\n"
            "                    valueBinding=\"filtroExtension\"\n"
            "                    placeholder=\"Ej. 20\"\n"
            "                    class=\"filter-input\" }}\n"
            "            </div>\n"
            "        </div>\n"
            "        {/literal}"
        )

        if old_agents_header not in tpl_content_norm:
            print("Error: Agents header not found in TPL file")
            return 1

        tpl_content_norm = tpl_content_norm.replace(old_agents_header, new_agents_header)

        # Replace {{#each agentes}} with {{#each agentesFiltrados}}
        tpl_content_norm = tpl_content_norm.replace('{{#each agentes}}', '{{#each agentesFiltrados}}')

        if '\r\n' in tpl_content:
            tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

        with open(tpl_file, 'w', encoding='utf-8') as f:
            f.write(tpl_content_norm)
        print("TPL successfully updated with filters and summary panel.")
    else:
        print(f"Error: TPL file not found at {tpl_file}")
        return 1

    # 3. Update JS to add filter properties, computed fields, and optimize sort/render
    if os.path.exists(js_file):
        print(f"Modifying JS: {js_file}")
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        js_content_norm = js_content.replace('\r\n', '\n')

        # Define App.estadosFiltro right before CampaignDetailsController
        old_controller_start = "	App.CampaignDetailsController = Ember.ObjectController.extend({"
        new_controller_start = (
            "	App.estadosFiltro = ['Todos', 'Libre', 'Ocupado', 'En descanso', 'No logon'];\n\n"
            "	App.CampaignDetailsController = Ember.ObjectController.extend({"
        )

        if old_controller_start not in js_content_norm:
            print("Error: CampaignDetailsController definition start not found in JS file")
            return 1

        js_content_norm = js_content_norm.replace(old_controller_start, new_controller_start)

        # Add properties and computed properties inside App.CampaignDetailsController
        old_properties_block = (
            "\t\tllamadas:       \tnull,\n"
            "\t\tllamadasMarcando:\tnull,\n"
            "\t\tagentes:\t\t\tnull,\n"
            "\t\tregistroVisible: false,\n"
            "\t\tregistro:\t\t\tnull,"
        )

        new_properties_block = (
            "\t\tllamadas:       \tnull,\n"
            "\t\tllamadasMarcando:\tnull,\n"
            "\t\tagentes:\t\t\tnull,\n"
            "\t\tregistroVisible: false,\n"
            "\t\tregistro:\t\t\tnull,\n"
            "\t\tfiltroEstado: 'Todos',\n"
            "\t\tfiltroExtension: '',\n"
            "\n"
            "\t\tresumenAgentes: function() {\n"
            "\t\t\tvar agentes = this.get('agentes') || [];\n"
            "\t\t\tvar total = agentes.length;\n"
            "\t\t\tvar libre = 0;\n"
            "\t\t\tvar ocupado = 0;\n"
            "\t\t\tvar descanso = 0;\n"
            "\t\t\tvar nologon = 0;\n"
            "\n"
            "\t\t\tagentes.forEach(function(agent) {\n"
            "\t\t\t\tvar statusLower = (agent.get('estado') || '').toLowerCase();\n"
            "\t\t\t\tvar isLoggedOut = statusLower.indexOf('no logon') !== -1 || \n"
            "\t\t\t\t                  statusLower.indexOf('logged out') !== -1 || \n"
            "\t\t\t\t                  statusLower.indexOf('no logoneado') !== -1 ||\n"
            "\t\t\t\t                  statusLower.indexOf('déconnecté') !== -1;\n"
            "\t\t\t\tvar isFree = statusLower.indexOf('libre') !== -1 || \n"
            "\t\t\t\t             statusLower.indexOf('free') !== -1 || \n"
            "\t\t\t\t             statusLower.indexOf('boşta') !== -1;\n"
            "\t\t\t\tvar isBusy = statusLower.indexOf('ocupado') !== -1 || \n"
            "\t\t\t\t             statusLower.indexOf('busy') !== -1 || \n"
            "\t\t\t\t             statusLower.indexOf('oncall') !== -1 ||\n"
            "\t\t\t\t             statusLower.indexOf('on call') !== -1;\n"
            "\t\t\t\tvar isBreak = statusLower.indexOf('break') !== -1 || \n"
            "\t\t\t\t              statusLower.indexOf('descanso') !== -1 || \n"
            "\t\t\t\t              statusLower.indexOf('pause') !== -1 || \n"
            "\t\t\t\t              statusLower.indexOf('paused') !== -1;\n"
            "\n"
            "\t\t\t\tif (isLoggedOut) nologon++;\n"
            "\t\t\t\telse if (isBusy) ocupado++;\n"
            "\t\t\t\telse if (isBreak) descanso++;\n"
            "\t\t\t\telse if (isFree) libre++;\n"
            "\t\t\t});\n"
            "\n"
            "\t\t\treturn {\n"
            "\t\t\t\ttotal: total,\n"
            "\t\t\t\tlibre: libre,\n"
            "\t\t\t\tocupado: ocupado,\n"
            "\t\t\t\tdescanso: descanso,\n"
            "\t\t\t\tnologon: nologon\n"
            "\t\t\t};\n"
            "\t\t}.property('agentes.@each.estado'),\n"
            "\n"
            "\t\tagentesFiltrados: function() {\n"
            "\t\t\tvar estado = this.get('filtroEstado');\n"
            "\t\t\tvar extPrefix = this.get('filtroExtension');\n"
            "\t\t\tvar agentes = this.get('agentes');\n"
            "\t\t\tif (!agentes) return [];\n"
            "\n"
            "\t\t\treturn agentes.filter(function(agent) {\n"
            "\t\t\t\t// 1. Filtrar por estado\n"
            "\t\t\t\tif (estado !== 'Todos') {\n"
            "\t\t\t\t\tvar agentStatus = agent.get('estado') || '';\n"
            "\t\t\t\t\tvar statusLower = agentStatus.toLowerCase();\n"
            "\t\t\t\t\t\n"
            "\t\t\t\t\tif (estado === 'No logon') {\n"
            "\t\t\t\t\t\tvar isLoggedOut = statusLower.indexOf('no logon') !== -1 || \n"
            "\t\t\t\t\t\t                  statusLower.indexOf('logged out') !== -1 || \n"
            "\t\t\t\t\t\t                  statusLower.indexOf('no logoneado') !== -1 ||\n"
            "\t\t\t\t\t\t                  statusLower.indexOf('déconnecté') !== -1;\n"
            "\t\t\t\t\t\tif (!isLoggedOut) return false;\n"
            "\t\t\t\t\t} else if (estado === 'Libre') {\n"
            "\t\t\t\t\t\tvar isFree = statusLower.indexOf('libre') !== -1 || \n"
            "\t\t\t\t\t\t             statusLower.indexOf('free') !== -1 || \n"
            "\t\t\t\t\t\t             statusLower.indexOf('boşta') !== -1;\n"
            "\t\t\t\t\t\tif (!isFree) return false;\n"
            "\t\t\t\t\t} else if (estado === 'Ocupado') {\n"
            "\t\t\t\t\t\tvar isBusy = statusLower.indexOf('ocupado') !== -1 || \n"
            "\t\t\t\t\t\t             statusLower.indexOf('busy') !== -1 || \n"
            "\t\t\t\t\t\t             statusLower.indexOf('oncall') !== -1 ||\n"
            "\t\t\t\t\t\t             statusLower.indexOf('on call') !== -1;\n"
            "\t\t\t\t\t\tif (!isBusy) return false;\n"
            "\t\t\t\t\t} else if (estado === 'En descanso') {\n"
            "\t\t\t\t\t\tvar isBreak = statusLower.indexOf('break') !== -1 || \n"
            "\t\t\t\t\t\t              statusLower.indexOf('descanso') !== -1 || \n"
            "\t\t\t\t\t\t              statusLower.indexOf('pause') !== -1 || \n"
            "\t\t\t\t\t\t              statusLower.indexOf('paused') !== -1;\n"
            "\t\t\t\t\t\tif (!isBreak) return false;\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\n"
            "\t\t\t\t// 2. Filtrar por prefijo de extension\n"
            "\t\t\t\tif (extPrefix && extPrefix.trim() !== '') {\n"
            "\t\t\t\t\tvar prefix = extPrefix.trim();\n"
            "\t\t\t\t\tvar canal = agent.get('canal') || '';\n"
            "\t\t\t\t\tvar matches = canal.match(/(?:PJSIP|SIP|IAX2|Local)\\/(\\d+)/i);\n"
            "\t\t\t\t\tvar ext = matches ? matches[1] : '';\n"
            "\t\t\t\t\tif (ext.indexOf(prefix) !== 0) {\n"
            "\t\t\t\t\t\treturn false;\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\n"
            "\t\t\t\treturn true;\n"
            "\t\t\t});\n"
            "\t\t}.property('agentes.@each.estado', 'agentes.@each.canal', 'filtroEstado', 'filtroExtension'),"
        )

        if old_properties_block not in js_content_norm:
            # Let's try matching with space normalizations
            old_properties_block_alt = old_properties_block.replace("\t", "    ")
            if old_properties_block_alt not in js_content_norm:
                print("Error: Properties block not found in JS file")
                return 1
            else:
                js_content_norm = js_content_norm.replace(old_properties_block_alt, new_properties_block)
                print("Properties block successfully replaced (alt).")
        else:
            js_content_norm = js_content_norm.replace(old_properties_block, new_properties_block)
            print("Properties block successfully replaced.")

        # Rewrite sortAgentsByStatus to prevent unnecessary list clearing and save/restore scrollTop
        old_sort_method = (
            "\t\tsortAgentsByStatus: function() {\n"
            "\t\t\tvar offlineStatuses = ['Logged out', 'No Logoneado', 'Déconnecté', 'Не в системе', 'Oturumu Kapalı'];\n"
            "\t\t\tvar self = this;\n"
            "\t\t\tvar sortedAgents = this.agentes.toArray().sort(function(a, b) {\n"
            "\t\t\t\tvar aOffline = offlineStatuses.indexOf(a.get('estado')) !== -1;\n"
            "\t\t\t\tvar bOffline = offlineStatuses.indexOf(b.get('estado')) !== -1;\n"
            "\t\t\t\tif (aOffline && !bOffline) return 1;\n"
            "\t\t\t\tif (!aOffline && bOffline) return -1;\n"
            "\t\t\t\treturn 0;\n"
            "\t\t\t});\n"
            "\t\t\tthis.agentes.clear();\n"
            "\t\t\tsortedAgents.forEach(function(agent) {\n"
            "\t\t\t\tself.agentes.pushObject(agent);\n"
            "\t\t\t\t// Re-apply color styling after re-adding\n"
            "\t\t\t\tagentColor(agent.get('estado'), agent.get('canal'));\n"
            "\t\t\t});\n"
            "\t\t},"
        )

        new_sort_method = (
            "\t\tsortAgentsByStatus: function() {\n"
            "\t\t\tvar offlineStatuses = ['Logged out', 'No Logoneado', 'Déconnecté', 'Не в системе', 'Oturumu Kapalı', 'No logon'];\n"
            "\t\t\tvar self = this;\n"
            "\t\t\tvar sortedAgents = this.agentes.toArray().sort(function(a, b) {\n"
            "\t\t\t\tvar aOffline = offlineStatuses.indexOf(a.get('estado')) !== -1;\n"
            "\t\t\t\tvar bOffline = offlineStatuses.indexOf(b.get('estado')) !== -1;\n"
            "\t\t\t\tif (aOffline && !bOffline) return 1;\n"
            "\t\t\t\tif (!aOffline && bOffline) return -1;\n"
            "\t\t\t\treturn 0;\n"
            "\t\t\t});\n"
            "\n"
            "\t\t\tvar orderChanged = false;\n"
            "\t\t\tif (this.agentes.length !== sortedAgents.length) {\n"
            "\t\t\t\torderChanged = true;\n"
            "\t\t\t} else {\n"
            "\t\t\t\tfor (var i = 0; i < sortedAgents.length; i++) {\n"
            "\t\t\t\t\tif (this.agentes.objectAt(i) !== sortedAgents[i]) {\n"
            "\t\t\t\t\t\torderChanged = true;\n"
            "\t\t\t\t\t\tbreak;\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
            "\n"
            "\t\t\tif (!orderChanged) {\n"
            "\t\t\t\tthis.agentes.forEach(function(agent) {\n"
            "\t\t\t\t\tagentColor(agent.get('estado'), agent.get('canal'));\n"
            "\t\t\t\t});\n"
            "\t\t\t\treturn;\n"
            "\t\t\t}\n"
            "\n"
            "\t\t\tvar container = $('.agent-table-wrapper');\n"
            "\t\t\tvar scrollTop = container.scrollTop();\n"
            "\n"
            "\t\t\tthis.agentes.clear();\n"
            "\t\t\tsortedAgents.forEach(function(agent) {\n"
            "\t\t\t\tself.agentes.pushObject(agent);\n"
            "\t\t\t\tagentColor(agent.get('estado'), agent.get('canal'));\n"
            "\t\t\t});\n"
            "\n"
            "\t\t\tEmber.run.next(function() {\n"
            "\t\t\t\tcontainer.scrollTop(scrollTop);\n"
            "\t\t\t});\n"
            "\t\t},"
        )

        if old_sort_method not in js_content_norm:
            # Try spaces normalization
            old_sort_method_alt = old_sort_method.replace("\t", "    ")
            if old_sort_method_alt not in js_content_norm:
                print("Error: sortAgentsByStatus method definition not found in JS file")
                return 1
            else:
                js_content_norm = js_content_norm.replace(old_sort_method_alt, new_sort_method)
                print("Sort method successfully updated (alt).")
        else:
            js_content_norm = js_content_norm.replace(old_sort_method, new_sort_method)
            print("Sort method successfully updated.")

        if '\r\n' in js_content:
            js_content_norm = js_content_norm.replace('\n', '\r\n')

        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content_norm)
        print("JS successfully updated with filters, summary controller, and scroll preservation.")
    else:
        print(f"Error: JS file not found at {js_file}")
        return 1

    print("Visual improvements V3 completed successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
