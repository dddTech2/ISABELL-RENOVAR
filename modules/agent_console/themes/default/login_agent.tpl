{* vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
  Codificación: UTF-8
  +----------------------------------------------------------------------+
  | Issabel version 0.8                                                  |
  | http://www.issabel.org                                               |
  +----------------------------------------------------------------------+
  | Copyright (c) 2006 Palosanto Solutions S. A.                         |
  +----------------------------------------------------------------------+
  | The contents of this file are subject to the General Public License  |
  | (GPL) Version 2 (the "License"); you may not use this file except in |
  | compliance with the License. You may obtain a copy of the License at |
  | http://www.opensource.org/licenses/gpl-license.php                   |
  |                                                                      |
  | Software distributed under the License is distributed on an "AS IS"  |
  | basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See  |
  | the License for the specific language governing rights and           |
  | limitations under the License.                                       |
  +----------------------------------------------------------------------+
  | The Initial Developer of the Original Code is PaloSanto Solutions    |
  +----------------------------------------------------------------------+
  $Id: default.conf.php,v 1.1.1.1 2007/03/23 00:13:58 elandivar Exp $
*}
{* Incluir todas las bibliotecas y CSS necesarios *}
{foreach from=$LISTA_JQUERY_CSS item=CURR_ITEM}
    {if $CURR_ITEM[0] == 'css'}
<link rel="stylesheet" href='{$CURR_ITEM[1]}' />
    {/if}
    {if $CURR_ITEM[0] == 'js'}
<script type="text/javascript" src='{$CURR_ITEM[1]}'></script>
    {/if}
{/foreach}

{if $NO_EXTENSIONS}
<p><h4 align="center">{$LABEL_NOEXTENSIONS}</h4></p>
{elseif $NO_AGENTS}
<p><h4 align="center">{$LABEL_NOAGENTS}</h4></p>
{else}
{* Wrapper flex para webphone + login *}
<div style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 30px; margin-top: 40px; margin-bottom: 40px;">

{* Columna izquierda: WebPhone *}
<div id="new-webphone-wrapper" style="width: 280px; flex-shrink: 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 4px;">
    <div class="webphone-panel" style="margin: 0; border: none;">
        <div class="webphone-header">
            <span>WebPhone</span>
            <button type="button" id="webphone-btn-pip" class="webphone-pip-icon-btn" title="Flotar WebPhone (Picture-in-Picture)" style="display: none;">⧉</button>
        </div>
        <div id="webphone-status" class="webphone-status webphone-unregistered">
            <span class="status-indicator"></span>
            <span class="status-text">Conectando...</span>
        </div>
        <div id="webphone-call-info" class="webphone-call-info" style="display: none;">
            <div class="caller-id"></div>
            <div class="call-timer" style="font-size: 1.1em; font-weight: bold; margin-top: 5px; display: none;">00:00</div>
        </div>
<!-- Contenedor para llamada retenida -->
        <div id="webphone-held-info" class="webphone-held-info" style="display: none;">
            <span class="held-text">Retenida: <span id="webphone-held-number"></span></span>
            <div class="held-actions">
                <button type="button" id="webphone-btn-resume-held" class="webphone-held-btn" title="Recuperar llamada">⎋ Recuperar</button>
                <button type="button" id="webphone-btn-hangup-held" class="webphone-held-btn hangup" title="Colgar retenida">❌</button>
            </div>
        </div>
        <div class="webphone-autoanswer-row">
            <label class="webphone-toggle">
                <input type="checkbox" id="webphone-autoanswer" />
                <span class="webphone-toggle-slider"></span>
            </label>
            <span class="webphone-autoanswer-label">Auto-Respuesta</span>
        </div>
        <div class="webphone-number-row">
            <input type="text" id="webphone-number" placeholder="Numero a marcar" style="border-radius: 3px 0 0 3px !important;" />
            <button type="button" id="webphone-btn-directory" class="webphone-btn-directory" title="Libreta de Extensiones">📖</button>
        </div>
        <!-- Panel de Libreta de Extensiones -->
        <div id="webphone-directory-panel" class="webphone-directory-panel" style="display: none;">
            <div class="directory-header">
                <span>Directorio</span>
                <button type="button" id="webphone-directory-close" class="directory-close-btn">&times;</button>
            </div>
            <div class="directory-search-row">
                <input type="text" id="webphone-directory-search" placeholder="Filtrar por nombre o ext..." autocomplete="off" />
            </div>
            <div class="directory-list-container">
                <div class="directory-loading">Cargando...</div>
                <table class="directory-table" style="display: none; width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr>
                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Ext</th>
                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Nombre</th>
                            <th style="font-weight: bold; color: #666; font-size: 11px; padding: 6px 4px; border-bottom: 1px solid #eee;">Estado</th>
                        </tr>
                    </thead>
                    <tbody id="webphone-directory-list"></tbody>
                </table>
            </div>
        </div>
        <!-- Fila para transferencia ciega -->
        <div id="webphone-transfer-row" class="webphone-transfer-row" style="display: none;">
            <input type="text" id="webphone-transfer-number" placeholder="Número/Ext. a transferir" />
            <button type="button" id="webphone-btn-do-transfer" class="webphone-btn webphone-btn-call">Enviar</button>
            <button type="button" id="webphone-btn-cancel-transfer" class="webphone-btn webphone-btn-hangup">X</button>
        </div>
        <div id="webphone-dialpad" class="webphone-dialpad" style="display: none;">
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="1">1</button>
                <button type="button" class="dialpad-btn" data-tone="2">2</button>
                <button type="button" class="dialpad-btn" data-tone="3">3</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="4">4</button>
                <button type="button" class="dialpad-btn" data-tone="5">5</button>
                <button type="button" class="dialpad-btn" data-tone="6">6</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="7">7</button>
                <button type="button" class="dialpad-btn" data-tone="8">8</button>
                <button type="button" class="dialpad-btn" data-tone="9">9</button>
            </div>
            <div class="dialpad-row">
                <button type="button" class="dialpad-btn" data-tone="*">*</button>
                <button type="button" class="dialpad-btn" data-tone="0">0</button>
                <button type="button" class="dialpad-btn" data-tone="#">#</button>
            </div>
        </div>
        <div class="webphone-buttons">
            <button id="webphone-btn-call" class="webphone-btn webphone-btn-call">Llamar</button>
            <button id="webphone-btn-hangup" class="webphone-btn webphone-btn-hangup" style="display:none;">Colgar</button>
            <button id="webphone-btn-hold" class="webphone-btn webphone-btn-hold" style="display:none;">Hold</button>
            <button id="webphone-btn-transfer" class="webphone-btn webphone-btn-transfer" style="display:none;">Transferir</button>
            <button id="webphone-btn-mute" class="webphone-btn webphone-btn-mute" style="display:none;">Silenciar</button>
            <button id="webphone-btn-answer" class="webphone-btn webphone-btn-answer" style="display:none;">Contestar</button>
            <button id="webphone-btn-reconnect" class="webphone-btn webphone-btn-reconnect" style="display:none;">Reconectar</button>
            <button id="webphone-btn-gestion" class="webphone-btn webphone-btn-gestion" style="display:none;">Gestión</button>
        </div>
    </div>
</div>

{* Columna derecha: formulario de login *}
<div>
<form method="POST"  action="index.php?menu={$MODULE_NAME}" onsubmit="do_login(); return false;">
<table width="400" border="0" cellspacing="0" cellpadding="0" align="center" style="box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <tr>
    <td width="498"  class="menudescription">
      <table width="100%" border="0" cellspacing="0" cellpadding="4" align="center">
        <tr>
          <td class="menudescription2">
              <div align="left"><font color="#ffffff">&nbsp;&raquo;&nbsp;{$WELCOME_AGENT}</font></div>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td width="498" bgcolor="#ffffff">
      <table width="100%" border="0" cellspacing="0" cellpadding="8" class="tabForm">
        <tr>
          <td colspan="2">
            <div align="center">{$ENTER_USER_PASSWORD}<br/><br/></div>
          </td>
        </tr>
        <tr id="login_fila_estado" {$ESTILO_FILA_ESTADO_LOGIN}>
          <td colspan="2">
            <div align="center" id="login_icono_espera" height='1'><img id="reloj" src="modules/{$MODULE_NAME}/images/loading.gif" border="0" alt=""></div>
            <div align="center" style="font-weight: bold;" id="login_msg_espera">{$MSG_ESPERA}</div>
            <div align="center" id="login_msg_error" style="color: #ff0000;"></div>
          </td>
        </tr>
        {* Fila visible: Extension callback text *}
        <tr>
          <td width="40%">
              <div align="right">{$CALLBACK_EXTENSION}:</div>
          </td>
          <td width="60%">
              <div align="center" style="font-weight: bold; font-size: 14px;">
                  {$LISTA_EXTENSIONES_CALLBACK.$ID_EXTENSION_CALLBACK|default:$ID_EXTENSION_CALLBACK}
              </div>
              <input type="hidden" id="input_extension_callback" name="input_extension_callback" value="{$ID_EXTENSION_CALLBACK}">
          </td>
        </tr>
        {* Campos ocultos: agent, extension, password, callback flag *}
        <tr style="display:none;">
          <td colspan="2">
                <select id="input_agent_user" name="input_agent_user">
                    {html_options options=$LISTA_AGENTES selected=$ID_AGENT}
                </select>
                <select name="input_extension" id="input_extension">
                    {html_options options=$LISTA_EXTENSIONES selected=$ID_EXTENSION}
                </select>
                <input type="password" name="input_agent_password" id="input_agent_password" value="">
          </td>
        </tr>
        {* Hidden fields for callback mode auto-login *}
        <input type="hidden" name="input_password_callback" id="input_password_callback" value="{$CALLBACK_PASSWORD}">
        <input type="hidden" name="input_callback" id="input_callback" value="checked">
        <input type=hidden name=onlycallback id=onlycallback value="1">
        <tr>
          <td colspan="2" align="center">
            <input type="button" id="submit_agent_login" name="submit_agent_login" value="{$LABEL_SUBMIT}" class="button" />
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

</form>
</div>

</div>{* fin wrapper flex *}

{if $REANUDAR_VERIFICACION}
<script type="text/javascript">
do_checklogin();
</script>
{/if}
{/if}

{literal}
<script type="text/javascript">
// WebPhone Initialization
var webPhoneConfig = {
    extension: '{/literal}{$WEBPHONE_EXTENSION}{literal}',
    password: '{/literal}{$WEBPHONE_PASSWORD}{literal}',
    domain: window.location.hostname,
    wssServer: window.location.hostname,
    wssPort: '8089',
    wssPath: '/ws',
    moduleName: '{/literal}{$MODULE_NAME}{literal}'
};

$(document).ready(function() {
    console.log('[WebPhone] Config:', {
        extension: webPhoneConfig.extension,
        passwordLength: webPhoneConfig.password ? webPhoneConfig.password.length : 0,
        domain: webPhoneConfig.domain,
        wssServer: webPhoneConfig.wssServer
    });
    
    if (!webPhoneConfig.extension) {
        console.warn('[WebPhone] No extension configured');
        $('#webphone-status .status-text').text('Error: Sin extension');
        return;
    }
    
    if (!webPhoneConfig.password) {
        console.warn('[WebPhone] No password configured');
        $('#webphone-status .status-text').text('Error: Sin contraseña');
        return;
    }
    
    $('#webphone-status .status-text').text('Registrando...');
    
    WebPhone.init(webPhoneConfig, {
        onRegistered: function() {
            console.log('[WebPhone] Registered successfully');
        },
        onUnregistered: function() {
            console.log('[WebPhone] Unregistered');
        },
        onError: function(error) {
            console.error('[WebPhone] Error:', error);
        },
        onCallStateChange: function(state) {
            console.log('[WebPhone] Call state:', state);
        },
        onCallRejectedBusy: function(caller) {
            console.log('[WebPhone] Call rejected (busy) from:', caller);
            $('#login_icono_espera').hide();
            $('#login_msg_espera').text("");
            $('#login_msg_error').text("Llamada directa perdida (Línea Ocupada): " + caller);
            $('#login_fila_estado').show();
            setTimeout(function() {
                $('#login_msg_error').text("");
                $('#login_fila_estado').hide();
            }, 7000);
        }
    });

    var $wp = function(selector) {
        var context = (window.pipWindow && !window.pipWindow.closed) ? window.pipWindow.document : document;
        return $(selector, context);
    };

    // Bind UI events
    $('#webphone-btn-call').on('click', function() {
        var number = $wp('#webphone-number').val().trim();
        if (number) {
            WebPhone.call(number);
        }
    });

    $('#webphone-btn-hangup').on('click', function() {
        WebPhone.hangup();
    });

    $('#webphone-btn-mute').on('click', function() {
        WebPhone.toggleMute();
    });

    $('#webphone-btn-answer').on('click', function() {
        WebPhone.answer();
    });

    $('#webphone-btn-reconnect').on('click', function() {
        WebPhone.reconnect();
    });

    // Eventos para Hold y Transferencia
    $('#webphone-btn-hold').on('click', function() {
        WebPhone.toggleHold();
    });

    $('#webphone-btn-transfer').on('click', function() {
        var phoneState = WebPhone.getState();
        if (phoneState.heldSession && phoneState.callState === 'connected') {
            // Transferencia atendida (conectar la retenida con la activa)
            WebPhone.transfer();
        } else {
            // Alternar fila de transferencia ciega
            var $row = $wp('#webphone-transfer-row');
            if ($row.is(':visible')) {
                $row.hide();
            } else {
                $row.css('display', 'flex');
                $wp('#webphone-transfer-number').val('').focus();
            }
        }
    });

    $('#webphone-btn-do-transfer').on('click', function() {
        var target = $wp('#webphone-transfer-number').val().trim();
        if (target) {
            WebPhone.transfer(target);
            $wp('#webphone-transfer-row').hide();
        }
    });

    $('#webphone-btn-cancel-transfer').on('click', function() {
        $wp('#webphone-transfer-row').hide();
    });

    $('#webphone-btn-resume-held').on('click', function() {
        WebPhone.resume();
    });

    $('#webphone-btn-hangup-held').on('click', function() {
        WebPhone.hangupHeld();
    });

    // Auto-answer toggle
    $('#webphone-autoanswer').on('change', function() {
        WebPhone.setAutoAnswer($(this).is(':checked'));
    });
    
    // Load saved auto-answer preference
    WebPhone.loadAutoAnswerPreference();

    // Bind DTMF Dialpad buttons click
    $('.dialpad-btn').on('click', function() {
        var tone = $(this).data('tone');
        if (tone !== undefined) {
            WebPhone.sendDTMF(String(tone));
        }
    });

    // Intercept physical keyboard keydowns for DTMF
    $(document).on('keydown', function(e) {
        var phoneState = WebPhone.getState();
        if (phoneState.callState !== 'connected') {
            return;
        }

        // Check if focused on input/textarea other than #webphone-number
        var activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'SELECT' || activeEl.isContentEditable)) {
            if (activeEl.id !== 'webphone-number') {
                return;
            }
        }

        var tone = e.key;
        if (tone === '*' || tone === '#' || (tone >= '0' && tone <= '9')) {
            WebPhone.sendDTMF(tone);

            var $btn = $('.dialpad-btn[data-tone="' + tone + '"]');
            if ($btn.length) {
                $btn.addClass('active');
                setTimeout(function() {
                    $btn.removeClass('active');
                }, 150);
            }
            e.preventDefault();
        }
    });

    $('#webphone-number').on('keypress', function(e) {
        if (e.which === 13) {
            var number = $(this).val().trim();
            if (number) {
                WebPhone.call(number);
            }
        }
    });

    // Global paste handler to route pasted number to WebPhone input field
    $(document).on('paste', function(e) {
        var $numInput = $('#webphone-number');
        if ($numInput.length === 0 || $numInput.prop('disabled')) {
            return;
        }

        // Allow standard paste if focused on another input/textarea
        var activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'SELECT' || activeEl.isContentEditable)) {
            if (activeEl.id !== 'webphone-number') {
                return;
            }
        }

        var clipboardData = e.originalEvent ? e.originalEvent.clipboardData : e.clipboardData;
        if (clipboardData) {
            var pastedText = clipboardData.getData('text');
            if (pastedText) {
                $numInput.val(pastedText.trim());
                $numInput.focus();
                e.preventDefault();
            }
        }
    });

    // Global Escape key handler to hangup/cancel calls
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' || e.key === 'Esc' || e.keyCode === 27) {
            var phoneState = WebPhone.getState();
            if (phoneState && phoneState.callState !== 'idle') {
                WebPhone.hangup();
                e.preventDefault();
            }
        }
    });

    // Check if Document Picture-in-Picture is supported
    if ('documentPictureInPicture' in window) {
        $('#webphone-btn-pip').show();
    }

    $('#webphone-btn-pip').on('click', async function() {
        if (!('documentPictureInPicture' in window)) {
            return;
        }

        if (window.pipWindow) {
            window.pipWindow.focus();
            return;
        }

        try {
            const pipWindow = await window.documentPictureInPicture.requestWindow({
                width: 280,
                height: 380
            });
            window.pipWindow = pipWindow;

            const $webphone = $('.webphone-panel');
            const $originalParent = $webphone.parent();

            pipWindow.document.body.append($webphone[0]);

            // Monkey patch WebRTC and audio APIs to execute in the context of the active PiP window
            // This prevents background tab throttling/delays when the parent window is inactive
            if (pipWindow.navigator && pipWindow.navigator.mediaDevices) {
                window.__originalGetUserMedia = navigator.mediaDevices.getUserMedia;
                navigator.mediaDevices.getUserMedia = function(constraints) {
                    if (window.pipWindow && !window.pipWindow.closed && window.pipWindow.navigator && window.pipWindow.navigator.mediaDevices) {
                        console.log('[WebPhone] Redirecting getUserMedia to PiP window context');
                        return window.pipWindow.navigator.mediaDevices.getUserMedia(constraints);
                    }
                    return window.__originalGetUserMedia.call(navigator.mediaDevices, constraints);
                };
            }

            if (pipWindow.RTCPeerConnection) {
                window.__originalRTCPeerConnection = window.RTCPeerConnection;
                window.RTCPeerConnection = function(config) {
                    if (window.pipWindow && !window.pipWindow.closed && window.pipWindow.RTCPeerConnection) {
                        console.log('[WebPhone] Redirecting RTCPeerConnection to PiP window context');
                        return new window.pipWindow.RTCPeerConnection(config);
                    }
                    return new window.__originalRTCPeerConnection(config);
                };
                window.RTCPeerConnection.prototype = window.__originalRTCPeerConnection.prototype;
            }

            const AudioCtxClass = pipWindow.AudioContext || pipWindow.webkitAudioContext;
            if (AudioCtxClass) {
                window.__originalAudioContext = window.AudioContext;
                window.__originalWebkitAudioContext = window.webkitAudioContext;
                window.AudioContext = function() {
                    if (window.pipWindow && !window.pipWindow.closed) {
                        console.log('[WebPhone] Redirecting AudioContext to PiP window context');
                        return new AudioCtxClass();
                    }
                    return new window.__originalAudioContext();
                };
                if (window.webkitAudioContext) {
                    window.webkitAudioContext = window.AudioContext;
                }
            }

            // Move audio elements to PiP window body to prevent background throttling
            if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
                const audios = WebPhone.getAudioElements();
                if (audios.remote) pipWindow.document.body.append(audios.remote);
                if (audios.local) pipWindow.document.body.append(audios.local);
            }
            pipWindow.document.body.style.margin = '0';
            pipWindow.document.body.style.padding = '0';
            pipWindow.document.body.style.overflow = 'hidden';
            pipWindow.document.body.style.backgroundColor = '#f5f5f5';

            // Copy styles
            [...document.styleSheets].forEach((styleSheet) => {
                try {
                    const cssRules = [...styleSheet.cssRules].map((rule) => rule.cssText).join('');
                    const style = document.createElement('style');
                    style.textContent = cssRules;
                    pipWindow.document.head.appendChild(style);
                } catch (e) {
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.type = styleSheet.type || 'text/css';
                    link.media = styleSheet.media.mediaText;
                    link.href = styleSheet.href;
                    pipWindow.document.head.appendChild(link);
                }
            });

            // Hide PiP button inside PiP window
            $(pipWindow.document.body).find('#webphone-btn-pip').hide();

            // Bind shortcuts inside the PiP document
            $(pipWindow.document).on('keydown', function(e) {
                if (e.key === 'Escape' || e.key === 'Esc' || e.keyCode === 27) {
                    var phoneState = WebPhone.getState();
                    if (phoneState && phoneState.callState !== 'idle') {
                        WebPhone.hangup();
                        e.preventDefault();
                    }
                }
            });

            $(pipWindow.document).on('paste', function(e) {
                var $numInput = $(pipWindow.document).find('#webphone-number');
                if ($numInput.length === 0 || $numInput.prop('disabled')) {
                    return;
                }

                var clipboardData = e.originalEvent ? e.originalEvent.clipboardData : e.clipboardData;
                if (clipboardData) {
                    var pastedText = clipboardData.getData('text');
                    if (pastedText) {
                        $numInput.val(pastedText.trim());
                        $numInput.focus();
                        e.preventDefault();
                    }
                }
            });

            pipWindow.addEventListener("pagehide", (event) => {
                window.pipWindow = null;
                $originalParent.append($webphone[0]);

                // Restore WebRTC and AudioContext APIs
                if (window.__originalGetUserMedia) {
                    navigator.mediaDevices.getUserMedia = window.__originalGetUserMedia;
                    delete window.__originalGetUserMedia;
                }
                if (window.__originalRTCPeerConnection) {
                    window.RTCPeerConnection = window.__originalRTCPeerConnection;
                    delete window.__originalRTCPeerConnection;
                }
                if (window.__originalAudioContext) {
                    window.AudioContext = window.__originalAudioContext;
                    delete window.__originalAudioContext;
                }
                if (window.__originalWebkitAudioContext) {
                    window.webkitAudioContext = window.__originalWebkitAudioContext;
                    delete window.__originalWebkitAudioContext;
                }

                // Restore audio elements to main body on PiP close
                if (typeof WebPhone !== 'undefined' && WebPhone.getAudioElements) {
                    const audios = WebPhone.getAudioElements();
                    if (audios.remote) document.body.append(audios.remote);
                    if (audios.local) document.body.append(audios.local);
                }
                $('#webphone-btn-pip').show();
            });

        } catch (err) {
            console.error('Failed to open PiP window:', err);
        }
    });
});
</script>
{/literal}
