import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    tpl_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    css_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "javascript.js")

    print(f"Modifying template file: {tpl_file}")
    print(f"Modifying CSS file: {css_file}")
    print(f"Modifying JS file: {js_file}")

    # 1. Modify agent_console.tpl
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1
    
    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    # Normalize line endings
    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_target = '\t    </div> {* issabel-callcenter-controles *}'
    tpl_replace = (
        '\t    </div> {* issabel-callcenter-controles *}\n'
        '        <div id="issabel-callcenter-controles-break">\n'
        '            <span class="quickbreak-label">Descansos Rápidos:</span>\n'
        '            {foreach from=$LISTA_BREAKS key=break_id item=break_name}\n'
        '                <button type="button" class="btn-quickbreak" data-breakid="{$break_id}">{$break_name}</button>\n'
        '            {/foreach}\n'
        '        </div>'
    )

    if tpl_target not in tpl_content_norm:
        print("Error: Target controls end block not found in agent_console.tpl")
        return 1
    
    tpl_content_norm = tpl_content_norm.replace(tpl_target, tpl_replace)

    # Restore line endings and write back
    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')
    
    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: agent_console.tpl updated.")

    # 2. Modify webphone.css
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')
    
    quickbreak_css_rules = (
        "\n"
        "/* ============================================ \n"
        "   QUICK BREAKS ROW & BUTTONS\n"
        "   ============================================ */\n"
        "#issabel-callcenter-controles-break {\n"
        "    flex: 0 0 100%;\n"
        "    width: 100%;\n"
        "    margin-bottom: 10px;\n"
        "    padding: 5px 8px;\n"
        "    background: #fdfdfd;\n"
        "    border: 1px dashed #cccccc;\n"
        "    border-radius: 4px;\n"
        "    box-sizing: border-box;\n"
        "    display: flex;\n"
        "    align-items: center;\n"
        "    flex-wrap: wrap;\n"
        "    gap: 5px;\n"
        "}\n"
        "\n"
        ".quickbreak-label {\n"
        "    font-weight: bold;\n"
        "    margin-right: 8px;\n"
        "    color: #555;\n"
        "    font-size: 12px;\n"
        "}\n"
        "\n"
        ".btn-quickbreak {\n"
        "    background: #e9ecef;\n"
        "    color: #495057;\n"
        "    border: 1px solid #ced4da;\n"
        "    padding: 6px 12px;\n"
        "    border-radius: 4px;\n"
        "    font-size: 11px;\n"
        "    font-weight: bold;\n"
        "    cursor: pointer;\n"
        "    transition: all 0.2s ease-in-out;\n"
        "}\n"
        "\n"
        ".btn-quickbreak:hover:not(:disabled) {\n"
        "    background: #dee2e6;\n"
        "    color: #212529;\n"
        "    border-color: #adb5bd;\n"
        "}\n"
        "\n"
        ".btn-quickbreak:disabled {\n"
        "    opacity: 0.5;\n"
        "    cursor: not-allowed;\n"
        "    background: #e9ecef;\n"
        "    color: #adb5bd;\n"
        "    border-color: #dee2e6;\n"
        "}\n"
        "\n"
        ".btn-quickbreak.active-break {\n"
        "    background: #dc3545 !important;\n"
        "    color: white !important;\n"
        "    border-color: #dc3545 !important;\n"
        "    box-shadow: 0 0 8px rgba(220, 53, 69, 0.4);\n"
        "    animation: break-pulse 1.5s infinite;\n"
        "}\n"
        "\n"
        "@keyframes break-pulse {\n"
        "    0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); }\n"
        "    70% { box-shadow: 0 0 0 8px rgba(220, 53, 69, 0); }\n"
        "    100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }\n"
        "}\n"
    )

    # Append to CSS content
    css_content_norm += quickbreak_css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: webphone.css updated.")

    # 3. Modify javascript.js
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Add quick break click handler
    click_target = (
        "    // El siguiente código se ejecuta al hacer click en el botón de break\n"
        "    $('#btn_togglebreak').click(function() {\n"
        "    \tif ($('#btn_togglebreak').hasClass('issabel-callcenter-boton-unbreak')) {\n"
        "    \t\tdo_unbreak();\n"
        "    \t} else {\n"
        "    \t\t// Botón está en estado de elegir break\n"
        "    \t\t$('#issabel-callcenter-seleccion-break').dialog('open');\n"
        "    \t}\n"
        "    });"
    )
    click_replace = (
        "    // El siguiente código se ejecuta al hacer click en el botón de break\n"
        "    $('#btn_togglebreak').click(function() {\n"
        "    \tif ($('#btn_togglebreak').hasClass('issabel-callcenter-boton-unbreak')) {\n"
        "    \t\tdo_unbreak();\n"
        "    \t} else {\n"
        "    \t\t// Botón está en estado de elegir break\n"
        "    \t\t$('#issabel-callcenter-seleccion-break').dialog('open');\n"
        "    \t}\n"
        "    });\n"
        "\n"
        "    // El siguiente código se ejecuta al hacer click en los botones rápidos de break\n"
        "    $('.btn-quickbreak').click(function() {\n"
        "        var breakid = $(this).data('breakid');\n"
        "        $('#break_select').val(breakid);\n"
        "        do_break();\n"
        "    });"
    )

    if click_target not in js_content_norm:
        print("Error: Target click handler block not found in javascript.js")
        return 1

    js_content_norm = js_content_norm.replace(click_target, click_replace)

    # Add initial quick break button states in initialize_client_state()
    init_target = (
        "    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription, false);\n"
        "    \n"
        "    \n"
        "}"
    )
    init_replace = (
        "    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription, false);\n"
        "    \n"
        "    // Inicializar estado de botones rápidos de break\n"
        "    if (estadoCliente.break_id != null) {\n"
        "        $('.btn-quickbreak').each(function() {\n"
        "            var $btn = $(this);\n"
        "            if ($btn.data('breakid') == estadoCliente.break_id) {\n"
        "                $btn.addClass('active-break').prop('disabled', true);\n"
        "            } else {\n"
        "                $btn.prop('disabled', true);\n"
        "            }\n"
        "        });\n"
        "    }\n"
        "}"
    )

    if init_target not in js_content_norm:
        # Let's try matching with different line ending spacing
        init_target_alt = (
            "    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription, false);\n"
            "}"
        )
        init_replace_alt = (
            "    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription, false);\n"
            "    // Inicializar estado de botones rápidos de break\n"
            "    if (estadoCliente.break_id != null) {\n"
            "        $('.btn-quickbreak').each(function() {\n"
            "            var $btn = $(this);\n"
            "            if ($btn.data('breakid') == estadoCliente.break_id) {\n"
            "                $btn.addClass('active-break').prop('disabled', true);\n"
            "            } else {\n"
            "                $btn.prop('disabled', true);\n"
            "            }\n"
            "        });\n"
            "    }\n"
            "}"
        )
        if init_target_alt not in js_content_norm:
            print("Error: Target initialize_client_state end block not found in javascript.js")
            return 1
        js_content_norm = js_content_norm.replace(init_target_alt, init_replace_alt)
    else:
        js_content_norm = js_content_norm.replace(init_target, init_replace)

    # Add breakenter cases
    enter_target = (
        "\t\tcase 'breakenter':\n"
        "\t\t\t// El agente ha entrado en break\n"
        "\t\t\testadoCliente.break_id = respuesta[i].break_id;\n"
        "\t\t\t$('#btn_togglebreak')\n"
        "\t\t\t\t.removeClass('issabel-callcenter-boton-break')\n"
        "\t\t\t\t.addClass('issabel-callcenter-boton-unbreak')\n"
        "\t\t\t\t.children('span').text(respuesta[i].txt_btn_break);\n"
        "\t\t\tbreak;"
    )
    enter_replace = (
        "\t\tcase 'breakenter':\n"
        "\t\t\t// El agente ha entrado en break\n"
        "\t\t\testadoCliente.break_id = respuesta[i].break_id;\n"
        "\t\t\t$('#btn_togglebreak')\n"
        "\t\t\t\t.removeClass('issabel-callcenter-boton-break')\n"
        "\t\t\t\t.addClass('issabel-callcenter-boton-unbreak')\n"
        "\t\t\t\t.children('span').text(respuesta[i].txt_btn_break);\n"
        "\t\t\t$('.btn-quickbreak').each(function() {\n"
        "\t\t\t\tvar $btn = $(this);\n"
        "\t\t\t\tif ($btn.data('breakid') == respuesta[i].break_id) {\n"
        "\t\t\t\t\t$btn.addClass('active-break').prop('disabled', true);\n"
        "\t\t\t\t} else {\n"
        "\t\t\t\t\t$btn.prop('disabled', true);\n"
        "\t\t\t\t}\n"
        "\t\t\t});\n"
        "\t\t\tbreak;"
    )

    if enter_target not in js_content_norm:
        print("Error: Target breakenter case not found in javascript.js")
        return 1
    
    js_content_norm = js_content_norm.replace(enter_target, enter_replace)

    # Add breakexit cases
    exit_target = (
        "\t\tcase 'breakexit':\n"
        "\t\t\t// El agente ha salido del break\n"
        "\t\t\testadoCliente.break_id = null;\n"
        "\t\t\t$('#btn_togglebreak')\n"
        "\t\t\t\t.removeClass('issabel-callcenter-boton-unbreak')\n"
        "\t\t\t\t.addClass('issabel-callcenter-boton-break')\n"
        "\t\t\t\t.children('span').text(respuesta[i].txt_btn_break);\n"
        "\t\t\tbreak;"
    )
    exit_replace = (
        "\t\tcase 'breakexit':\n"
        "\t\t\t// El agente ha salido del break\n"
        "\t\t\testadoCliente.break_id = null;\n"
        "\t\t\t$('#btn_togglebreak')\n"
        "\t\t\t\t.removeClass('issabel-callcenter-boton-unbreak')\n"
        "\t\t\t\t.addClass('issabel-callcenter-boton-break')\n"
        "\t\t\t\t.children('span').text(respuesta[i].txt_btn_break);\n"
        "\t\t\t$('.btn-quickbreak').removeClass('active-break').prop('disabled', false);\n"
        "\t\t\tbreak;"
    )

    if exit_target not in js_content_norm:
        print("Error: Target breakexit case not found in javascript.js")
        return 1

    js_content_norm = js_content_norm.replace(exit_target, exit_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: javascript.js updated.")
    
    print("All files updated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
