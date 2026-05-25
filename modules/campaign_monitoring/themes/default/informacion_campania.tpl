{* Este DIV se usa para mostrar los mensajes de error *}
<div
    id="issabel-callcenter-error-message"
    class="ui-state-error ui-corner-all">
    <p>
        <span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>
        <span id="issabel-callcenter-error-message-text"></span>
    </p>
</div>
<div id="campaignMonitoringApplication">
<script type="text/x-handlebars" data-template-name="campaign">

<b>{$ETIQUETA_CAMPANIA}:</b> <br>
{literal}
{{view App.CampaignSelect
            contentBinding="content"
            optionValuePath="content.key_campaign"
            optionLabelPath="content.label_with_status"
            valueBinding="key_campaign" }}
{/literal}
<br><br>

{literal}{{outlet}}{/literal}

</script>

<script type="text/x-handlebars" data-template-name="campaign/details">
{* Atributos de la campaña elegida *}

<div class="flex-container">
    <table class="campaign-table" border="1">
        <tr>
            <th colspan="3" class="table-header">Campaign Configuration</th>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_COLA}:</b></td>
            <td colspan="2">{literal}{{cola}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_INTENTOS}:</b></td>
            <td colspan="2">{literal}{{maxIntentos}}{/literal}</td>
        </tr>
    </table>

    <table class="campaign-table" border="1">
        <tr>
            <th colspan="2" class="table-header">Dates and Times</th>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_FECHA_INICIO}:</b></td>
            <td>{literal}{{fechaInicio}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_FECHA_FINAL}:</b></td>
            <td>{literal}{{fechaFinal}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_HORARIO}:</b></td>
            <td colspan="4">{literal}{{horaInicio}} - {{horaFinal}}{/literal}</td>
        </tr>
    </table>
</div>

<div class="flex-container">
    <table class="campaign-table" border="1">
        <tr>
            <th colspan="3" class="table-header">Campaign Counters</th>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_TOTAL_LLAMADAS}:</b></td>
            <td colspan="2">{literal}{{llamadas.total}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_LLAMADAS_EXITO}:</b></td>
            <td colspan="3">{literal}{{llamadas.conectadas}}{/literal}</td>
        </tr>
    </table>

    <table class="campaign-table" border="1">
        <tr>
            <th colspan="3" class="table-header">Call Duration Statistics</th>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_PROMEDIO_DURAC_LLAM}:</b></td>
            <td>{literal}{{llamadas.fmtpromedio}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_MAX_DURAC_LLAM}:</b></td>
            <td>{literal}{{llamadas.fmtmaxduration}}{/literal}</td>
        </tr>
    </table>
</div>

<div class="flex-container">
    {literal}{{#if outgoing }}{/literal}
    <table class="campaign-table-outgoing" border="1">
        <tr>
            <th colspan="4" class="table-header">Outgoing Call Details</th>
        </tr>
        <tr>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_PENDIENTES}:</b></td>
            <td class="data-out">{literal}{{llamadas.pendientes}}{/literal}</td>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_FALLIDAS}:</b></td>
            <td class="data-out">{literal}{{llamadas.fallidas}}{/literal}
        </tr>
        <tr>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_MARCANDO}:</b></td>
            <td class="data-out">{literal}{{llamadas.marcando}}{/literal}</td>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_NOCONTESTA}:</b></td>
            <td class="data-out">{literal}{{llamadas.nocontesta}}{/literal}
        </tr>
        <tr>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_TIMBRANDO}:</b></td>
            <td class="data-out">{literal}{{llamadas.timbrando}}{/literal}</td>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_ABANDONADAS}:</b></td>
            <td class="data-out">{literal}{{llamadas.abandonadas}}{/literal}
        </tr>
        <tr>
            <td class="table-label-out"><b>{$ETIQUETA_LLAMADAS_CORTAS}:</b></td>
            <td class="data-out">{literal}{{llamadas.cortas}}{/literal}</td>
            <td class="empty-cell"></td>
            <td class="empty-cell"></td>
        </tr>
    </table>
    {literal}{{else}}{/literal}
    <table class="campaign-table" border="1">
        <tr>
            <th colspan="3" class="table-header">Incoming Call Details</th>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_LLAMADAS_SINRASTRO}:</b></td>
            <td>{literal}{{llamadas.sinrastro}}{/literal}</td>
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_LLAMADAS_ABANDONADAS}:</b></td>
            <td>{literal}{{llamadas.abandonadas}}{/literal}
        </tr>
        <tr>
            <td class="table-label"><b>{$ETIQUETA_LLAMADAS_TERMINADAS}:</b></td>
            <td>{literal}{{llamadas.terminadas}}{/literal}
        </tr>
    </table>
    {literal}{{/if}}{/literal}
</div>



{* Listado de llamadas y de agentes *}
<table width="100%" ><tr>
    <td width="35%" style="vertical-align: top;">
        <b>{$ETIQUETA_LLAMADAS_MARCANDO}:</b>
        <table class="titulo" style="table-layout: fixed; width: 100%;">
            <tr>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_ESTADO}</td>
                <td width="30%" nowrap="nowrap">{$ETIQUETA_NUMERO_TELEFONO}</td>
                <td width="30%" nowrap="nowrap">{$ETIQUETA_TRONCAL}</td>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_DESDE}</td>
            </tr>
        </table>
        <div class="llamadas" {literal}{{bindAttr style="alturaLlamada"}}{/literal}>
            <table style="table-layout: fixed; width: 100%;">
                {literal}{{#view tagName="tbody"}}
                {{#each llamadasMarcando}}
                <tr style="background-color:#00e7ffa6" {{bindAttr class="reciente"}}>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{estado}}</td>
                    <td width="30%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{numero}}</td>
                    <td width="30%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{troncal}}</td>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{desde}}</td>
                </tr>
                {{/each}}
                {{/view}}{/literal}
            </table>
        </div>
    </td>
    <td width="65%" style="vertical-align: top;">
        <b>{$ETIQUETA_AGENTES}:</b>
        <table class="titulo" style="table-layout: fixed; width: 100%;">
            <tr>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_AGENTE}</td>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_ESTADO}</td>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_NUMERO_TELEFONO}</td>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_TRONCAL}</td>
                <td width="20%" nowrap="nowrap">{$ETIQUETA_DESDE}</td>
            </tr>
        </table>
        <div class="llamadas agent-table-wrapper" {literal}{{bindAttr style="alturaLlamada"}}{/literal}>
            <table style="table-layout: fixed; width: 100%;">
                {literal}{{#view tagName="tbody"}}
                {{#each agentes}}
                <tr  {{bindAttr class="canal"}} {{bindAttr data-agent="canal" data-status="estado"}}>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{{nombre}}">{{nombre}}</td>
                    <td width="20%" nowrap="nowrap"><div class="trAgent">{{image}}{{estado}}</div></td>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{numero}}</td>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{troncal}}</td>
                    <td width="20%" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{desde}}</td>
                </tr>
                {{/each}}
                {{/view}}{/literal}
            </table>
        </div>
    </td>
</tr></table>

{* Registro de actividad de la campaña *}
{literal}{{view Ember.Checkbox checkedBinding="registroVisible"}}{/literal}
<b>{$ETIQUETA_REGISTRO}: </b><br/>
{literal}{{#if registroVisible}}
<button class="button" {{action "cargarprevios" }}>{/literal}{$PREVIOUS_N}{literal}</button>
{{#view App.RegistroView class="registro" }}
<table>
    {{#each registro}}
    <tr>
        <td>{{timestamp}}</td>
        <td>{{mensaje}}</td>
    </tr>
    {{/each}}
</table>
{{/view}}
{{/if}}{/literal}
</script>

{* Context menu for agents on break *}
<div id="agentContextMenu" style="display: none;">
  <a href="#" id="btnUnbreakAgent">🔓 Finalizar Descanso</a>
  <a href="#" id="btnForceLoginAgent">🔑 Iniciar Sesión</a>
</div>
</div>
