#!/usr/bin/env python3
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    javascript_js = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'javascript.js')
    webphone_css = os.path.join(base_dir, 'modules', 'agent_console', 'themes', 'default', 'js', 'webphone', 'webphone.css')
    
    # 1. Patch javascript.js
    if not os.path.exists(javascript_js):
        print(f"Error: File not found {javascript_js}")
        return
        
    with open(javascript_js, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'state-loading' in content:
        print("Fluency/Optimistic UI patch already present in javascript.js")
    else:
        # Replace do_break
        target_do_break = """function do_break()
{
	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'break',
		breakid:	$('#break_select').val()
	},
	function (respuesta) {
		verificar_error_session(respuesta);
        if (respuesta['action'] == 'error') {
        	mostrar_mensaje_error(respuesta['message']);
        }

        // El cambio de estado de la interfaz se delega a la revisión
        // periódica del estado del agente.
        // TODO: definir evento agentbreakenter y agentbreakexit
	}, 'json')
	.fail(function() {
		mostrar_mensaje_error('Failed to connect to server to run request!');
	});
}"""

        replacement_do_break = """function do_break()
{
	// Optimistic UI: Disable all break buttons and show loading state
	var breakid = $('#break_select').val();
	$('.btn-quickbreak').prop('disabled', true);
	$('#btn_togglebreak').button('disable').children('span').text('Pausando...');
	
	// Disable WebPhone gestion button if it is a GESTION break
	var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
	var $gestionBtn = $('#webphone-btn-gestion', context);
	
	var $gestionQuickBtn = $('.btn-quickbreak').filter(function() {
		var text = $(this).text().toUpperCase();
		return text.indexOf('GESTION') !== -1 || text.indexOf('GESTIÓN') !== -1;
	});
	if ($gestionQuickBtn.length && $gestionQuickBtn.data('breakid') == breakid) {
		if ($gestionBtn.length) {
			$gestionBtn.prop('disabled', true).text('Procesando...');
		}
		$gestionQuickBtn.addClass('active-break state-loading');
	}

	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'break',
		breakid:	breakid
	},
	function (respuesta) {
		verificar_error_session(respuesta);
        if (respuesta['action'] == 'error') {
        	mostrar_mensaje_error(respuesta['message']);
        	
        	// Restore buttons on error
        	$('.btn-quickbreak').removeClass('active-break state-loading').prop('disabled', false);
        	$('#btn_togglebreak').button('enable').children('span').text('Descanso');
        	if ($gestionBtn.length) {
        		$gestionBtn.prop('disabled', false).text('Gestión');
        	}
        }
	}, 'json')
	.fail(function() {
		mostrar_mensaje_error('Failed to connect to server to run request!');
		
    	// Restore buttons on fail
    	$('.btn-quickbreak').removeClass('active-break state-loading').prop('disabled', false);
    	$('#btn_togglebreak').button('enable').children('span').text('Descanso');
    	if ($gestionBtn.length) {
    		$gestionBtn.prop('disabled', false).text('Gestión');
    	}
	});
}"""

        if target_do_break not in content:
            print("Error: Could not find target do_break pattern in javascript.js")
            return
        content = content.replace(target_do_break, replacement_do_break, 1)

        # Replace do_unbreak
        target_do_unbreak = """function do_unbreak()
{
	// Botón está en estado de quitar break
    $.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'unbreak'
	},
	function (respuesta) {
		verificar_error_session(respuesta);
        if (respuesta['action'] == 'error') {
        	mostrar_mensaje_error(respuesta['message']);
        }

        // El cambio de estado de la interfaz se delega a la revisión
        // periódica del estado del agente.
        // TODO: definir evento agentbreakenter y agentbreakexit
	}, 'json')
	.fail(function() {
		mostrar_mensaje_error('Failed to connect to server to run request!');
	});
}"""

        replacement_do_unbreak = """function do_unbreak()
{
	// Optimistic UI: disable toggle break button
	$('#btn_togglebreak').button('disable').children('span').text('Quitando...');
	
	// Disable WebPhone gestion button if exists
	var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
	var $gestionBtn = $('#webphone-btn-gestion', context);
	if ($gestionBtn.length) {
		$gestionBtn.prop('disabled', true).text('Procesando...');
	}

	// Botón está en estado de quitar break
    $.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'unbreak'
	},
	function (respuesta) {
		verificar_error_session(respuesta);
        if (respuesta['action'] == 'error') {
        	mostrar_mensaje_error(respuesta['message']);
        	
        	// Restore buttons on error
        	$('#btn_togglebreak').button('enable').children('span').text('Fin Descanso');
        	if ($gestionBtn.length) {
        		$gestionBtn.prop('disabled', false).text('Fin Gestión');
        	}
        }
	}, 'json')
	.fail(function() {
		mostrar_mensaje_error('Failed to connect to server to run request!');
		
    	// Restore buttons on fail
    	$('#btn_togglebreak').button('enable').children('span').text('Fin Descanso');
    	if ($gestionBtn.length) {
    		$gestionBtn.prop('disabled', false).text('Fin Gestión');
    	}
	});
}"""

        if target_do_unbreak not in content:
            print("Error: Could not find target do_unbreak pattern in javascript.js")
            return
        content = content.replace(target_do_unbreak, replacement_do_unbreak, 1)

        # Replace breakenter case
        target_breakenter = """		case 'breakenter':
			// El agente ha entrado en break
			estadoCliente.break_id = respuesta[i].break_id;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-break')
				.addClass('issabel-callcenter-boton-unbreak')
				.children('span').text(respuesta[i].txt_btn_break);
			$('.btn-quickbreak').each(function() {
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

        replacement_breakenter = """		case 'breakenter':
			// El agente ha entrado en break
			estadoCliente.break_id = respuesta[i].break_id;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-break')
				.addClass('issabel-callcenter-boton-unbreak')
				.children('span').text(respuesta[i].txt_btn_break);
			$('#btn_togglebreak').button('enable'); // Ensure it is enabled!
			$('.btn-quickbreak').removeClass('state-loading').each(function() {
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
					$gestionBtn.addClass('active').text('Fin Gestión').prop('disabled', false);
				} else {
					$gestionBtn.removeClass('active').text('Gestión').prop('disabled', false);
				}
			}
			break;"""

        if target_breakenter not in content:
            print("Error: Could not find target breakenter case pattern in javascript.js")
            return
        content = content.replace(target_breakenter, replacement_breakenter, 1)

        # Replace breakexit case
        target_breakexit = """		case 'breakexit':
			// El agente ha salido del break
			estadoCliente.break_id = null;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-unbreak')
				.addClass('issabel-callcenter-boton-break')
				.children('span').text(respuesta[i].txt_btn_break);
			$('.btn-quickbreak').removeClass('active-break').prop('disabled', false);

			// Sync WebPhone Gestión break button
			var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
			$('#webphone-btn-gestion', context).removeClass('active').text('Gestión');
			break;"""

        replacement_breakexit = """		case 'breakexit':
			// El agente ha salido del break
			estadoCliente.break_id = null;
			$('#btn_togglebreak')
				.removeClass('issabel-callcenter-boton-unbreak')
				.addClass('issabel-callcenter-boton-break')
				.children('span').text(respuesta[i].txt_btn_break);
			$('#btn_togglebreak').button('enable'); // Ensure it is enabled!
			$('.btn-quickbreak').removeClass('active-break state-loading').prop('disabled', false);

			// Sync WebPhone Gestión break button
			var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
			$('#webphone-btn-gestion', context).removeClass('active').text('Gestión').prop('disabled', false);
			break;"""

        if target_breakexit not in content:
            print("Error: Could not find target breakexit case pattern in javascript.js")
            return
        content = content.replace(target_breakexit, replacement_breakexit, 1)

        # Save javascript.js changes
        with open(javascript_js, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully patched javascript.js for optimistic break UI changes")

    # 2. Patch webphone.css
    if not os.path.exists(webphone_css):
        print(f"Error: File not found {webphone_css}")
        return

    with open(webphone_css, 'r', encoding='utf-8') as f:
        css_content = f.read()

    if 'state-loading' in css_content:
        print("Loading status styles already present in webphone.css")
    else:
        extra_css = """

/* Loading state for quick breaks */
.btn-quickbreak.state-loading {
    background: #ffc107 !important;
    color: #212529 !important;
    border-color: #d39e00 !important;
    cursor: wait !important;
    opacity: 0.85;
}
"""
        with open(webphone_css, 'a', encoding='utf-8') as f:
            f.write(extra_css)
        print("Successfully appended loading CSS styles to webphone.css")

if __name__ == '__main__':
    main()
