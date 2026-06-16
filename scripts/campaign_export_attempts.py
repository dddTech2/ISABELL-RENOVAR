import os
import sys

# Compute path to target files relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

model_file = os.path.join(project_dir, "modules", "campaign_out", "libs", "paloSantoCampaignCC.class.php")
controller_file = os.path.join(project_dir, "modules", "campaign_out", "index.php")
es_lang_file = os.path.join(project_dir, "modules", "campaign_out", "lang", "es.lang")
en_lang_file = os.path.join(project_dir, "modules", "campaign_out", "lang", "en.lang")

# 1. Modify Model (paloSantoCampaignCC.class.php)
print(f"Modifying Model: {model_file}")
if not os.path.exists(model_file):
    print(f"Error: {model_file} not found.", file=sys.stderr)
    sys.exit(1)

with open(model_file, "r", encoding="utf-8") as f:
    model_content = f.read()

orig_model_end = """        return $datosCampania;
    }
}"""

repl_model_end = """        return $datosCampania;
    }

    function getCampaignAttemptsData($campaign_ids)
    {
        $this->errMsg = NULL;
        if (!is_array($campaign_ids) || count($campaign_ids) == 0) {
            $this->errMsg = _tr('No campaign IDs provided');
            return NULL;
        }

        // Validate campaign IDs
        foreach ($campaign_ids as $id) {
            if (!ctype_digit((string)$id)) {
                $this->errMsg = _tr('Invalid campaign ID');
                return NULL;
            }
        }

        $placeholders = implode(',', array_fill(0, count($campaign_ids), '?'));
        $sqlAttempts = <<<SQL_ATTEMPTS
SELECT
    camp.name           AS camp_name,
    calls.phone         AS telefono,
    cpl.datetime_entry  AS fecha_hora,
    cpl.retry           AS intento,
    cpl.new_status      AS estado,
    a.number            AS agente,
    cpl.trunk           AS trunk,
    cpl.duration        AS duracion
FROM call_progress_log cpl
INNER JOIN calls ON cpl.id_call_outgoing = calls.id
INNER JOIN campaign camp ON calls.id_campaign = camp.id
LEFT JOIN agent a ON cpl.id_agent = a.id
WHERE calls.id_campaign IN ($placeholders)
ORDER BY camp.name, cpl.datetime_entry ASC
SQL_ATTEMPTS;

        $datosAttempts = $this->_DB->fetchTable($sqlAttempts, TRUE, $campaign_ids);
        if (!is_array($datosAttempts)) {
            $this->errMsg = 'Unable to read campaign attempts data - '.$this->_DB->errMsg;
            return NULL;
        }

        return $datosAttempts;
    }
}"""

if orig_model_end not in model_content:
    print("Error: Could not find exact text match to insert new method in model.", file=sys.stderr)
    sys.exit(1)

model_content = model_content.replace(orig_model_end, repl_model_end)

with open(model_file, "w", encoding="utf-8") as f:
    f.write(model_content)


# 2. Modify Controller (index.php)
print(f"Modifying Controller: {controller_file}")
if not os.path.exists(controller_file):
    print(f"Error: {controller_file} not found.", file=sys.stderr)
    sys.exit(1)

with open(controller_file, "r", encoding="utf-8") as f:
    controller_content = f.read()

# Replace A: Routing hook
orig_routing = """    $sAction = 'list_campaign';
    if (isset($_GET['action'])) $sAction = $_GET['action'];
    switch ($sAction) {"""

repl_routing = """    $sAction = 'list_campaign';
    if (isset($_GET['action'])) $sAction = $_GET['action'];
    if (isset($_POST['csv_attempts'])) {
        $has_campaigns = false;
        if (isset($_POST['id_campaign'])) {
            if (is_array($_POST['id_campaign'])) {
                foreach ($_POST['id_campaign'] as $id) {
                    if (ctype_digit($id)) { $has_campaigns = true; break; }
                }
            } elseif (ctype_digit($_POST['id_campaign'])) {
                $has_campaigns = true;
            }
        }
        if ($has_campaigns) {
            $sAction = 'csv_attempts';
        }
    }
    switch ($sAction) {"""

# Replace B: Case in switch routing
orig_switch_case = """    case 'csv_data':
        $contenidoModulo = displayCampaignCSV($pDB, $smarty, $module_name, $local_templates_dir);
        break;"""

repl_switch_case = """    case 'csv_data':
        $contenidoModulo = displayCampaignCSV($pDB, $smarty, $module_name, $local_templates_dir);
        break;
    case 'csv_attempts':
        $contenidoModulo = displayCampaignAttemptsCSV($pDB, $smarty, $module_name, $local_templates_dir);
        break;"""

# Replace C: Grid action handler for checkbox list
orig_grid_action_handler = """    // Recoger ID de campaña para operación
    $id_campaign = NULL;
    if (isset($_POST['id_campaign']) && ctype_digit($_POST['id_campaign']))
        $id_campaign = $_POST['id_campaign'];

    // Revisar si se debe de borrar una campaña elegida
    if (isset($_POST['delete']) && !is_null($id_campaign)) {
        if($oCampaign->delete_campaign($id_campaign)) {
            $smarty->assign("mb_title",_tr('Message'));
            $smarty->assign("mb_message", _tr('Campaign was deleted successfully'));
        } else {
            $msg_error = ($oCampaign->errMsg!="") ? "<br/>".$oCampaign->errMsg:"";
            $smarty->assign("mb_title", _tr('Delete Error'));
            $smarty->assign("mb_message", _tr('Error when deleting the Campaign').$msg_error);
        }
    }

    // Activar o desactivar campañas elegidas
    if (isset($_POST['change_status']) && !is_null($id_campaign)){
        if($_POST['status_campaing_sel']=='activate'){
            if(!$oCampaign->activar_campaign($id_campaign, 'A')) {
                $smarty->assign("mb_title", _tr('Activate Error'));
                $smarty->assign("mb_message", _tr('Error when Activating the Campaign').': '.$oCampaign->errMsg);
            }
        }elseif($_POST['status_campaing_sel']=='deactivate'){
            if(!$oCampaign->activar_campaign($id_campaign, 'I')) {
                $smarty->assign("mb_title", _tr('Desactivate Error'));
                $smarty->assign("mb_message", _tr('Error when desactivating the Campaign').': '.$oCampaign->errMsg);
            }
        }
    }"""

repl_grid_action_handler = """    // Recoger ID de campaña para operación
    $id_campaign = NULL;
    $campaign_ids = array();
    if (isset($_POST['id_campaign'])) {
        if (is_array($_POST['id_campaign'])) {
            foreach ($_POST['id_campaign'] as $id) {
                if (ctype_digit($id)) $campaign_ids[] = (int)$id;
            }
            if (count($campaign_ids) > 0) {
                $id_campaign = $campaign_ids[0];
            }
        } elseif (ctype_digit($_POST['id_campaign'])) {
            $id_campaign = $_POST['id_campaign'];
            $campaign_ids[] = (int)$id_campaign;
        }
    }

    // Interceptar error si se pulsa csv_attempts sin seleccionar campañas
    if (isset($_POST['csv_attempts']) && count($campaign_ids) == 0) {
        $smarty->assign("mb_title", _tr("Validation Error"));
        $smarty->assign("mb_message", _tr("Please select at least one campaign to download attempts"));
    }

    // Revisar si se debe de borrar una campaña elegida
    if (isset($_POST['delete']) && count($campaign_ids) > 0) {
        $exito = true;
        foreach ($campaign_ids as $id) {
            if (!$oCampaign->delete_campaign($id)) {
                $exito = false;
                $msg_error = ($oCampaign->errMsg!="") ? "<br/>".$oCampaign->errMsg:"";
                $smarty->assign("mb_title", _tr('Delete Error'));
                $smarty->assign("mb_message", _tr('Error when deleting the Campaign').$msg_error);
                break;
            }
        }
        if ($exito) {
            $smarty->assign("mb_title",_tr('Message'));
            $smarty->assign("mb_message", _tr('Campaign was deleted successfully'));
        }
    }

    // Activar o desactivar campañas elegidas
    if (isset($_POST['change_status']) && count($campaign_ids) > 0){
        $exito = true;
        $status_to_set = ($_POST['status_campaing_sel'] == 'activate') ? 'A' : 'I';
        foreach ($campaign_ids as $id) {
            if (!$oCampaign->activar_campaign($id, $status_to_set)) {
                $exito = false;
                $mb_title = ($status_to_set == 'A') ? _tr('Activate Error') : _tr('Desactivate Error');
                $mb_msg = ($status_to_set == 'A') ? _tr('Error when Activating the Campaign') : _tr('Error when desactivating the Campaign');
                $smarty->assign("mb_title", $mb_title);
                $smarty->assign("mb_message", $mb_msg.': '.$oCampaign->errMsg);
                break;
            }
        }
    }"""

# Replace D: Grid column row input type (radio to checkbox)
orig_grid_row_input = """                "<input class=\\"button\\" type=\\"radio\\" name=\\"id_campaign\\" value=\\"$campaign[id]\\" />","""

repl_grid_row_input = """                "<input class=\\"button\\" type=\\"checkbox\\" name=\\"id_campaign[]\\" value=\\"$campaign[id]\\" />","""

# Replace E: Grid header column select all checkbox
orig_grid_header = """    $oGrid->setColumns(array('', 'ID', _tr('Name Campaign'),"""

repl_grid_header = """    $oGrid->setColumns(array(
        "<input type=\\"checkbox\\" id=\\"select_all_campaigns\\" onclick=\\"var checkboxes = document.getElementsByName('id_campaign[]'); for (var i = 0; i < checkboxes.length; i++) { checkboxes[i].checked = this.checked; }\\" />",
        'ID',
        _tr('Name Campaign'),"""

# Replace F: Grid Action custom button registration
orig_custom_action = """    $oGrid->deleteList('Are you sure you wish to delete campaign?', 'delete', _tr('Delete'));
    $oGrid->setData($arrData);"""

repl_custom_action = """    $oGrid->deleteList('Are you sure you wish to delete campaign?', 'delete', _tr('Delete'));
    $oGrid->customAction("csv_attempts", _tr("Download Attempts CSV"), "download", false);
    $oGrid->setData($arrData);"""

# Replace G: Append displayCampaignAttemptsCSV function at end of index.php
orig_controller_end = """    return $oForm->fetchForm(
        "$local_templates_dir/duplicate.tpl",
        _tr("Duplicate Campaign"),
        $_POST
    );
}

?>"""

repl_controller_end = """    return $oForm->fetchForm(
        "$local_templates_dir/duplicate.tpl",
        _tr("Duplicate Campaign"),
        $_POST
    );
}

function displayCampaignAttemptsCSV($pDB, $smarty, $module_name, $local_templates_dir)
{
    $campaign_ids = array();
    if (isset($_POST['id_campaign'])) {
        if (is_array($_POST['id_campaign'])) {
            foreach ($_POST['id_campaign'] as $id) {
                if (ctype_digit($id)) $campaign_ids[] = (int)$id;
            }
        } elseif (ctype_digit($_POST['id_campaign'])) {
            $campaign_ids[] = (int)$_POST['id_campaign'];
        }
    }

    if (count($campaign_ids) == 0) {
        Header("Location: ?menu=$module_name");
        return '';
    }

    ini_set('max_execution_time', 3600);

    $oCampaign = new paloSantoCampaignCC($pDB);
    $datosAttempts = $oCampaign->getCampaignAttemptsData($campaign_ids);

    header("Cache-Control: private");
    header("Pragma: cache");
    header('Content-Type: text/csv; charset=UTF-8; header=present');
    header("Content-disposition: attachment; filename=\\"campaign_attempts_report.csv\\"");

    $sDatosCSV = '';
    if (is_null($datosAttempts) || count($datosAttempts) <= 0) {
        $sDatosCSV = "No Data Found\\r\\n";
    } else {
        $headers = array(
            _tr('Campaign Name'),
            _tr('Phone Customer'),
            _tr('Date & Time'),
            _tr('Attempt Number'),
            _tr('Status'),
            _tr('Agent'),
            _tr('Trunk'),
            _tr('Duration')
        );
        $sDatosCSV .= join(',', array_map('csv_replace', $headers))."\\r\\n";

        foreach ($datosAttempts as $row) {
            $linea = array(
                $row['camp_name'],
                $row['telefono'],
                $row['fecha_hora'],
                $row['intento'],
                $row['estado'],
                is_null($row['agente']) ? '' : $row['agente'],
                $row['trunk'],
                $row['duracion']
            );
            $sDatosCSV .= join(',', array_map('csv_replace', $linea))."\\r\\n";
        }
    }

    return $sDatosCSV;
}

?>"""

# Verify all controller search tags are present
all_ok = True
for label, orig in [
    ("routing", orig_routing),
    ("switch_case", orig_switch_case),
    ("grid_action_handler", orig_grid_action_handler),
    ("grid_row_input", orig_grid_row_input),
    ("grid_header", orig_grid_header),
    ("custom_action", orig_custom_action),
    ("controller_end", orig_controller_end)
]:
    if orig not in controller_content:
        print(f"Error: Could not find exact text match for controller: {label}", file=sys.stderr)
        all_ok = False

if not all_ok:
    sys.exit(1)

# Apply controller replacements
controller_content = controller_content.replace(orig_routing, repl_routing)
controller_content = controller_content.replace(orig_switch_case, repl_switch_case)
controller_content = controller_content.replace(orig_grid_action_handler, repl_grid_action_handler)
controller_content = controller_content.replace(orig_grid_row_input, repl_grid_row_input)
controller_content = controller_content.replace(orig_grid_header, repl_grid_header)
controller_content = controller_content.replace(orig_custom_action, repl_custom_action)
controller_content = controller_content.replace(orig_controller_end, repl_controller_end)

with open(controller_file, "w", encoding="utf-8") as f:
    f.write(controller_content)


# 3. Modify Spanish Translations (es.lang)
print(f"Modifying Spanish Lang: {es_lang_file}")
if os.path.exists(es_lang_file):
    with open(es_lang_file, "r", encoding="utf-8") as f:
        es_content = f.read()
    
    orig_es_end = """    "Error when duplicating the Campaign" => "Error al duplicar la campaña",
);"""
    
    repl_es_end = """    "Error when duplicating the Campaign" => "Error al duplicar la campaña",
    "Campaign Name" => "Nombre de Campaña",
    "Attempt Number" => "Número de Intento",
    "Download Attempts CSV" => "Descargar CSV de Intentos",
    "Please select at least one campaign to download attempts" => "Por favor seleccione al menos una campaña para descargar los intentos",
);"""
    
    if orig_es_end in es_content:
        es_content = es_content.replace(orig_es_end, repl_es_end)
        with open(es_lang_file, "w", encoding="utf-8") as f:
            f.write(es_content)
    else:
        print("Warning: Could not find exact text match to insert translations in es.lang")

# 4. Modify English Translations (en.lang)
print(f"Modifying English Lang: {en_lang_file}")
if os.path.exists(en_lang_file):
    with open(en_lang_file, "r", encoding="utf-8") as f:
        en_content = f.read()
    
    orig_en_end = """    "Error when duplicating the Campaign" => "Error when duplicating the Campaign",
);"""
    
    repl_en_end = """    "Error when duplicating the Campaign" => "Error when duplicating the Campaign",
    "Campaign Name" => "Campaign Name",
    "Attempt Number" => "Attempt Number",
    "Download Attempts CSV" => "Download Attempts CSV",
    "Please select at least one campaign to download attempts" => "Please select at least one campaign to download attempts",
);"""
    
    if orig_en_end in en_content:
        en_content = en_content.replace(orig_en_end, repl_en_end)
        with open(en_lang_file, "w", encoding="utf-8") as f:
            f.write(en_content)
    else:
        print("Warning: Could not find exact text match to insert translations in en.lang")

print("All modifications completed successfully!")
