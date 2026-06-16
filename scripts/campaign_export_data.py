import os
import sys

# Compute path to target files relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

controller_file = os.path.join(project_dir, "modules", "campaign_out", "index.php")
es_lang_file = os.path.join(project_dir, "modules", "campaign_out", "lang", "es.lang")
en_lang_file = os.path.join(project_dir, "modules", "campaign_out", "lang", "en.lang")

# 1. Modify index.php
print(f"Modifying Controller: {controller_file}")
if not os.path.exists(controller_file):
    print(f"Error: {controller_file} not found.", file=sys.stderr)
    sys.exit(1)

with open(controller_file, "r", encoding="utf-8") as f:
    content = f.read()

# Add routing check if not present
routing_check = """    if (isset($_POST['csv_data'])) {
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
            $sAction = 'csv_data';
        }
    }"""

if "isset($_POST['csv_data'])" not in content:
    target_routing = """    if (isset($_POST['csv_attempts'])) {
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
    }"""
    if target_routing in content:
        content = content.replace(target_routing, target_routing + "\n" + routing_check)
        print("Added csv_data POST routing check.")
    else:
        print("Warning: Could not find target routing block to append csv_data check.")

# Add validation check if not present
validation_check = """    // Interceptar error si se pulsa csv_data sin seleccionar campañas
    if (isset($_POST['csv_data']) && count($campaign_ids) == 0) {
        $smarty->assign("mb_title", _tr("Validation Error"));
        $smarty->assign("mb_message", _tr("Please select at least one campaign to download data"));
    }"""

if "count($campaign_ids) == 0) {\n        $smarty->assign(\"mb_title\", _tr(\"Validation Error\"));\n        $smarty->assign(\"mb_message\", _tr(\"Please select at least one campaign to download data\"));" not in content:
    target_validation = """    // Interceptar error si se pulsa csv_attempts sin seleccionar campañas
    if (isset($_POST['csv_attempts']) && count($campaign_ids) == 0) {
        $smarty->assign("mb_title", _tr("Validation Error"));
        $smarty->assign("mb_message", _tr("Please select at least one campaign to download attempts"));
    }"""
    if target_validation in content:
        content = content.replace(target_validation, target_validation + "\n\n" + validation_check)
        print("Added csv_data empty selection validation check.")
    else:
        print("Warning: Could not find target validation block to append csv_data check.")

# Add customAction button if not present
custom_action = '    $oGrid->customAction("csv_data", _tr("Download Campaigns CSV"), "download", false);'
if 'customAction("csv_data"' not in content:
    target_action = '    $oGrid->customAction("csv_attempts", _tr("Download Attempts CSV"), "download", false);'
    if target_action in content:
        content = content.replace(target_action, target_action + "\n" + custom_action)
        print("Added csv_data custom action button to grid.")
    else:
        print("Warning: Could not find target customAction block to append csv_data button.")

# Save modified index.php
with open(controller_file, "w", encoding="utf-8") as f:
    f.write(content)

print("All campaign data CSV modifications validated successfully!")
