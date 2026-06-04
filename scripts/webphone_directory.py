import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    
    agent_console_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "agent_console.tpl")
    login_agent_tpl = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "login_agent.tpl")
    css_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "webphone.css")
    js_file = os.path.join(workspace_dir, "modules", "agent_console", "themes", "default", "js", "webphone", "sip-phone.js")
    index_php = os.path.join(workspace_dir, "modules", "agent_console", "index.php")

    print("Applying Directory feature modifications...")

    # 1. Update index.php to add the getExtensionsList action
    if not os.path.exists(index_php):
        print(f"Error: index.php not found at {index_php}")
        return 1

    with open(index_php, 'r', encoding='utf-8') as f:
        php_content = f.read()

    php_content_norm = php_content.replace('\r\n', '\n')

    # Add the function right before the closing PHP tag
    function_code = """
function manejarSesionActiva_getExtensionsList($module_name, &$smarty, $sDirLocalPlantillas, $oPaloConsola, $estado, $listpanels = null)
{
    session_commit();
    
    $dsn = generarDSNSistema('asteriskuser', 'asterisk');
    $db = new paloDB($dsn);
    $query = "SELECT id, description, tech FROM devices ORDER BY id ASC";
    $dbExtensions = $db->fetchTable($query, TRUE);
    
    $onlineExtensions = array();
    
    $astman = new AGI_AsteriskManager();
    if ($astman->connect("127.0.0.1", "admin" , obtenerClaveAMIAdmin())) {
        // Parse SIP peers
        $rSip = $astman->Command('sip show peers');
        if (isset($rSip['data'])) {
            foreach (explode("\\n", $rSip['data']) as $line) {
                if (preg_match("/^\\s*(\\d+)\\/(\\d+)\\s+((\\d{1,3}(\\.\\d{1,3}){1,3})|\\(Unspecified\\))\\s+.*?(OK|Unmonitored)/i", $line, $matches)) {
                    $ext = $matches[1];
                    $onlineExtensions[$ext] = true;
                }
            }
        }
        
        // Parse PJSIP endpoints
        $rPjsip = $astman->Command('pjsip show endpoints');
        if (isset($rPjsip['data'])) {
            foreach (explode("\\n", $rPjsip['data']) as $line) {
                if (preg_match("/^Endpoint:\\s*(\\d+)\\b.*?Not\\s+in\\s+use|In\\s+use|Ringing|Busy/i", $line, $matches)) {
                    $ext = $matches[1];
                    $onlineExtensions[$ext] = true;
                }
                if (preg_match("/^\\s*Endpoint:\\s*(\\d+)\\/(\\d+)\\s+(\\D+)/", $line, $matches)) {
                    $ext = $matches[1];
                    if (strpos(strtolower($matches[3]), 'unavailable') === false) {
                        $onlineExtensions[$ext] = true;
                    }
                }
            }
        }
        $astman->disconnect();
    }
    
    $list = array();
    if (is_array($dbExtensions)) {
        foreach ($dbExtensions as $row) {
            $ext = $row['id'];
            $list[] = array(
                'extension' => $ext,
                'name' => $row['description'],
                'tech' => $row['tech'],
                'status' => isset($onlineExtensions[$ext]) ? 'online' : 'offline'
            );
        }
    }
    
    header('Content-Type: application/json');
    echo json_encode($list);
    exit();
}
"""

    if "function manejarSesionActiva_getExtensionsList" not in php_content_norm:
        target = "?>"
        if target in php_content_norm:
            # Insert before the last closing tag
            php_content_norm = php_content_norm.replace(target, function_code + "\n?>")
            print("Successfully added getExtensionsList backend function to index.php")
        else:
            php_content_norm += "\n" + function_code
            print("Appended getExtensionsList backend function to index.php (no closing tag)")
    else:
        print("Backend function getExtensionsList already exists in index.php")

    if '\r\n' in php_content:
        php_content_norm = php_content_norm.replace('\n', '\r\n')

    with open(index_php, 'w', encoding='utf-8') as f:
        f.write(php_content_norm)

    # 2. Update agent_console.tpl
    if not os.path.exists(agent_console_tpl):
        print(f"Error: agent_console.tpl not found at {agent_console_tpl}")
        return 1

    with open(agent_console_tpl, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    # Add moduleName to config
    config_target = (
        "var webPhoneConfig = {\n"
        "    extension: '{/literal}{$WEBPHONE_EXTENSION}{literal}',\n"
        "    password: '{/literal}{$WEBPHONE_PASSWORD}{literal}',\n"
        "    domain: window.location.hostname,\n"
        "    wssServer: window.location.hostname,\n"
        "    wssPort: '8089',\n"
        "    wssPath: '/ws'\n"
        "};"
    )
    config_replace = (
        "var webPhoneConfig = {\n"
        "    extension: '{/literal}{$WEBPHONE_EXTENSION}{literal}',\n"
        "    password: '{/literal}{$WEBPHONE_PASSWORD}{literal}',\n"
        "    domain: window.location.hostname,\n"
        "    wssServer: window.location.hostname,\n"
        "    wssPort: '8089',\n"
        "    wssPath: '/ws',\n"
        "    moduleName: '{/literal}{$MODULE_NAME}{literal}'\n"
        "};"
    )

    if config_target in tpl_content_norm:
        tpl_content_norm = tpl_content_norm.replace(config_target, config_replace)
        print("Added moduleName to webPhoneConfig in agent_console.tpl")

    # Add directory button and panel HTML
    html_target = (
        '                    <div class="webphone-number-row">\n'
        '                        <input type="text" id="webphone-number" placeholder="Numero a marcar" />\n'
        '                    </div>'
    )
    html_replace = (
        '                    <div class="webphone-number-row">\n'
        '                        <input type="text" id="webphone-number" placeholder="Numero a marcar" style="border-radius: 3px 0 0 3px !important;" />\n'
        '                        <button type="button" id="webphone-btn-directory" class="webphone-btn-directory" title="Libreta de Extensiones">📖</button>\n'
        '                    </div>\n'
        '                    <!-- Panel de Libreta de Extensiones -->\n'
        '                    <div id="webphone-directory-panel" class="webphone-directory-panel" style="display: none;">\n'
        '                        <div class="directory-header">\n'
        '                            <span>Directorio</span>\n'
        '                            <button type="button" id="webphone-directory-close" class="directory-close-btn">&times;</button>\n'
        '                        </div>\n'
        '                        <div class="directory-search-row">\n'
        '                            <input type="text" id="webphone-directory-search" placeholder="Filtrar por nombre o ext..." autocomplete="off" />\n'
        '                        </div>\n'
        '                        <div class="directory-list-container">\n'
        '                            <div class="directory-loading">Cargando...</div>\n'
        '                            <table class="directory-table" style="display: none; width: 100%; border-collapse: collapse; text-align: left;">\n'
        '                                <thead>\n'
        '                                    <tr>\n'
        '                                        <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Ext</th>\n'
        '                                        <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Nombre</th>\n'
        '                                        <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Estado</th>\n'
        '                                    </tr>\n'
        '                                </thead>\n'
        '                                <tbody id="webphone-directory-list"></tbody>\n'
        '                            </table>\n'
        '                        </div>\n'
        '                    </div>'
    )

    if html_target in tpl_content_norm:
        tpl_content_norm = tpl_content_norm.replace(html_target, html_replace)
        print("Successfully injected directory HTML into agent_console.tpl")
    else:
        # Check if already modified
        if 'id="webphone-btn-directory"' in tpl_content_norm:
            print("Directory HTML already exists in agent_console.tpl")
        else:
            print("Error: Target HTML block not found in agent_console.tpl")
            return 1

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(agent_console_tpl, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)

    # 3. Update login_agent.tpl
    if not os.path.exists(login_agent_tpl):
        print(f"Error: login_agent.tpl not found at {login_agent_tpl}")
        return 1

    with open(login_agent_tpl, 'r', encoding='utf-8') as f:
        login_content = f.read()

    login_content_norm = login_content.replace('\r\n', '\n')

    # Add moduleName to config
    config_target_login = (
        "var webPhoneConfig = {\n"
        "    extension: '{/literal}{$WEBPHONE_EXTENSION}{literal}',\n"
        "    password: '{/literal}{$WEBPHONE_PASSWORD}{literal}',\n"
        "    domain: window.location.hostname,\n"
        "    wssServer: window.location.hostname,\n"
        "    wssPort: '8089',\n"
        "    wssPath: '/ws'\n"
        "};"
    )
    config_replace_login = (
        "var webPhoneConfig = {\n"
        "    extension: '{/literal}{$WEBPHONE_EXTENSION}{literal}',\n"
        "    password: '{/literal}{$WEBPHONE_PASSWORD}{literal}',\n"
        "    domain: window.location.hostname,\n"
        "    wssServer: window.location.hostname,\n"
        "    wssPort: '8089',\n"
        "    wssPath: '/ws',\n"
        "    moduleName: '{/literal}{$MODULE_NAME}{literal}'\n"
        "};"
    )

    if config_target_login in login_content_norm:
        login_content_norm = login_content_norm.replace(config_target_login, config_replace_login)
        print("Added moduleName to webPhoneConfig in login_agent.tpl")

    # Add directory button and panel HTML
    html_target_login = (
        '        <div class="webphone-number-row">\n'
        '            <input type="text" id="webphone-number" placeholder="Numero a marcar" />\n'
        '        </div>'
    )
    html_replace_login = (
        '        <div class="webphone-number-row">\n'
        '            <input type="text" id="webphone-number" placeholder="Numero a marcar" style="border-radius: 3px 0 0 3px !important;" />\n'
        '            <button type="button" id="webphone-btn-directory" class="webphone-btn-directory" title="Libreta de Extensiones">📖</button>\n'
        '        </div>\n'
        '        <!-- Panel de Libreta de Extensiones -->\n'
        '        <div id="webphone-directory-panel" class="webphone-directory-panel" style="display: none;">\n'
        '            <div class="directory-header">\n'
        '                <span>Directorio</span>\n'
        '                <button type="button" id="webphone-directory-close" class="directory-close-btn">&times;</button>\n'
        '            </div>\n'
        '            <div class="directory-search-row">\n'
        '                <input type="text" id="webphone-directory-search" placeholder="Filtrar por nombre o ext..." autocomplete="off" />\n'
        '            </div>\n'
        '            <div class="directory-list-container">\n'
        '                <div class="directory-loading">Cargando...</div>\n'
        '                <table class="directory-table" style="display: none; width: 100%; border-collapse: collapse; text-align: left;">\n'
        '                    <thead>\n'
        '                        <tr>\n'
        '                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Ext</th>\n'
        '                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Nombre</th>\n'
        '                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Estado</th>\n'
        '                        </tr>\n'
        '                    </thead>\n'
        '                    <tbody id="webphone-directory-list"></tbody>\n'
        '                </table>\n'
        '            </div>\n'
        '        </div>'
    )

    if html_target_login in login_content_norm:
        login_content_norm = login_content_norm.replace(html_target_login, html_replace_login)
        print("Successfully injected directory HTML into login_agent.tpl")
    else:
        # Check if already modified
        if 'id="webphone-btn-directory"' in login_content_norm:
            print("Directory HTML already exists in login_agent.tpl")
        else:
            print("Error: Target HTML block not found in login_agent.tpl")
            return 1

    if '\r\n' in login_content:
        login_content_norm = login_content_norm.replace('\n', '\r\n')

    with open(login_agent_tpl, 'w', encoding='utf-8') as f:
        f.write(login_content_norm)

    # 4. Update webphone.css
    if not os.path.exists(css_file):
        print(f"Error: webphone.css not found at {css_file}")
        return 1

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_styles = """
/* Directory Panel Styles */
.webphone-btn-directory {
    background: #eaeaea;
    border: 1px solid #ccc;
    border-left: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 0 3px 3px 0;
    font-size: 14px;
    transition: background 0.2s ease;
    outline: none;
}
.webphone-btn-directory:hover {
    background: #dddddd;
}
.webphone-directory-panel {
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #fff;
    padding: 10px;
    margin-bottom: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    font-size: 13px;
    text-align: left;
}
.directory-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
}
.directory-close-btn {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #999;
    padding: 0;
    line-height: 1;
}
.directory-close-btn:hover {
    color: #333;
}
.directory-search-row {
    margin-bottom: 8px;
}
.directory-search-row input {
    width: 100%;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-size: 12px;
    box-sizing: border-box;
}
.directory-list-container {
    max-height: 180px;
    overflow-y: auto;
}
.directory-table tbody tr {
    cursor: pointer;
    transition: background 0.1s ease;
}
.directory-table tbody tr:hover {
    background: #f5f5f5;
}
.directory-table tbody td {
    padding: 6px 4px;
    border-bottom: 1px solid #eee;
}
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
}
.status-dot.online {
    background-color: #5cb85c;
    box-shadow: 0 0 4px #5cb85c;
}
.status-dot.offline {
    background-color: #d9534f;
}
.directory-loading {
    padding: 15px 0;
    text-align: center;
    color: #666;
}
"""

    if ".webphone-directory-panel" not in css_content_norm:
        css_content_norm += "\n" + css_styles
        print("Appended directory styling to webphone.css")
    else:
        print("Directory styling already exists in webphone.css")

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)

    # 5. Update sip-phone.js
    if not os.path.exists(js_file):
        print(f"Error: sip-phone.js not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    js_logic = """
    // Global Event Handlers for Extension Directory
    $(document).ready(function() {
        var extensionsCache = [];

        $(document).on('click', '#webphone-btn-directory', function() {
            var $panel = $('#webphone-directory-panel');
            if ($panel.is(':visible')) {
                $panel.slideUp(200);
            } else {
                $panel.slideDown(200);
                $('#webphone-directory-search').val('').focus();
                loadDirectoryList();
            }
        });

        $(document).on('click', '#webphone-directory-close', function() {
            $('#webphone-directory-panel').slideUp(200);
        });

        $(document).on('keyup', '#webphone-directory-search', function() {
            var search = $(this).val().toLowerCase().trim();
            filterDirectory(search);
        });

        $(document).on('click', '.directory-item-row', function() {
            var ext = $(this).data('extension');
            if ($('#webphone-transfer-row').is(':visible')) {
                $('#webphone-transfer-number').val(ext).focus();
            } else {
                var $numInput = $('#webphone-number');
                if (!$numInput.prop('disabled')) {
                    $numInput.val(ext).focus();
                }
            }
            $('#webphone-directory-panel').slideUp(200);
        });

        function loadDirectoryList() {
            var $loading = $('.directory-loading');
            var $table = $('.directory-table');
            var $list = $('#webphone-directory-list');

            $loading.show().text('Cargando extensiones...');
            $table.hide();
            $list.empty();

            var menu = (config && config.moduleName) ? config.moduleName : 'agent_console';
            $.getJSON('index.php?menu=' + menu + '&action=getExtensionsList', function(data) {
                extensionsCache = data;
                renderDirectory(data);
                $loading.hide();
                $table.show();
            }).fail(function() {
                $loading.show().text('Error al cargar extensiones');
            });
        }

        function renderDirectory(items) {
            var $list = $('#webphone-directory-list');
            $list.empty();
            if (!items || items.length === 0) {
                $list.append('<tr><td colspan="3" style="text-align:center; color:#999;">Sin resultados</td></tr>');
                return;
            }
            items.forEach(function(item) {
                var dotClass = item.status === 'online' ? 'online' : 'offline';
                var statusText = item.status === 'online' ? 'Disponible' : 'No disponible';
                var row = $('<tr class="directory-item-row" data-extension="' + item.extension + '">' +
                    '<td style="font-weight:bold; padding: 6px 4px; border-bottom: 1px solid #eee;">' + item.extension + '</td>' +
                    '<td style="padding: 6px 4px; border-bottom: 1px solid #eee;">' + item.name + '</td>' +
                    '<td style="white-space:nowrap; padding: 6px 4px; border-bottom: 1px solid #eee;"><span class="status-dot ' + dotClass + '"></span>' + statusText + '</td>' +
                    '</tr>');
                $list.append(row);
            });
        }

        function filterDirectory(search) {
            if (!search) {
                renderDirectory(extensionsCache);
                return;
            }
            var filtered = extensionsCache.filter(function(item) {
                var extMatch = item.extension.indexOf(search) !== -1;
                var nameMatch = item.name && item.name.toLowerCase().indexOf(search) !== -1;
                return extMatch || nameMatch;
            });
            renderDirectory(filtered);
        }
    });
"""

    if "Global Event Handlers for Extension Directory" not in js_content_norm:
        target_js = "    // Public API\n    return {"
        if target_js in js_content_norm:
            js_content_norm = js_content_norm.replace(target_js, js_logic + "\n    // Public API\n    return {")
            print("Successfully injected directory JS logic to sip-phone.js")
        else:
            print("Error: Target JS position not found in sip-phone.js")
            return 1
    else:
        print("Directory JS logic already exists in sip-phone.js")

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)

    print("All directory features applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
