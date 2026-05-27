#!/usr/bin/env python3
import os

def patch_agent_console_tpl(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    # 1. Add button HTML
    target_btn = """                        <button id="webphone-btn-answer" class="webphone-btn webphone-btn-answer" style="display:none;">Contestar</button>
                        <button id="webphone-btn-reconnect" class="webphone-btn webphone-btn-reconnect" style="display:none;">Reconectar</button>
                    </div>"""
    
    replacement_btn = """                        <button id="webphone-btn-answer" class="webphone-btn webphone-btn-answer" style="display:none;">Contestar</button>
                        <button id="webphone-btn-reconnect" class="webphone-btn webphone-btn-reconnect" style="display:none;">Reconectar</button>
                        <button id="webphone-btn-gestion" class="webphone-btn webphone-btn-gestion" style="display:none;">Gestión</button>
                    </div>"""

    if 'webphone-btn-gestion' not in content_norm:
        if target_btn in content_norm:
            content_norm = content_norm.replace(target_btn, replacement_btn, 1)
            print(f"Added Gestion button HTML to {filepath}")
        else:
            print(f"Error: Could not find target HTML button block in {filepath}")
            return False
    else:
        print(f"Gestion button HTML already present in {filepath}")

    # 2. Add click handler
    target_click = """        $('#webphone-btn-reconnect').on('click', function() {
            WebPhone.reconnect();
        });"""
        
    replacement_click = """        $('#webphone-btn-reconnect').on('click', function() {
            WebPhone.reconnect();
        });

        $('#webphone-btn-gestion').on('click', function() {
            var $gestionQuickBtn = window.jQuery('.btn-quickbreak').filter(function() {
                var text = window.jQuery(this).text().toUpperCase();
                return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
            });
            if ($gestionQuickBtn.length === 0) {
                console.warn('[WebPhone] No se encontró descanso de GESTIÓN configurado');
                return;
            }
            var breakid = $gestionQuickBtn.data('breakid');
            if (typeof estadoCliente !== 'undefined' && estadoCliente.break_id != null) {
                if (estadoCliente.break_id == breakid) {
                    if (typeof do_unbreak === 'function') do_unbreak();
                } else {
                    if (typeof do_unbreak === 'function') do_unbreak();
                }
            } else {
                window.jQuery('#break_select').val(breakid);
                if (typeof do_break === 'function') do_break();
            }
        });"""

    if "webphone-btn-gestion" not in content_norm or "$('#webphone-btn-gestion').on('click'" not in content_norm:
        if target_click in content_norm:
            content_norm = content_norm.replace(target_click, replacement_click, 1)
            print(f"Added click handler to {filepath}")
        else:
            print(f"Error: Could not find target click handler block in {filepath}")
            return False
    else:
        print(f"Click handler already present in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def patch_webphone_css(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    css_rules = """
/* Gestión Break Button Styles */
.webphone-btn-gestion {
    background: #ff7675;
    color: white;
}
.webphone-btn-gestion:hover:not(:disabled) {
    background: #ee5253;
}
.webphone-btn-gestion.active {
    background: #d63031 !important;
    color: white !important;
    animation: break-pulse 1.5s infinite;
}
"""

    if 'webphone-btn-gestion' not in content_norm:
        content_norm += css_rules
        print(f"Appended Gestion button CSS styles to {filepath}")
    else:
        print(f"Gestion button CSS styles already present in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def patch_sip_phone_js(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    target_status = """        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
        } else if (state.lastCallError) {
            $status.removeClass('webphone-registered webphone-connected').addClass('webphone-unregistered');
            $statusText.text(state.lastCallError);
        } else if (state.registered) {
            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');
            $statusText.text('Registrado');
        } else {
            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');
            $statusText.text('No registrado');
        }"""
        
    replacement_status = """        var $gestionBtn = $('#webphone-btn-gestion');
        if (state.authFailed) {
            $status.removeClass('webphone-registered webphone-unregistered').addClass('webphone-auth-failed');
            $statusText.text('Error de autenticacion');
            $gestionBtn.hide();
        } else if (state.lastCallError) {
            $status.removeClass('webphone-registered webphone-connected').addClass('webphone-unregistered');
            $statusText.text(state.lastCallError);
            $gestionBtn.hide();
        } else if (state.registered) {
            $status.removeClass('webphone-unregistered webphone-auth-failed').addClass('webphone-registered');
            $statusText.text('Registrado');
            $gestionBtn.show();
            
            // Sync active state based on global estadoCliente if available
            if (typeof estadoCliente !== 'undefined' && estadoCliente.break_id != null) {
                var $gestionQuickBtn = window.jQuery('.btn-quickbreak').filter(function() {
                    var text = window.jQuery(this).text().toUpperCase();
                    return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
                });
                if ($gestionQuickBtn.length && $gestionQuickBtn.data('breakid') == estadoCliente.break_id) {
                    $gestionBtn.addClass('active').text('Fin Gestión');
                } else {
                    $gestionBtn.removeClass('active').text('Gestión');
                }
            } else {
                $gestionBtn.removeClass('active').text('Gestión');
            }
        } else {
            $status.removeClass('webphone-registered webphone-auth-failed').addClass('webphone-unregistered');
            $statusText.text('No registrado');
            $gestionBtn.hide();
        }"""

    if 'Sync active state based on global estadoCliente' not in content_norm:
        if target_status in content_norm:
            content_norm = content_norm.replace(target_status, replacement_status, 1)
            print(f"Added Gestion button sync logic to sip-phone.js")
        else:
            print(f"Error: Could not find target registration status block in {filepath}")
            return False
    else:
        print(f"Gestion button sync logic already present in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def patch_javascript_js(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    # 1. Patch initialize_client_state
    target_init = """	// Inicializar estado de botones rápidos de break
	if (estadoCliente.break_id != null) {
		$('.btn-quickbreak').each(function() {
			var $btn = $(this);
			if ($btn.data('breakid') == estadoCliente.break_id) {
				$btn.addClass('active-break').prop('disabled', true);
			} else {
				$btn.prop('disabled', true);
			}
		});
	}"""

    replacement_init = """	// Inicializar estado de botones rápidos de break
	if (estadoCliente.break_id != null) {
		$('.btn-quickbreak').each(function() {
			var $btn = $(this);
			if ($btn.data('breakid') == estadoCliente.break_id) {
				$btn.addClass('active-break').prop('disabled', true);
			} else {
				$btn.prop('disabled', true);
			}
		});
	}

	// WebPhone Gestión break button initialization
	var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
	var $gestionBtn = $('#webphone-btn-gestion', context);
	if ($gestionBtn.length) {
		var $gestionQuickBtn = $('.btn-quickbreak').filter(function() {
			var text = $(this).text().toUpperCase();
			return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
		});
		if ($gestionQuickBtn.length && $gestionQuickBtn.data('breakid') == estadoCliente.break_id) {
			$gestionBtn.addClass('active').text('Fin Gestión');
		} else {
			$gestionBtn.removeClass('active').text('Gestión');
		}
	}"""

    if 'WebPhone Gestión break button initialization' not in content_norm:
        if target_init in content_norm:
            content_norm = content_norm.replace(target_init, replacement_init, 1)
            print(f"Added Gestion button initialization to javascript.js")
        else:
            # Maybe spacing differs, try another variant with different indentation tabs/spaces
            target_init_spaces = target_init.replace('\t', '    ')
            replacement_init_spaces = replacement_init.replace('\t', '    ')
            if target_init_spaces in content_norm:
                content_norm = content_norm.replace(target_init_spaces, replacement_init_spaces, 1)
                print(f"Added Gestion button initialization (spaces variant) to javascript.js")
            else:
                print(f"Error: Could not find target initialize_client_state block in {filepath}")
                return False
    else:
        print(f"Gestion button initialization already present in {filepath}")

    # 2. Patch case 'breakenter'
    target_enter = """			$('.btn-quickbreak').each(function() {
				var $btn = $(this);
				if ($btn.data('breakid') == respuesta[i].break_id) {
					$btn.addClass('active-break').prop('disabled', true);
				} else {
					$btn.prop('disabled', true);
				}
			});
			break;"""

    replacement_enter = """			$('.btn-quickbreak').each(function() {
				var $btn = $(this);
				if ($btn.data('breakid') == respuesta[i].break_id) {
					$btn.addClass('active-break').prop('disabled', true);
				} else {
					$btn.prop('disabled', true);
				}
			});

			// Sync WebPhone Gestión break button
			var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
			var $gestionBtn = $('#webphone-btn-gestion', context);
			if ($gestionBtn.length) {
				var $gestionQuickBtn = $('.btn-quickbreak').filter(function() {
					var text = $(this).text().toUpperCase();
					return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
				});
				if ($gestionQuickBtn.length && $gestionQuickBtn.data('breakid') == respuesta[i].break_id) {
					$gestionBtn.addClass('active').text('Fin Gestión');
				}
			}
			break;"""

    if 'Sync WebPhone Gestión break button' not in content_norm:
        if target_enter in content_norm:
            content_norm = content_norm.replace(target_enter, replacement_enter, 1)
            print(f"Added breakenter sync handler to {filepath}")
        else:
            target_enter_spaces = target_enter.replace('\t', '    ')
            replacement_enter_spaces = replacement_enter.replace('\t', '    ')
            if target_enter_spaces in content_norm:
                content_norm = content_norm.replace(target_enter_spaces, replacement_enter_spaces, 1)
                print(f"Added breakenter sync handler (spaces variant) to {filepath}")
            else:
                print(f"Error: Could not find target breakenter block in {filepath}")
                return False
    else:
        print(f"Breakenter sync handler already present in {filepath}")

    # 3. Patch case 'breakexit'
    target_exit = """			estadoCliente.break_id = null;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-unbreak')
				.addClass('issabel-callcenter-boton-break')
				.children('span').text(respuesta[i].txt_btn_break);
			$('.btn-quickbreak').removeClass('active-break').prop('disabled', false);
			break;"""

    replacement_exit = """			estadoCliente.break_id = null;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-unbreak')
				.addClass('issabel-callcenter-boton-break')
				.children('span').text(respuesta[i].txt_btn_break);
			$('.btn-quickbreak').removeClass('active-break').prop('disabled', false);

			// Sync WebPhone Gestión break button
			var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
			$('#webphone-btn-gestion', context).removeClass('active').text('Gestión');
			break;"""

    if 'breakexit' in content_norm and 'webphone-btn-gestion' not in content_norm.split('breakexit')[1]:
        if target_exit in content_norm:
            content_norm = content_norm.replace(target_exit, replacement_exit, 1)
            print(f"Added breakexit sync handler to {filepath}")
        else:
            target_exit_spaces = target_exit.replace('\t', '    ')
            replacement_exit_spaces = replacement_exit.replace('\t', '    ')
            if target_exit_spaces in content_norm:
                content_norm = content_norm.replace(target_exit_spaces, replacement_exit_spaces, 1)
                print(f"Added breakexit sync handler (spaces variant) to {filepath}")
            else:
                print(f"Error: Could not find target breakexit block in {filepath}")
                return False
    else:
        print(f"Breakexit sync handler already present in {filepath}")

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_norm)
        
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_console_tpl = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'agent_console.tpl')
    webphone_css = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'webphone.css')
    sip_phone_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'sip-phone.js')
    javascript_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'javascript.js')
    
    success = True
    success &= patch_agent_console_tpl(agent_console_tpl)
    success &= patch_webphone_css(webphone_css)
    success &= patch_sip_phone_js(sip_phone_js)
    success &= patch_javascript_js(javascript_js)
    
    if success:
        print("All Gestión quick break modifications applied successfully.")
        return 0
    else:
        print("Failed to apply some modifications.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
