import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")

    print("Starting visual improvements V4 (filtering summary cards by extension)...")

    if os.path.exists(js_file):
        print(f"Modifying JS: {js_file}")
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        js_content_norm = js_content.replace('\r\n', '\n')

        old_resumen_agentes = (
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
            "\t\t}.property('agentes.@each.estado'),"
        )

        new_resumen_agentes = (
            "\t\tresumenAgentes: function() {\n"
            "\t\t\tvar agentes = this.get('agentes') || [];\n"
            "\t\t\tvar extPrefix = this.get('filtroExtension');\n"
            "\n"
            "\t\t\t// Filtrar agentes por el prefijo de la extensión\n"
            "\t\t\tif (extPrefix && extPrefix.trim() !== '') {\n"
            "\t\t\t\tvar prefix = extPrefix.trim();\n"
            "\t\t\t\tagentes = agentes.filter(function(agent) {\n"
            "\t\t\t\t\tvar canal = agent.get('canal') || '';\n"
            "\t\t\t\t\tvar matches = canal.match(/(?:PJSIP|SIP|IAX2|Local)\\/(\\d+)/i);\n"
            "\t\t\t\t\tvar ext = matches ? matches[1] : '';\n"
            "\t\t\t\t\treturn ext.indexOf(prefix) === 0;\n"
            "\t\t\t\t});\n"
            "\t\t\t}\n"
            "\n"
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
            "\t\t}.property('agentes.@each.estado', 'filtroExtension'),"
        )

        if old_resumen_agentes not in js_content_norm:
            # Try spaces normalization
            old_resumen_agentes_alt = old_resumen_agentes.replace('\t', '    ')
            if old_resumen_agentes_alt not in js_content_norm:
                print("Error: old_resumen_agentes function block not found in JS file.")
                return 1
            else:
                js_content_norm = js_content_norm.replace(old_resumen_agentes_alt, new_resumen_agentes)
                print("resumenAgentes replaced successfully (alt).")
        else:
            js_content_norm = js_content_norm.replace(old_resumen_agentes, new_resumen_agentes)
            print("resumenAgentes replaced successfully.")

        if '\r\n' in js_content:
            js_content_norm = js_content_norm.replace('\n', '\r\n')

        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content_norm)
        print("JS successfully updated.")
        return 0
    else:
        print(f"Error: JS file not found at {js_file}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
