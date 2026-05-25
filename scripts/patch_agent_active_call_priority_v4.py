import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    index_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "index.php")

    print(f"Modifying Campaign Monitoring index file: {index_file}")

    if not os.path.exists(index_file):
        print(f"Error: Index file not found at {index_file}")
        return 1

    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content_norm = content.replace('\r\n', '\n')

    old_oncall_format = (
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        if (isset($agent['original_status'])) {\n"
        "            if ($agent['original_status'] == 'paused') {\n"
        "                $sEtiquetaPause = _tr('paused');\n"
        "                if (!is_null($agent['pauseinfo'])) {\n"
        "                    $sEtiquetaPause .= ': '.$agent['pauseinfo']['pausename'];\n"
        "                }\n"
        "                $sEtiquetaStatus = _tr('oncall') . ' (' . $sEtiquetaPause . ')';\n"
        "            } elseif ($agent['original_status'] == 'offline') {\n"
        "                $sEtiquetaStatus = _tr('oncall') . ' (' . _tr('No logon') . ')';\n"
        "            }\n"
        "        }\n"
        "        break;"
    )

    new_oncall_format = (
        "    case 'oncall':\n"
        "        $sDesde = $agent['callinfo']['linkstart'];\n"
        "        break;"
    )

    if old_oncall_format not in content_norm:
        print("Error: Old oncall formatting logic not found in index.php")
        return 1

    content_norm = content_norm.replace(old_oncall_format, new_oncall_format)

    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content_norm)

    print("Success: Updated modules/campaign_monitoring/index.php")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
