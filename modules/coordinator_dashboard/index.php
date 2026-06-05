<?php
/* vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
  Codificación: UTF-8
  +----------------------------------------------------------------------+
  | Issabel - Coordinator Dashboard Module                               |
  | Provides a premium real-time view for call center coordinators       |
  +----------------------------------------------------------------------+ */

require_once 'libs/paloSantoGrid.class.php';

function _moduleContent(&$smarty, $module_name)
{
    global $arrConf;
    global $arrLang;

    require_once "modules/agent_console/libs/issabel2.lib.php";
    require_once "modules/agent_console/libs/paloSantoConsola.class.php";
    require_once "modules/agent_console/libs/JSON.php";
    require_once "modules/$module_name/configs/default.conf.php";

    $arrConf = array_merge($arrConf, $arrConfModule);

    load_language_module($module_name);

    $smarty->assign("MODULE_NAME", $module_name);

    $sAction = getParameter('action');
    $allowedActions = array('', 'getAgentStatus', 'getCampaignList', 'getHourlyStats',
                            'spyAgent', 'forceUnbreakAgent', 'forceLoginAgent');
    if (!in_array($sAction, $allowedActions)) $sAction = '';

    switch ($sAction) {
    case 'getAgentStatus':
        return coordDash_getAgentStatus($module_name, $smarty, $arrConf);
    case 'getCampaignList':
        return coordDash_getCampaignList($module_name);
    case 'getHourlyStats':
        return coordDash_getHourlyStats();
    case 'spyAgent':
        return coordDash_spyAgent($arrConf);
    case 'forceUnbreakAgent':
        return coordDash_forceUnbreakAgent();
    case 'forceLoginAgent':
        return coordDash_forceLoginAgent();
    case '':
    default:
        return coordDash_renderHTML($module_name, $smarty, $arrConf);
    }
}

/* ============================================================
   HTML PRINCIPAL
   ============================================================ */
function coordDash_renderHTML($module_name, &$smarty, $arrConf)
{
    global $arrLang;

    require_once "modules/agent_console/libs/paloSantoConsola.class.php";

    $smarty->assign(array(
        'FRAMEWORK_TIENE_TITULO_MODULO' => existeSoporteTituloFramework(),
        'icon'  => 'modules/' . $module_name . '/images/icon.png',
        'title' => _tr('Coordinator Dashboard'),
    ));

    // Build queue list for filter
    $oPaloConsola = new PaloSantoConsola();
    $estadoMonitor = $oPaloConsola->listarEstadoMonitoreoAgentes();
    $oPaloConsola->desconectarTodo();

    $queues = array();
    if (is_array($estadoMonitor)) {
        foreach (array_keys($estadoMonitor) as $q) {
            $queues[] = $q;
        }
        sort($queues);
    }

    // Build hours options for shift filter
    $hoursOptions = array();
    for ($h = 0; $h < 24; $h++) {
        $hoursOptions[] = sprintf('%02d', $h);
    }

    $smarty->assign(array(
        'QUEUES'        => $queues,
        'HOURS_OPTIONS' => $hoursOptions,
        'LANG_JSON'     => json_encode(array(
            'all_queues'    => _tr('All Queues'),
            'all_statuses'  => _tr('All Statuses'),
            'online'        => _tr('Online'),
            'oncall'        => _tr('On Call'),
            'paused'        => _tr('Paused'),
            'offline'       => _tr('Offline'),
            'ringing'       => _tr('Ringing'),
            'hold'          => _tr('Hold'),
            'spy'           => _tr('Spy'),
            'unbreak'       => _tr('Unbreak'),
            'force_login'   => _tr('Force Login'),
            'calls_today'   => _tr('Calls Today'),
            'talk_time'     => _tr('Talk Time'),
            'break_time'    => _tr('Break Time'),
            'login_time'    => _tr('Login Time'),
            'no_agents'     => _tr('No agents found'),
            'loading'       => _tr('Loading'),
            'campaign'      => _tr('Campaign'),
            'queue'         => _tr('Queue'),
            'error'         => _tr('Error'),
        )),
        'MODULE_NAME'   => $module_name,
    ));

    $sDirScript = dirname($_SERVER['SCRIPT_FILENAME']);
    $sDirPlantillas = isset($arrConf['templates_dir']) ? $arrConf['templates_dir'] : 'themes';
    $sDirLocalPlantillas = "$sDirScript/modules/$module_name/" . $sDirPlantillas . '/' . $arrConf['theme'];

    return $smarty->fetch("file:$sDirLocalPlantillas/coordinator_dashboard.tpl");
}

/* ============================================================
   ACTION: getAgentStatus — returns full agent state as JSON
   ============================================================ */
function coordDash_getAgentStatus($module_name, &$smarty, $arrConf)
{
    require_once "modules/agent_console/libs/paloSantoConsola.class.php";

    Header('Content-Type: application/json');

    // Parse shift filter
    $shiftFrom = (int)getParameter('shift_from');
    $shiftTo   = (int)getParameter('shift_to');
    if ($shiftFrom < 0 || $shiftFrom > 23) $shiftFrom = 0;
    if ($shiftTo < 0   || $shiftTo > 23)   $shiftTo   = 23;
    $shiftRange = coordDash_calculateShiftRange($shiftFrom, $shiftTo);

    $oPaloConsola = new PaloSantoConsola();
    $estadoMonitor = $oPaloConsola->listarEstadoMonitoreoAgentes();
    if (!is_array($estadoMonitor)) {
        $oPaloConsola->desconectarTodo();
        return json_encode(array('status' => 'error', 'message' => $oPaloConsola->errMsg));
    }

    // Get agent name map from call_center.agent
    $agentNames = $oPaloConsola->listarAgentes();
    if (!is_array($agentNames)) $agentNames = array();

    // Get campaign name map
    $campaignNames = coordDash_buildCampaignMap($oPaloConsola);

    // Get DB metrics
    $breakData = coordDash_queryBreakTime($shiftRange['start'], $shiftRange['end']);
    $holdData  = coordDash_queryHoldTime($shiftRange['start'], $shiftRange['end']);
    $loginData = coordDash_queryLoginTime($shiftRange['start'], $shiftRange['end']);
    $callData  = coordDash_queryCallData($shiftRange['start'], $shiftRange['end']);

    $oPaloConsola->desconectarTodo();

    $iNow   = time();
    $agents = array();
    $seen   = array(); // deduplicate agents appearing in multiple queues

    ksort($estadoMonitor);
    foreach ($estadoMonitor as $sQueue => $agentList) {
        ksort($agentList);
        foreach ($agentList as $sAgentChannel => $info) {
            // Deduplicate: use first queue occurrence
            if (isset($seen[$sAgentChannel])) continue;
            $seen[$sAgentChannel] = true;

            // Resolve agent name
            $agentName = $sAgentChannel;
            if (isset($agentNames[$sAgentChannel])) {
                // Format is "PJSIP/1001 - Nombre Apellido" — extract only the name part
                $parts = explode(' - ', $agentNames[$sAgentChannel], 2);
                $agentName = isset($parts[1]) ? $parts[1] : $sAgentChannel;
            } else {
                // Try FreePBX users table fallback
                $agentName = coordDash_resolveNameFromFreePBX($sAgentChannel);
            }

            // Call info
            $callNumber   = null;
            $campaignId   = null;
            $campaignName = null;
            $linkStart    = null;
            $callType     = null;
            if (!is_null($info['linkstart'])) {
                $linkStart = strtotime($info['linkstart']);
            }
            if (isset($info['callnumber']) && $info['callnumber'] !== '') {
                $callNumber = $info['callnumber'];
            }
            if (isset($info['campaign_id']) && !is_null($info['campaign_id'])) {
                $campaignId   = $info['campaign_id'];
                $callType     = isset($info['calltype']) ? $info['calltype'] : null;
                $campaignKey  = $callType . ':' . $campaignId;
                $campaignName = isset($campaignNames[$campaignKey]) ? $campaignNames[$campaignKey] : null;
            }

            // Pause info
            $pauseName = null;
            if (isset($info['pausename']) && !is_null($info['pausename'])) {
                $pauseName = $info['pausename'];
            }

            // Metrics from DB
            $numCalls  = isset($callData[$sAgentChannel]['num_calls'])  ? (int)$callData[$sAgentChannel]['num_calls']  : 0;
            $secCalls  = isset($callData[$sAgentChannel]['sec_calls'])  ? (int)$callData[$sAgentChannel]['sec_calls']  : 0;
            $secBreaks = isset($breakData['breakTimes'][$sAgentChannel]) ? (int)$breakData['breakTimes'][$sAgentChannel] : 0;
            $secHolds  = isset($holdData[$sAgentChannel])               ? (int)$holdData[$sAgentChannel]               : 0;
            $loginTime = isset($loginData[$sAgentChannel])              ? (int)$loginData[$sAgentChannel]              : 0;

            // Add active call duration if oncall
            $activeDur = 0;
            if (!is_null($linkStart)) {
                $activeDur = max(0, $iNow - $linkStart);
                $numCalls++; // count current call
            }

            $agents[] = array(
                'channel'       => $sAgentChannel,
                'name'          => $agentName,
                'status'        => $info['agentstatus'],
                'queue'         => $sQueue,
                'call_number'   => $callNumber,
                'campaign_id'   => $campaignId,
                'campaign_name' => $campaignName,
                'call_type'     => $callType,
                'link_start'    => $linkStart,       // unix timestamp, for JS timer
                'pause_name'    => $pauseName,
                'on_hold'       => (bool)$info['onhold'],
                'num_calls'     => $numCalls,
                'sec_calls'     => $secCalls + $activeDur,
                'sec_breaks'    => $secBreaks,
                'sec_holds'     => $secHolds,
                'login_time'    => $loginTime,
                'server_time'   => $iNow,
            );
        }
    }

    // KPI summary
    $kpi = array('online' => 0, 'oncall' => 0, 'paused' => 0, 'offline' => 0, 'ringing' => 0);
    foreach ($agents as $a) {
        $st = $a['status'];
        if ($st === 'online')   $kpi['online']++;
        elseif ($st === 'oncall')  $kpi['oncall']++;
        elseif ($st === 'paused')  $kpi['paused']++;
        elseif ($st === 'offline') $kpi['offline']++;
        elseif ($st === 'ringing') $kpi['ringing']++;
    }

    return json_encode(array(
        'status'  => 'success',
        'agents'  => $agents,
        'kpi'     => $kpi,
        'ts'      => $iNow,
    ));
}

/* ============================================================
   ACTION: getCampaignList
   ============================================================ */
function coordDash_getCampaignList($module_name)
{
    require_once "modules/agent_console/libs/paloSantoConsola.class.php";
    Header('Content-Type: application/json');

    $oPaloConsola = new PaloSantoConsola();
    $listaCampanias = $oPaloConsola->leerListaCampanias();
    $oPaloConsola->desconectarTodo();

    if (!is_array($listaCampanias)) {
        return json_encode(array('status' => 'error', 'campaigns' => array()));
    }

    $out = array();
    foreach ($listaCampanias as $c) {
        if ($c['status'] === 'A') {
            $out[] = array(
                'id'     => $c['id'],
                'name'   => $c['name'],
                'type'   => $c['type'],
                'status' => $c['status'],
            );
        }
    }
    return json_encode(array('status' => 'success', 'campaigns' => $out));
}

/* ============================================================
   ACTION: getHourlyStats — calls per hour for last 12 hours
   ============================================================ */
function coordDash_getHourlyStats()
{
    Header('Content-Type: application/json');

    try {
        $pDB = new PDO('mysql:host=localhost;dbname=call_center;charset=utf8', 'asterisk', 'asterisk');
        $pDB->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch (PDOException $e) {
        return json_encode(array('status' => 'error', 'data' => array()));
    }

    $hours = array();
    for ($i = 11; $i >= 0; $i--) {
        $hours[] = date('Y-m-d H', strtotime("-$i hours")) . ':00:00';
    }

    // Query incoming + outgoing grouped by hour
    $sql = "SELECT HOUR(datetime_init) AS hr, COUNT(*) AS cnt
            FROM call_entry
            WHERE datetime_init >= DATE_SUB(NOW(), INTERVAL 12 HOUR)
            GROUP BY HOUR(datetime_init)
            UNION ALL
            SELECT HOUR(start_time) AS hr, COUNT(*) AS cnt
            FROM calls
            WHERE start_time >= DATE_SUB(NOW(), INTERVAL 12 HOUR)
            GROUP BY HOUR(start_time)";

    $raw = array();
    try {
        $stmt = $pDB->query($sql);
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $hr = (int)$row['hr'];
            $raw[$hr] = isset($raw[$hr]) ? $raw[$hr] + (int)$row['cnt'] : (int)$row['cnt'];
        }
    } catch (PDOException $e) {}

    $data = array();
    for ($i = 11; $i >= 0; $i--) {
        $hr   = (int)date('H', strtotime("-$i hours"));
        $label = date('H:00', strtotime("-$i hours"));
        $data[] = array('label' => $label, 'value' => isset($raw[$hr]) ? $raw[$hr] : 0);
    }

    $pDB = null;
    return json_encode(array('status' => 'success', 'data' => $data));
}

/* ============================================================
   ACTION: spyAgent — listen to an agent call via ChanSpy AMI
   ============================================================ */
function coordDash_spyAgent($arrConf)
{
    Header('Content-Type: application/json');
    $resp = array('status' => 'success', 'message' => '');

    $sAgentChannel = getParameter('agentchannel');
    if (empty($sAgentChannel)) {
        return json_encode(array('status' => 'error', 'message' => 'Canal de agente no válido'));
    }

    // Get supervisor extension from ACL session
    $user = isset($_SESSION['issabel_user']) ? $_SESSION['issabel_user'] : null;
    $sSupervisorExt = null;
    if (!is_null($user) && isset($arrConf['issabel_dsn']['acl'])) {
        require_once 'libs/paloSantoDB.class.php';
        require_once 'libs/paloACL.class.php';
        $pDB_acl = new paloDB($arrConf['issabel_dsn']['acl']);
        $pACL    = new paloACL($pDB_acl);
        $sSupervisorExt = $pACL->getUserExtension($user);
    }

    if (empty($sSupervisorExt)) {
        return json_encode(array('status' => 'error', 'message' => 'Su usuario no tiene extensión telefónica asociada en ACL'));
    }

    // Extract extension number from channel
    $agentExt = null;
    if (preg_match('/(?:Agent|SIP|PJSIP|IAX2)\\/([\\d]+)/i', $sAgentChannel, $m)) {
        $agentExt = $m[1];
    }
    if (is_null($agentExt)) {
        return json_encode(array('status' => 'error', 'message' => 'No se pudo extraer extensión del canal: ' . $sAgentChannel));
    }

    // Get ChanSpy feature code
    $chanspyCode = '555';
    $dsnAsterisk = generarDSNSistema('asteriskuser', 'asterisk');
    $pDB_ast = new paloDB($dsnAsterisk);
    if (empty($pDB_ast->errMsg)) {
        $res = $pDB_ast->fetchTable("SELECT code FROM featurecodes WHERE modulename = 'core' AND feature = 'chanspy' AND active = 1", TRUE);
        if (is_array($res) && count($res) > 0 && !empty($res[0]['code'])) {
            $chanspyCode = $res[0]['code'];
        }
    }

    // AMI Originate
    require_once '/var/lib/asterisk/agi-bin/phpagi-asmanager.php';
    $astman = new AGI_AsteriskManager();
    if (!$astman->connect("127.0.0.1", 'admin', obtenerClaveAMIAdmin())) {
        return json_encode(array('status' => 'error', 'message' => 'No se pudo conectar a AMI de Asterisk'));
    }

    $origResult = $astman->Originate(array(
        'Channel'  => "local/$sSupervisorExt@from-internal",
        'Exten'    => "$chanspyCode$agentExt",
        'Context'  => 'from-internal',
        'Priority' => '1',
        'Async'    => 'true',
        'CallerID' => "Escucha: $agentExt <$chanspyCode$agentExt>",
    ));
    $astman->disconnect();

    if (isset($origResult['Response']) && strtolower($origResult['Response']) === 'success') {
        return json_encode(array('status' => 'success', 'message' => 'Escucha iniciada — su teléfono sonará en breve'));
    }
    $msg = isset($origResult['Message']) ? $origResult['Message'] : 'Respuesta fallida de Asterisk AMI';
    return json_encode(array('status' => 'error', 'message' => $msg));
}

/* ============================================================
   ACTION: forceUnbreakAgent
   ============================================================ */
function coordDash_forceUnbreakAgent()
{
    require_once "modules/agent_console/libs/paloSantoConsola.class.php";
    Header('Content-Type: application/json');

    $sAgentChannel = getParameter('agentchannel');
    if (empty($sAgentChannel)) {
        return json_encode(array('status' => 'error', 'message' => 'Canal de agente no válido'));
    }

    $oConsola = new PaloSantoConsola($sAgentChannel);
    $exito = $oConsola->terminarBreak();
    $oConsola->desconectarTodo();

    if (!$exito) {
        return json_encode(array('status' => 'error', 'message' => $oConsola->errMsg));
    }
    return json_encode(array('status' => 'success', 'message' => 'Despausa aplicada'));
}

/* ============================================================
   ACTION: forceLoginAgent
   ============================================================ */
function coordDash_forceLoginAgent()
{
    require_once "modules/agent_console/libs/paloSantoConsola.class.php";
    Header('Content-Type: application/json');

    $sAgentChannel = getParameter('agentchannel');
    if (empty($sAgentChannel)) {
        return json_encode(array('status' => 'error', 'message' => 'Canal de agente no válido'));
    }

    $oConsola = new PaloSantoConsola($sAgentChannel);
    $exito = $oConsola->loginAgente($sAgentChannel);
    $oConsola->desconectarTodo();

    if (!$exito) {
        return json_encode(array('status' => 'error', 'message' => $oConsola->errMsg));
    }
    return json_encode(array('status' => 'success', 'message' => 'Login enviado al agente'));
}

/* ============================================================
   HELPERS — DB QUERIES
   ============================================================ */
function coordDash_calculateShiftRange($fromHour, $toHour)
{
    $today     = date('Y-m-d');
    $yesterday = date('Y-m-d', strtotime('-1 day'));
    if ($fromHour > $toHour) {
        return array(
            'start' => $yesterday . ' ' . sprintf('%02d:00:00', $fromHour),
            'end'   => $today    . ' ' . sprintf('%02d:59:59', $toHour),
        );
    }
    return array(
        'start' => $today . ' ' . sprintf('%02d:00:00', $fromHour),
        'end'   => $today . ' ' . sprintf('%02d:59:59', $toHour),
    );
}

function coordDash_getPDO()
{
    static $pDB = null;
    if (is_null($pDB)) {
        try {
            $pDB = new PDO('mysql:host=localhost;dbname=call_center;charset=utf8', 'asterisk', 'asterisk');
            $pDB->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        } catch (PDOException $e) {
            return null;
        }
    }
    return $pDB;
}

function coordDash_queryBreakTime($start, $end)
{
    $result = array('breakTimes' => array(), 'holdNames' => array());
    $pDB = coordDash_getPDO();
    if (!$pDB) return $result;

    $sql = "SELECT CONCAT(agent.type, '/', agent.number) AS ch,
            SUM(UNIX_TIMESTAMP(audit.datetime_end) - UNIX_TIMESTAMP(audit.datetime_init)) AS sec_breaks
            FROM audit
            INNER JOIN break ON break.id = audit.id_break
            INNER JOIN agent ON agent.id = audit.id_agent
            WHERE break.tipo = 'B'
            AND audit.datetime_end IS NOT NULL
            AND audit.datetime_init >= :start
            AND audit.datetime_init <= :end
            GROUP BY agent.id";
    try {
        $stmt = $pDB->prepare($sql);
        $stmt->execute(array(':start' => $start, ':end' => $end));
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $result['breakTimes'][$row['ch']] = (int)$row['sec_breaks'];
        }
        $stmt2 = $pDB->query("SELECT name FROM break WHERE tipo = 'H' AND status = 'A'");
        while ($row = $stmt2->fetch(PDO::FETCH_ASSOC)) {
            $result['holdNames'][] = $row['name'];
        }
    } catch (PDOException $e) {}
    return $result;
}

function coordDash_queryHoldTime($start, $end)
{
    $result = array();
    $pDB = coordDash_getPDO();
    if (!$pDB) return $result;

    $sql = "SELECT CONCAT(agent.type, '/', agent.number) AS ch,
            SUM(UNIX_TIMESTAMP(audit.datetime_end) - UNIX_TIMESTAMP(audit.datetime_init)) AS sec_holds
            FROM audit
            INNER JOIN break ON break.id = audit.id_break
            INNER JOIN agent ON agent.id = audit.id_agent
            WHERE break.tipo = 'H'
            AND audit.datetime_end IS NOT NULL
            AND audit.datetime_init >= :start
            AND audit.datetime_init <= :end
            GROUP BY agent.id";
    try {
        $stmt = $pDB->prepare($sql);
        $stmt->execute(array(':start' => $start, ':end' => $end));
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $result[$row['ch']] = (int)$row['sec_holds'];
        }
    } catch (PDOException $e) {}
    return $result;
}

function coordDash_queryLoginTime($start, $end)
{
    $result = array();
    $pDB = coordDash_getPDO();
    if (!$pDB) return $result;

    $sNow       = date('Y-m-d H:i:s');
    $sActiveEnd = ($sNow < $end) ? $sNow : $end;

    $sql = "SELECT CONCAT(agent.type, '/', agent.number) AS ch,
            SUM(
              UNIX_TIMESTAMP(LEAST(COALESCE(audit.datetime_end, :active_end), :end1))
              - UNIX_TIMESTAMP(GREATEST(audit.datetime_init, :start1))
            ) AS logintime
            FROM audit
            INNER JOIN agent ON agent.id = audit.id_agent
            WHERE audit.id_break IS NULL
            AND audit.datetime_init <= :end2
            AND (audit.datetime_end IS NULL OR audit.datetime_end >= :start2)
            GROUP BY agent.id
            HAVING logintime > 0";
    try {
        $stmt = $pDB->prepare($sql);
        $stmt->execute(array(
            ':active_end' => $sActiveEnd,
            ':start1'     => $start,
            ':end1'       => $end,
            ':start2'     => $start,
            ':end2'       => $end,
        ));
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $result[$row['ch']] = (int)$row['logintime'];
        }
    } catch (PDOException $e) {}
    return $result;
}

function coordDash_queryCallData($start, $end)
{
    $result = array();
    $pDB = coordDash_getPDO();
    if (!$pDB) return $result;

    // Incoming
    $sql1 = "SELECT CONCAT(agent.type, '/', agent.number) AS ch,
              SUM(call_entry.duration) AS sec_calls, COUNT(*) AS num_calls
              FROM call_entry
              INNER JOIN agent ON agent.id = call_entry.id_agent
              WHERE call_entry.datetime_init >= :start AND call_entry.datetime_init <= :end
              AND call_entry.duration IS NOT NULL
              GROUP BY call_entry.id_agent";
    // Outgoing
    $sql2 = "SELECT CONCAT(agent.type, '/', agent.number) AS ch,
              SUM(calls.duration) AS sec_calls, COUNT(*) AS num_calls
              FROM calls
              INNER JOIN agent ON agent.id = calls.id_agent
              WHERE calls.start_time >= :start AND calls.start_time <= :end
              AND calls.duration IS NOT NULL
              GROUP BY calls.id_agent";
    try {
        foreach (array($sql1, $sql2) as $sql) {
            $stmt = $pDB->prepare($sql);
            $stmt->execute(array(':start' => $start, ':end' => $end));
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $ch = $row['ch'];
                $result[$ch]['sec_calls'] = (isset($result[$ch]['sec_calls']) ? $result[$ch]['sec_calls'] : 0) + (int)$row['sec_calls'];
                $result[$ch]['num_calls'] = (isset($result[$ch]['num_calls']) ? $result[$ch]['num_calls'] : 0) + (int)$row['num_calls'];
            }
        }
    } catch (PDOException $e) {}
    return $result;
}

function coordDash_buildCampaignMap($oPaloConsola)
{
    $map = array();
    $list = $oPaloConsola->leerListaCampanias();
    if (!is_array($list)) return $map;
    foreach ($list as $c) {
        $key = $c['type'] . ':' . $c['id'];
        $map[$key] = $c['name'];
    }
    return $map;
}

function coordDash_resolveNameFromFreePBX($sAgentChannel)
{
    // Extract numeric extension
    if (!preg_match('/(?:SIP|PJSIP|IAX2|Agent)\\/([\\d]+)/i', $sAgentChannel, $m)) {
        return $sAgentChannel;
    }
    $ext = $m[1];

    try {
        $pDB = new PDO('mysql:host=localhost;dbname=asterisk;charset=utf8', 'asteriskuser', 'amp109');
        $pDB->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $stmt = $pDB->prepare("SELECT name FROM users WHERE extension = ? LIMIT 1");
        $stmt->execute(array($ext));
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row && !empty($row['name'])) return $row['name'];
    } catch (PDOException $e) {}

    return $sAgentChannel;
}
?>
