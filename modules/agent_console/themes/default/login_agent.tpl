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

{* WebPhone includes *}
<link rel="stylesheet" href="modules/agent_console/themes/default/js/webphone/webphone.css" />
<script type="text/javascript" src="modules/agent_console/themes/default/js/webphone/sip-0.20.0.min.js"></script>
<script type="text/javascript" src="modules/agent_console/themes/default/js/webphone/sip-phone.js"></script>

{if $NO_EXTENSIONS}
<p><h4 align="center">{$LABEL_NOEXTENSIONS}</h4></p>
{elseif $NO_AGENTS}
<p><h4 align="center">{$LABEL_NOAGENTS}</h4></p>
{else}
{* Wrapper flex para login + webphone *}
<div style="display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: center; gap: 20px; padding: 20px 0;">

{* Columna izquierda: formulario de login *}
<div>
<form method="POST"  action="index.php?menu={$MODULE_NAME}" onsubmit="do_login(); return false;">

<p>&nbsp;</p>
<p>&nbsp;</p>
<table width="400" border="0" cellspacing="0" cellpadding="0" align="center">
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

{* Columna derecha: WebPhone *}
<div id="new-webphone-wrapper" style="width: 280px; flex-shrink: 0;">
    <div class="webphone-panel">
        <div class="webphone-header">WebPhone</div>
        <div id="webphone-status" class="webphone-status webphone-unregistered">
            <span class="status-indicator"></span>
            <span class="status-text">Conectando...</span>
        </div>
        <div class="webphone-number-row">
            <input type="text" id="webphone-number" placeholder="Numero a marcar" />
        </div>
        <div class="webphone-buttons">
            <button id="webphone-btn-call" class="webphone-btn webphone-btn-call">Llamar</button>
            <button id="webphone-btn-hangup" class="webphone-btn webphone-btn-hangup" style="display:none;">Colgar</button>
            <button id="webphone-btn-answer" class="webphone-btn webphone-btn-answer" style="display:none;">Contestar</button>
        </div>
    </div>
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
    wssPath: '/ws'
};

$(document).ready(function() {
    console.log('[WebPhone] Initializing for extension: ' + webPhoneConfig.extension);
    
    if (!webPhoneConfig.extension) {
        console.warn('[WebPhone] No extension configured');
        $('#webphone-status .status-text').text('Sin extension');
        return;
    }
    
    if (!webPhoneConfig.password) {
        console.warn('[WebPhone] No password configured');
        $('#webphone-status .status-text').text('Sin contraseña');
        // Still try to init - user will see the error
    }
    
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
        }
    });

    // Bind UI events
    $('#webphone-btn-call').on('click', function() {
        var number = $('#webphone-number').val().trim();
        if (number) {
            WebPhone.call(number);
        }
    });

    $('#webphone-btn-hangup').on('click', function() {
        WebPhone.hangup();
    });

    $('#webphone-btn-answer').on('click', function() {
        WebPhone.answer();
    });

    $('#webphone-number').on('keypress', function(e) {
        if (e.which === 13) {
            var number = $(this).val().trim();
            if (number) {
                WebPhone.call(number);
            }
        }
    });
});
</script>
{/literal}
