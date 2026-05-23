import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    js_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "js", "javascript.js")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")
    css_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "css", "styles.css")

    print(f"Modifying JS file: {js_file}")
    print(f"Modifying template file: {tpl_file}")
    print(f"Modifying CSS file: {css_file}")

    # 1. Modify JS file
    if not os.path.exists(js_file):
        print(f"Error: JS file not found at {js_file}")
        return 1

    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    js_content_norm = js_content.replace('\r\n', '\n')

    # Add App.CampaignSelect view
    router_map_target = (
        "\tApp.Router.map(function() {\n"
        "\t\tthis.resource('campaign', { path: '/' }, function () {\n"
        "\t\t\tthis.route('details', { path: '/details/:type/:id_campaign' });\n"
        "\t\t});\n"
        "\t});"
    )
    router_map_replace = (
        "\tApp.Router.map(function() {\n"
        "\t\tthis.resource('campaign', { path: '/' }, function () {\n"
        "\t\t\tthis.route('details', { path: '/details/:type/:id_campaign' });\n"
        "\t\t});\n"
        "\t});\n\n"
        "\tApp.CampaignSelect = Ember.Select.extend({\n"
        "\t\toptionView: Ember.SelectOption.extend({\n"
        "\t\t\tclassNameBindings: ['statusClass'],\n"
        "\t\t\tstatusClass: function() {\n"
        "\t\t\t\tvar content = this.get('content');\n"
        "\t\t\t\tif (content) {\n"
        "\t\t\t\t\tvar status = content.get('status');\n"
        "\t\t\t\t\tif (status === 'A' || status === 'active' || status === 'activequeue') {\n"
        "\t\t\t\t\t\treturn 'campaign-status-active';\n"
        "\t\t\t\t\t} else if (status === 'I' || status === 'inactive') {\n"
        "\t\t\t\t\t\treturn 'campaign-status-inactive';\n"
        "\t\t\t\t\t} else if (status === 'T' || status === 'finished' || status === 'terminada') {\n"
        "\t\t\t\t\t\treturn 'campaign-status-finished';\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\t}\n"
        "\t\t\t\treturn '';\n"
        "\t\t\t}.property('content.status')\n"
        "\t\t})\n"
        "\t});"
    )

    if router_map_target not in js_content_norm:
        print("Error: App.Router.map target not found in javascript.js")
        return 1

    js_content_norm = js_content_norm.replace(router_map_target, router_map_replace)

    # Add label_with_status inside CampaignSummary
    summary_target = (
        "\tApp.CampaignSummary = Ember.Object.extend({\n"
        "\t\tid_campaign:\tnull,\n"
        "\t\tdesc_campaign:\tnull,\n"
        "\t\ttype:\t\t\tnull,\n"
        "\t\tstatus:\t\t\tnull,\n"
        "\t\tkey_campaign:\tfunction() {\n"
        "\t\t\treturn this.get('type') + '-' + this.get('id_campaign');\n"
        "\t\t}.property('type', 'id_campaign')\n"
        "\t});"
    )
    summary_replace = (
        "\tApp.CampaignSummary = Ember.Object.extend({\n"
        "\t\tid_campaign:\tnull,\n"
        "\t\tdesc_campaign:\tnull,\n"
        "\t\ttype:\t\t\tnull,\n"
        "\t\tstatus:\t\t\tnull,\n"
        "\t\tkey_campaign:\tfunction() {\n"
        "\t\t\treturn this.get('type') + '-' + this.get('id_campaign');\n"
        "\t\t}.property('type', 'id_campaign'),\n"
        "\t\tlabel_with_status: function() {\n"
        "\t\t\tvar desc = this.get('desc_campaign');\n"
        "\t\t\tvar status = this.get('status');\n"
        "\t\t\tvar prefix = '';\n"
        "\t\t\tif (status === 'A' || status === 'active' || status === 'activequeue') {\n"
        "\t\t\t\tprefix = '🟢 ';\n"
        "\t\t\t} else if (status === 'I' || status === 'inactive') {\n"
        "\t\t\t\tprefix = '🟡 ';\n"
        "\t\t\t} else if (status === 'T' || status === 'finished' || status === 'terminada') {\n"
        "\t\t\t\tprefix = '🔴 ';\n"
        "\t\t\t} else {\n"
        "\t\t\t\tprefix = '⚪ ';\n"
        "\t\t\t}\n"
        "\t\t\treturn prefix + desc;\n"
        "\t\t}.property('desc_campaign', 'status')\n"
        "\t});"
    )

    if summary_target not in js_content_norm:
        print("Error: CampaignSummary target not found in javascript.js")
        return 1

    js_content_norm = js_content_norm.replace(summary_target, summary_replace)

    if '\r\n' in js_content:
        js_content_norm = js_content_norm.replace('\n', '\r\n')

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content_norm)
    print("Success: Updated javascript.js")

    # 2. Modify template file
    if not os.path.exists(tpl_file):
        print(f"Error: Template file not found at {tpl_file}")
        return 1

    with open(tpl_file, 'r', encoding='utf-8') as f:
        tpl_content = f.read()

    tpl_content_norm = tpl_content.replace('\r\n', '\n')

    tpl_target = (
        "{{view Ember.Select\n"
        "            contentBinding=\"content\"\n"
        "            optionValuePath=\"content.key_campaign\"\n"
        "            optionLabelPath=\"content.desc_campaign\"\n"
        "            valueBinding=\"key_campaign\" }}"
    )
    tpl_replace = (
        "{{view App.CampaignSelect\n"
        "            contentBinding=\"content\"\n"
        "            optionValuePath=\"content.key_campaign\"\n"
        "            optionLabelPath=\"content.label_with_status\"\n"
        "            valueBinding=\"key_campaign\" }}"
    )

    if tpl_target not in tpl_content_norm:
        print("Error: Campaign select view target not found in informacion_campania.tpl")
        return 1

    tpl_content_norm = tpl_content_norm.replace(tpl_target, tpl_replace)

    if '\r\n' in tpl_content:
        tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

    with open(tpl_file, 'w', encoding='utf-8') as f:
        f.write(tpl_content_norm)
    print("Success: Updated informacion_campania.tpl")

    # 3. Modify CSS file
    if not os.path.exists(css_file):
        print(f"Error: CSS file not found at {css_file}")
        return 1

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    css_content_norm = css_content.replace('\r\n', '\n')

    css_rules = (
        "\n"
        "/* Styles for campaign dropdown options based on status */\n"
        "select option.campaign-status-active {\n"
        "  background-color: #d4edda;\n"
        "  color: #155724;\n"
        "  font-weight: bold;\n"
        "}\n"
        "\n"
        "select option.campaign-status-inactive {\n"
        "  background-color: #fff3cd;\n"
        "  color: #856404;\n"
        "}\n"
        "\n"
        "select option.campaign-status-finished {\n"
        "  background-color: #f8d7da;\n"
        "  color: #721c24;\n"
        "}\n"
    )

    if "select option.campaign-status-active" not in css_content_norm:
        css_content_norm += css_rules

    if '\r\n' in css_content:
        css_content_norm = css_content_norm.replace('\n', '\r\n')

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content_norm)
    print("Success: Updated styles.css")

    print("All visual updates for campaign status applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
