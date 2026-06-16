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

# We need to find getCampaignAttemptsData and replace it with the new version that returns both attempts and attributes.
# If it doesn't exist yet (because we are overwriting or running it on an unmodified branch), we can check for both cases.

orig_model_method = """    function getCampaignAttemptsData($campaign_ids)
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
    }"""

repl_model_method = """    function getCampaignAttemptsData($campaign_ids)
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
    calls.id            AS id_call,
    calls.phone         AS telefono,
    cpl.datetime_entry  AS fecha_hora,
    cpl.retry           AS intento,
    cpl.new_status      AS estado,
    a.number            AS agente,
    cpl.trunk           AS trunk,
    IF(cpl.new_status = 'Success', calls.duration, cpl.duration) AS duracion
FROM call_progress_log cpl
INNER JOIN (
    SELECT MAX(cpl2.id) AS max_id
    FROM call_progress_log cpl2
    INNER JOIN calls c2 ON cpl2.id_call_outgoing = c2.id
    WHERE cpl2.new_status IN ('Success', 'Failure', 'NoAnswer', 'Abandoned', 'ShortCall')
      AND c2.id_campaign IN ($placeholders)
    GROUP BY cpl2.id_call_outgoing, cpl2.retry
) sub ON cpl.id = sub.max_id
INNER JOIN calls ON cpl.id_call_outgoing = calls.id
INNER JOIN campaign camp ON calls.id_campaign = camp.id
LEFT JOIN agent a ON cpl.id_agent = a.id
ORDER BY camp.name, cpl.datetime_entry ASC
SQL_ATTEMPTS;

        $datosAttempts = $this->_DB->fetchTable($sqlAttempts, TRUE, $campaign_ids);
        if (!is_array($datosAttempts)) {
            $this->errMsg = 'Unable to read campaign attempts data - '.$this->_DB->errMsg;
            return NULL;
        }

        $sqlAttributes = <<<SQL_ATTRIBUTES
SELECT
    ca.id_call          AS id_call,
    ca.columna          AS label,
    ca.value            AS value
FROM call_attribute ca
INNER JOIN calls c ON ca.id_call = c.id
WHERE c.id_campaign IN ($placeholders)
ORDER BY ca.id_call, ca.column_number
SQL_ATTRIBUTES;

        $datosAttributes = $this->_DB->fetchTable($sqlAttributes, TRUE, $campaign_ids);
        if (!is_array($datosAttributes)) {
            $this->errMsg = 'Unable to read campaign attributes data - '.$this->_DB->errMsg;
            return NULL;
        }

        return array(
            'ATTEMPTS'   => $datosAttempts,
            'ATTRIBUTES' => $datosAttributes
        );
    }"""

if orig_model_method in model_content:
    model_content = model_content.replace(orig_model_method, repl_model_method)
    with open(model_file, "w", encoding="utf-8") as f:
        f.write(model_content)
    print("Updated getCampaignAttemptsData in model successfully.")
else:
    # If not found, check if it's already updated
    if "SQL_ATTRIBUTES" in model_content:
        print("Model already contains the updated getCampaignAttemptsData method.")
    else:
        print("Error: Could not find getCampaignAttemptsData method in model.", file=sys.stderr)
        sys.exit(1)


# 2. Modify Controller (index.php)
print(f"Modifying Controller: {controller_file}")
if not os.path.exists(controller_file):
    print(f"Error: {controller_file} not found.", file=sys.stderr)
    sys.exit(1)

with open(controller_file, "r", encoding="utf-8") as f:
    controller_content = f.read()

# We need to find displayCampaignAttemptsCSV and update it to process attributes
orig_display_fn = """function displayCampaignAttemptsCSV($pDB, $smarty, $module_name, $local_templates_dir)
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
}"""

repl_display_fn = """function displayCampaignAttemptsCSV($pDB, $smarty, $module_name, $local_templates_dir)
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
    $result = $oCampaign->getCampaignAttemptsData($campaign_ids);

    header("Cache-Control: private");
    header("Pragma: cache");
    header('Content-Type: text/csv; charset=UTF-8; header=present');
    header("Content-disposition: attachment; filename=\\"campaign_attempts_report.csv\\"");

    $sDatosCSV = '';
    if (is_null($result) || count($result['ATTEMPTS']) <= 0) {
        $sDatosCSV = "No Data Found\\r\\n";
    } else {
        // Map attributes
        $callAttributes = array();
        $allLabels = array();
        if (isset($result['ATTRIBUTES']) && is_array($result['ATTRIBUTES'])) {
            foreach ($result['ATTRIBUTES'] as $attr) {
                $callAttributes[$attr['id_call']][$attr['label']] = $attr['value'];
                if (!in_array($attr['label'], $allLabels)) {
                    $allLabels[] = $attr['label'];
                }
            }
        }

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
        $headers = array_merge($headers, $allLabels);
        $sDatosCSV .= join(',', array_map('csv_replace', $headers))."\\r\\n";

        foreach ($result['ATTEMPTS'] as $row) {
            $id_call = $row['id_call'];
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

            // Add attributes
            foreach ($allLabels as $label) {
                $val = isset($callAttributes[$id_call][$label]) ? $callAttributes[$id_call][$label] : '';
                $linea[] = $val;
            }

            $sDatosCSV .= join(',', array_map('csv_replace', $linea))."\\r\\n";
        }
    }

    return $sDatosCSV;
}"""

if orig_display_fn in controller_content:
    controller_content = controller_content.replace(orig_display_fn, repl_display_fn)
    with open(controller_file, "w", encoding="utf-8") as f:
        f.write(controller_content)
    print("Updated displayCampaignAttemptsCSV in controller successfully.")
else:
    if "result['ATTRIBUTES']" in controller_content:
        print("Controller already contains the updated displayCampaignAttemptsCSV function.")
    else:
        print("Error: Could not find displayCampaignAttemptsCSV function in controller.", file=sys.stderr)
        sys.exit(1)

print("All modifications completed successfully!")
