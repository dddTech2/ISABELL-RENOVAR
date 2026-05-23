import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")
    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")

    print(f"Modifying PHP file: {php_file}")
    print(f"Modifying JS file: {js_file}")
    print(f"Modifying template file: {tpl_file}")

    # 1. Modify PHP file
    if not os.path.exists(php_file):
        print(f"Error: PHP file not found at {php_file}")
        return 1

    with open(php_file, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    php_target = (
        "function formatoAgente($agent)\n"
        "{\n"
        "    $sEtiquetaStatus = _tr($agent['status']);\n"
        "    $sFechaHoy = date('Y-m-d');\n"
        "    $sDesde = '-';\n"
        "    switch ($agent['status']) {\n"
        "    case 'paused':\n"
        "        // Prioridad de pausa: hold, break, agendada\n"
        "        if ($agent['onhold']) {\n"
        "            $sEtiquetaStatus = _tr('Hold');\n"
        "            // TODO: desde cuándo está en hold?\n"
        "        } elseif (!is_null($agent['pauseinfo'])) {\n"
        "            $sDesde = $agent['pauseinfo']['pausestart'];\n"
        "            $sEtiquetaStatus .= ': '.$agent['pauseinfo']['pausename'];\n"
        "        }\n"
        "        // TODO: exponer pausa de agendamiento\n"
        "        break;\n"
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        break;\n"
        "    }\n"
        "    if (strpos($sDesde, $sFechaHoy) === 0)\n"
        "        $sDesde = substr($sDesde, strlen($sFechaHoy) + 1);\n"
        "    return array(\n"
        "        'agent'         =>  $agent['agentchannel'],\n"
        "        'status'        =>  $sEtiquetaStatus,\n"
        "        'callnumber'    =>  is_null($agent['callinfo']['callnumber']) ? '-' : $agent['callinfo']['callnumber'],\n"
        "        'trunk'         =>  is_null($agent['callinfo']['trunk']) ? '-' : $agent['callinfo']['trunk'],\n"
        "        'desde'         =>  $sDesde,\n"
        "    );\n"
        "}"
    )

    php_replace = (
        "function formatoAgente($agent)\n"
        "{\n"
        "    static $arrNombresAgentes = null;\n"
        "    if (is_null($arrNombresAgentes)) {\n"
        "        $arrNombresAgentes = array();\n"
        "        $oPaloConsola = new PaloSantoConsola();\n"
        "        $lista = $oPaloConsola->listarAgentes();\n"
        "        if (is_array($lista)) {\n"
        "            foreach ($lista as $chan => $formatted) {\n"
        "                $arrNombresAgentes[$chan] = $formatted;\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "\n"
        "    $sEtiquetaStatus = _tr($agent['status']);\n"
        "    $sFechaHoy = date('Y-m-d');\n"
        "    $sDesde = '-';\n"
        "    switch ($agent['status']) {\n"
        "    case 'paused':\n"
        "        // Prioridad de pausa: hold, break, agendada\n"
        "        if ($agent['onhold']) {\n"
        "            $sEtiquetaStatus = _tr('Hold');\n"
        "            // TODO: desde cuándo está en hold?\n"
        "        } elseif (!is_null($agent['pauseinfo'])) {\n"
        "            $sDesde = $agent['pauseinfo']['pausestart'];\n"
        "            $sEtiquetaStatus .= ': '.$agent['pauseinfo']['pausename'];\n"
        "        }\n"
        "        // TODO: exponer pausa de agendamiento\n"
        "        break;\n"
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        break;\n"
        "    }\n"
        "    if (strpos($sDesde, $sFechaHoy) === 0)\n"
        "        $sDesde = substr($sDesde, strlen($sFechaHoy) + 1);\n"
        "    return array(\n"
        "        'agent'         =>  $agent['agentchannel'],\n"
        "        'name'          =>  isset($arrNombresAgentes[$agent['agentchannel']]) ? $arrNombresAgentes[$agent['agentchannel']] : $agent['agentchannel'],\n"
        "        'status'        =>  $sEtiquetaStatus,\n"
        "        'callnumber'    =>  is_null($agent['callinfo']['callnumber']) ? '-' : $agent['callinfo']['callnumber'],\n"
        "        'trunk'         =>  is_null($agent['callinfo']['trunk']) ? '-' : $agent['callinfo']['trunk'],\n"
        "        'desde'         =>  $sDesde,\n"
        "    );\n"
        "}"
    )

    if php_target not in php_content_norm:
        print("Error: formatoAgente target not found in index.php")
        return 1

    php_content_norm = php_content_norm.replace(php_target, php_replace)

    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)
    print("Success: Updated index.php")

    # 2. Modify JS file
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    js_add_target = (
        "\t\t\tfor (var i = 0; i < respuesta.agents.add.length; i++) {\n"
        "\t\t\t\t  var agente = respuesta.agents.add[i];\n"
        "\t\t\t\t  const agentUpdate = agentUpdateColor(agente.status, agente.agent);\n"
        "\t\t\t\t  this.agentes.addObject(Ember.Object.create({\n"
        "\t\t\t\t    canal:     agente.agent,\n"
        "\t\t\t\t    numero:    agente.callnumber,\n"
        "\t\t\t\t    troncal:   agente.trunk,\n"
        "\t\t\t\t    estado:    agente.status,\n"
        "\t\t\t\t    image: \t   Ember.String.htmlSafe(agentUpdate.statusImage),\n"
        "\t\t\t\t    desde:     agente.desde,\n"
        "\t\t\t\t    rtime:     new Date(),\n"
        "\t\t\t\t    reciente:  true\n"
        "\t\t\t\t  }));\n"
        "\t\t\t\t  agentColor(agente.status, agente.agent);\n"
        "\t\t\t\t}"
    )

    js_add_replace = (
        "\t\t\tfor (var i = 0; i < respuesta.agents.add.length; i++) {\n"
        "\t\t\t\t  var agente = respuesta.agents.add[i];\n"
        "\t\t\t\t  const agentUpdate = agentUpdateColor(agente.status, agente.agent);\n"
        "\t\t\t\t  this.agentes.addObject(Ember.Object.create({\n"
        "\t\t\t\t    canal:     agente.agent,\n"
        "\t\t\t\t    nombre:    agente.name || agente.agent,\n"
        "\t\t\t\t    numero:    agente.callnumber,\n"
        "\t\t\t\t    troncal:   agente.trunk,\n"
        "\t\t\t\t    estado:    agente.status,\n"
        "\t\t\t\t    image: \t   Ember.String.htmlSafe(agentUpdate.statusImage),\n"
        "\t\t\t\t    desde:     agente.desde,\n"
        "\t\t\t\t    rtime:     new Date(),\n"
        "\t\t\t\t    reciente:  true\n"
        "\t\t\t\t  }));\n"
        "\t\t\t\t  agentColor(agente.status, agente.agent);\n"
        "\t\t\t\t}"
    )

    # Let's normalize tabs / spaces just in case
    # Actually let's search for a slightly looser target or exact target if matching
    if js_add_target not in js_content_norm:
        # Fallback to search without tabs
        js_add_target_fallback = js_add_target.replace('\t', '')
        js_content_norm_fallback = js_content_norm.replace('\t', '')
        if js_add_target_fallback not in js_content_norm_fallback:
            print("Error: Agents add loop target not found in javascript.js")
            return 1
        else:
            # Let's do a direct replacement in the original file
            # By finding the line: "canal:     agente.agent,"
            # and inserting "nombre:    agente.name || agente.agent," right after
            target_line = "canal:     agente.agent,"
            replace_line = "canal:     agente.agent,\n\t\t\t\t    nombre:    agente.name || agente.agent,"
            js_content_norm = js_content_norm.replace(target_line, replace_line)
    else:
        js_content_norm = js_content_norm.replace(js_add_target, js_add_replace)

    js_update_target = (
        "\t\t\t        if (agenteLista != null) {\n"
        "\t\t\t            agenteLista.setProperties({\n"
        "\t\t\t                'numero':   agente.callnumber,\n"
        "\t\t\t                'troncal':  agente.trunk,\n"
        "\t\t\t                'estado':   agente.status,\n"
        "\t\t\t                'image':    Ember.String.htmlSafe(agentUpdate.statusImage),\n"
        "\t\t\t                'desde':    agente.desde,\n"
        "\t\t\t                'rtime':    new Date(),\n"
        "\t\t\t                'reciente': true\n"
        "\t\t\t            });"
    )
    js_update_replace = (
        "\t\t\t        if (agenteLista != null) {\n"
        "\t\t\t            agenteLista.setProperties({\n"
        "\t\t\t                'nombre':   agente.name || agente.agent,\n"
        "\t\t\t                'numero':   agente.callnumber,\n"
        "\t\t\t                'troncal':  agente.trunk,\n"
        "\t\t\t                'estado':   agente.status,\n"
        "\t\t\t                'image':    Ember.String.htmlSafe(agentUpdate.statusImage),\n"
        "\t\t\t                'desde':    agente.desde,\n"
        "\t\t\t                'rtime':    new Date(),\n"
        "\t\t\t                'reciente': true\n"
        "\t\t\t            });"
    )

    if js_update_target not in js_content_norm:
        # Fallback replacement
        target_prop = "'numero':   agente.callnumber,"
        replace_prop = "'nombre':   agente.name || agente.agent,\n\t\t\t                'numero':   agente.callnumber,"
        js_content_norm = js_content_norm.replace(target_prop, replace_prop)
    else:
        js_content_norm = js_content_norm.replace(js_update_target, js_update_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Updated javascript.js")

    # 3. Modify template file
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1

    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_target = (
        "                {{#each agentes}}\n"
        "                <tr  {{bindAttr class=\"canal\"}}>\n"
        "                    <td width=\"20%\" nowrap=\"nowrap\">{{canal}}</td>"
    )
    tpl_replace = (
        "                {{#each agentes}}\n"
        "                <tr  {{bindAttr class=\"canal\"}}>\n"
        "                    <td width=\"20%\" nowrap=\"nowrap\">{{nombre}}</td>"
    )

    if tpl_target not in tpl_content_norm:
        print("Error: Template channel display cell target not found in informacion_campania.tpl")
        return 1

    tpl_content_norm = tpl_content_norm.replace(tpl_target, tpl_replace)

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: Updated informacion_campania.tpl")

    print("All agent name displays in monitoring updated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
