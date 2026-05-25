<?php
/* vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
  Codificación: UTF-8
  +----------------------------------------------------------------------+
  | Issabel version 0.5                                                  |
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
  |                                                                      |
  | The Initial Developer of the Original Code is PaloSanto Solutions    |
  +----------------------------------------------------------------------+
*/

require_once 'libs/misc.lib.php';
require_once 'libs/paloSantoForm.class.php';
require_once 'libs/paloSantoGrid.class.php';
require_once "modules/agent_console/libs/issabel2.lib.php";

define ('LIMITE_PAGINA', 50);

if (!function_exists('_tr')) {
    function _tr($s)
    {
        global $arrLang;
        return isset($arrLang[$s]) ? $arrLang[$s] : $s;
    }
}
if (!function_exists('load_language_module')) {
    function load_language_module($module_id, $ruta_base='')
    {
        $lang = get_language($ruta_base);
        include_once $ruta_base."modules/$module_id/lang/en.lang";
        $lang_file_module = $ruta_base."modules/$module_id/lang/$lang.lang";
        if ($lang != 'en' && file_exists("$lang_file_module")) {
            $arrLangEN = $arrLangModule;
            include_once "$lang_file_module";
            $arrLangModule = array_merge($arrLangEN, $arrLangModule);
        }

        global $arrLang;
        global $arrLangModule;
        $arrLang = array_merge($arrLang,$arrLangModule);
    }
}

function _moduleContent(&$smarty, $module_name)
{
    load_language_module($module_name);

    include_once "modules/$module_name/configs/default.conf.php";
    global $arrConf;

    $arrConf = array_merge($arrConf, $arrConfModule);

    require_once "modules/$module_name/libs/paloSantoDashAgentJourney.class.php";

    $base_dir = dirname($_SERVER['SCRIPT_FILENAME']);
    $templates_dir = (isset($arrConf['templates_dir']))?$arrConf['templates_dir']:'themes';
    $local_templates_dir = "$base_dir/modules/$module_name/".$templates_dir.'/'.$arrConf['theme'];

    $pDB = new paloDB($arrConf["cadena_dsn"]);
    if (!is_object($pDB->conn) || $pDB->errMsg!="") {
        $smarty->assign('mb_message', _tr('Error when connecting to database')." ".$pDB->errMsg);
        return NULL;
    }

    $action = getParameter("action");

    if ($action == "get_metrics") {
        return getMetricsJSON($pDB, $module_name);
    } else {
        return showDashboard($pDB, $smarty, $module_name, $local_templates_dir);
    }
}

function showDashboard($pDB, $smarty, $module_name, $local_templates_dir)
{
    $oJourney = new paloSantoDashAgentJourney($pDB);
    $smarty->assign(array(
        'SHOW'      =>  _tr('Show'),
        'Filter'    =>  _tr('Find'),
    ));

    // Get list of agents for dropdown
    $listaAgentes = $oJourney->getAgents();
    $comboAgentes = array('' => '('._tr('All Agents').')');
    if (is_array($listaAgentes)) {
        foreach ($listaAgentes as $tuplaAgente) {
            $sDesc = $tuplaAgente['number'].' - '.$tuplaAgente['name'];
            if ($tuplaAgente['estatus'] != 'A') $sDesc .= ' ('.$tuplaAgente['estatus'].')';
            $comboAgentes[$tuplaAgente['id']] = $sDesc;
        }
    }

    $arrFormElements = array(
        'date_start'  => array(
            'LABEL'                  => _tr('Date Init'),
            'REQUIRED'               => 'yes',
            'INPUT_TYPE'             => 'DATE',
            'INPUT_EXTRA_PARAM'      => '',
            'VALIDATION_TYPE'        => 'ereg',
            'VALIDATION_EXTRA_PARAM' => '^[[:digit:]]{1,2}[[:space:]]+[[:alnum:]]{3}[[:space:]]+[[:digit:]]{4}$'),
        'date_end'    => array(
            'LABEL'                  => _tr('Date End'),
            'REQUIRED'               => 'yes',
            'INPUT_TYPE'             => 'DATE',
            'INPUT_EXTRA_PARAM'      => '',
            'VALIDATION_TYPE'        => 'ereg',
            'VALIDATION_EXTRA_PARAM' => '^[[:digit:]]{1,2}[[:space:]]+[[:alnum:]]{3}[[:space:]]+[[:digit:]]{4}$'),
        'agent'  => array(
            'LABEL'                  => _tr('Agent'),
            'REQUIRED'               => 'no',
            'INPUT_TYPE'             => 'SELECT',
            'INPUT_EXTRA_PARAM'      => $comboAgentes,
            'VALIDATION_TYPE'        => 'ereg',
            'VALIDATION_EXTRA_PARAM' => '^[[:digit:]]*$'),
        'holdincluded'  => array(
            'LABEL'                  => _tr('Hold Included'),
            'REQUIRED'               => 'no',
            'INPUT_TYPE'             => 'SELECT',
            'INPUT_EXTRA_PARAM'      => array(
                'no' => _tr('No'),
                'yes' => _tr('Yes')),
            'VALIDATION_TYPE'        => 'text',
            'VALIDATION_EXTRA_PARAM' => ''),
    );
    $oFilterForm = new paloForm($smarty, $arrFormElements);

    $url = array('menu' => $module_name);
    $paramFiltroBase = $paramFiltro = array(
        'date_start'    =>  date('d M Y'),
        'date_end'      =>  date('d M Y'),
        'agent'         =>  '',
        'holdincluded'  =>  'no',
    );
    foreach (array_keys($paramFiltro) as $k) {
        if (!is_null(getParameter($k))){
            $paramFiltro[$k] = getParameter($k);
        }
    }

    $htmlFilter = $oFilterForm->fetchForm("$local_templates_dir/filter.tpl", "", $paramFiltro);
    if (!$oFilterForm->validateForm($paramFiltro)) {
        $smarty->assign(array(
            'mb_title'      =>  _tr('Validation Error'),
            'mb_message'    =>  '<b>'._tr('The following fields contain errors').':</b><br/>'.
                                implode(', ', array_keys($oFilterForm->arrErroresValidacion)),
        ));
        $paramFiltro = $paramFiltroBase;
    }

    $smarty->assign("FILTER_HTML", $htmlFilter);
    $smarty->assign("MODULE_NAME", $module_name);
    
    $smarty->assign("CHARTJS", "<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>");

    $html = $smarty->fetch("$local_templates_dir/dash_agent_journey.tpl");

    $oGrid = new paloSantoGrid($smarty);
    $oGrid->setTitle(_tr('Dash Agent Journey'));
    $oGrid->showFilter($htmlFilter);
    $oGrid->customHTML($html);

    return $oGrid->fetchGrid();
}

function getMetricsJSON($pDB, $module_name) {
    header('Content-Type: application/json');
    $oJourney = new paloSantoDashAgentJourney($pDB);

    $date_start_raw = getParameter("date_start");
    $date_end_raw = getParameter("date_end");
    $agent_raw = getParameter("agent");
    $holdincluded_raw = getParameter("holdincluded");

    $date_start = empty($date_start_raw) ? date('Y-m-d 00:00:00') : translateDate($date_start_raw).' 00:00:00';
    $date_end = empty($date_end_raw) ? date('Y-m-d 23:59:59') : translateDate($date_end_raw).' 23:59:59';
    $idAgent = (trim($agent_raw) == '') ? NULL : (int)$agent_raw;
    $bHoldIncluded = ($holdincluded_raw == 'yes');

    $recordset = $oJourney->getAgentJourney($date_start, $date_end, $idAgent, $bHoldIncluded);
    
    if (!is_array($recordset)) {
        echo json_encode(array("error" => $oJourney->errMsg));
        return;
    }

    $metrics = calculateMetrics($recordset);
    echo json_encode($metrics);
    return;
}

function calculateMetrics($recordset) {
    $agents = array();
    $totals = array(
        'LOGIN' => 0,
        'LOGOUT' => 0,
        'BREAK' => 0,
        'INCOMING_CALL' => 0,
        'OUTGOING_CALL' => 0,
        'MANUAL_INCOMING' => 0,
        'MANUAL_OUTGOING' => 0,
        'HOLD' => 0
    );

    foreach ($recordset as $event) {
        $agentName = $event['name'];
        $type = $event['event_type'];
        $duration = (int)$event['duration'];

        if (!isset($agents[$agentName])) {
            $agents[$agentName] = array(
                'name' => $agentName,
                'number' => $event['number'],
                'events' => 0,
                'total_duration' => 0,
                'types' => array()
            );
        }

        if (!isset($agents[$agentName]['types'][$type])) {
            $agents[$agentName]['types'][$type] = 0;
        }

        $agents[$agentName]['events']++;
        if ($duration > 0) {
            $agents[$agentName]['total_duration'] += $duration;
            $agents[$agentName]['types'][$type] += $duration;
            
            if (isset($totals[$type])) {
                $totals[$type] += $duration;
            } else {
                $totals[$type] = $duration;
            }
        }
    }

    // Sort agents to find best/worst based on talk time (call events)
    $agentStats = array();
    foreach ($agents as $agent) {
        $talkTime = (isset($agent['types']['INCOMING_CALL']) ? $agent['types']['INCOMING_CALL'] : 0) + 
                    (isset($agent['types']['OUTGOING_CALL']) ? $agent['types']['OUTGOING_CALL'] : 0) +
                    (isset($agent['types']['MANUAL_INCOMING']) ? $agent['types']['MANUAL_INCOMING'] : 0) +
                    (isset($agent['types']['MANUAL_OUTGOING']) ? $agent['types']['MANUAL_OUTGOING'] : 0);
                    
        $breakTime = isset($agent['types']['BREAK']) ? $agent['types']['BREAK'] : 0;
        
        $agentStats[] = array(
            'name' => $agent['name'],
            'number' => $agent['number'],
            'talk_time' => $talkTime,
            'break_time' => $breakTime,
            'total_time' => $agent['total_duration']
        );
    }

    usort($agentStats, function($a, $b) {
        return $b['talk_time'] - $a['talk_time'];
    });

    $bestAgent = count($agentStats) > 0 ? $agentStats[0] : null;
    $worstAgent = count($agentStats) > 0 ? $agentStats[count($agentStats) - 1] : null;

    return array(
        "totals" => $totals,
        "agents" => array_values($agents),
        "agentStats" => $agentStats,
        "bestAgent" => $bestAgent,
        "worstAgent" => $worstAgent,
        "raw_events" => count($recordset)
    );
}
?>
