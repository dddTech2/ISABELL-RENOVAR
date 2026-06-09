import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    campaign_class_php = os.path.join(workspace_dir, "modules", "campaign_out", "libs", "paloSantoCampaignCC.class.php")
    campaign_index_php = os.path.join(workspace_dir, "modules", "campaign_out", "index.php")

    print("=== Campaign Out List Modification ===")

    # 1. Modify campaign order in paloSantoCampaignCC.class.php
    if os.path.exists(campaign_class_php):
        with open(campaign_class_php, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_str = "$sPeticionSQL .= ' ORDER BY c.datetime_init, c.daytime_init';"
        replacement_str = "$sPeticionSQL .= ' ORDER BY c.id DESC';"

        if target_str in content:
            content = content.replace(target_str, replacement_str)
            with open(campaign_class_php, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully updated campaign sorting to ORDER BY c.id DESC.")
        else:
            if replacement_str in content:
                print("Campaign sorting is already set to ORDER BY c.id DESC.")
            else:
                print("Warning: Target string for sorting not found in paloSantoCampaignCC.class.php")
    else:
        print(f"Error: {campaign_class_php} does not exist.")
        return 1

    # 2. Modify campaign columns and data to show ID in index.php
    if os.path.exists(campaign_index_php):
        with open(campaign_index_php, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update setColumns
        columns_target = """    $oGrid->setColumns(array('', _tr('Name Campaign'), _tr('Range Date'),
        _tr('Schedule per Day'), _tr('Retries'), _tr('Trunk'), _tr('Queue'),
        _tr('Total Calls'), _tr('Pending Calls'), _tr('Completed Calls'), _tr('Average Time'), _tr('Status'), _tr('Options')));"""

        columns_replacement = """    $oGrid->setColumns(array('', 'ID', _tr('Name Campaign'), _tr('Range Date'),
        _tr('Schedule per Day'), _tr('Retries'), _tr('Trunk'), _tr('Queue'),
        _tr('Total Calls'), _tr('Pending Calls'), _tr('Completed Calls'), _tr('Average Time'), _tr('Status'), _tr('Options')));"""

        if columns_target in content:
            content = content.replace(columns_target, columns_replacement)
            print("Successfully updated Grid columns with 'ID'.")
        else:
            if columns_replacement in content:
                print("Grid columns already include 'ID'.")
            else:
                print("Warning: Grid columns target string not found in index.php")

        # Update arrData row mapping
        # Let's match the exact snippet including newlines and indents.
        data_target = '            $arrData[] = array(\n                "<input class=\\"button\\" type=\\"radio\\" name=\\"id_campaign\\" value=\\"$campaign[id]\\" />",\n                "<a href=\'?menu=$module_name&amp;action=edit_campaign&amp;id_campaign=".$campaign[\'id\']."\'>".'
        
        data_replacement = '            $arrData[] = array(\n                "<input class=\\"button\\" type=\\"radio\\" name=\\"id_campaign\\" value=\\"$campaign[id]\\" />",\n                $campaign[\'id\'],\n                "<a href=\'?menu=$module_name&amp;action=edit_campaign&amp;id_campaign=".$campaign[\'id\']."\'>".'

        if data_target in content:
            content = content.replace(data_target, data_replacement)
            print("Successfully added Campaign ID value to rows data.")
        else:
            if data_replacement in content:
                print("Campaign ID value is already added to rows data.")
            else:
                print("Warning: arrData row mapping target string not found in index.php")

        with open(campaign_index_php, 'w', encoding='utf-8') as f:
            f.write(content)

    else:
        print(f"Error: {campaign_index_php} does not exist.")
        return 1

    print("Campaign list updates applied successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
