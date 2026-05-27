import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    css_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "css", "styles.css")
    tpl_file = os.path.join(workspace_dir, "modules", "campaign_monitoring", "themes", "default", "informacion_campania.tpl")

    print("Starting visual improvements (V2)...")

    # 1. Update CSS with clean, full-width cards, light headers, and enabled scrollbars
    if os.path.exists(css_file):
        print(f"Modifying CSS: {css_file}")
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        css_content_norm = css_content.replace('\r\n', '\n')

        # Since styles.css is restored to original clean state, we just prepend the V2 block
        new_v2_block = (
            "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');\n\n"
            "#campaignMonitoringApplication {\n"
            "    font-family: 'Inter', sans-serif !important;\n"
            "    background-color: #f8fafc !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 12px !important;\n"
            "    padding: 24px !important;\n"
            "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;\n"
            "}\n\n"
            "#campaignMonitoringApplication table {\n"
            "    font-family: 'Inter', sans-serif !important;\n"
            "}\n\n"
            ".flex-container {\n"
            "    display: flex !important;\n"
            "    justify-content: space-between !important;\n"
            "    width: 100% !important; /* Full width layout instead of 50% */\n"
            "    gap: 24px !important;\n"
            "    margin-bottom: 24px !important;\n"
            "}\n\n"
            ".campaign-table {\n"
            "    flex: 1 !important; /* Share row space equally */\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 8px !important;\n"
            "    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;\n"
            "    border-collapse: separate !important;\n"
            "    border-spacing: 0 !important;\n"
            "    overflow: hidden !important;\n"
            "    margin-bottom: 0 !important;\n"
            "}\n\n"
            ".campaign-table-outgoing {\n"
            "    width: 100% !important;\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-radius: 8px !important;\n"
            "    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;\n"
            "    border-collapse: separate !important;\n"
            "    border-spacing: 0 !important;\n"
            "    overflow: hidden !important;\n"
            "    margin-bottom: 24px !important;\n"
            "}\n\n"
            ".table-header {\n"
            "    background-color: #f8fafc !important; /* Light clean header */\n"
            "    color: #0f172a !important; /* Charcoal dark text */\n"
            "    font-size: 12px !important;\n"
            "    font-weight: 700 !important;\n"
            "    padding: 14px 16px !important;\n"
            "    text-transform: uppercase !important;\n"
            "    letter-spacing: 0.05em !important;\n"
            "    border: none !important;\n"
            "    border-bottom: 1px solid #e2e8f0 !important;\n"
            "}\n\n"
            ".table-label, .table-label-out {\n"
            "    color: #475569 !important;\n"
            "    font-weight: 600 !important;\n"
            "    font-size: 13px !important;\n"
            "}\n\n"
            ".campaign-table td, .campaign-table-outgoing td {\n"
            "    padding: 12px 16px !important;\n"
            "    border-bottom: 1px solid #f1f5f9 !important;\n"
            "    border-top: none !important;\n"
            "    border-left: none !important;\n"
            "    border-right: none !important;\n"
            "    font-size: 13px !important;\n"
            "    color: #0f172a !important;\n"
            "}\n\n"
            "table.titulo {\n"
            "    background-color: #f8fafc !important; /* Light header for bottom tables */\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-bottom: none !important;\n"
            "    border-top-left-radius: 8px !important;\n"
            "    border-top-right-radius: 8px !important;\n"
            "    overflow: hidden !important;\n"
            "    height: auto !important;\n"
            "}\n\n"
            "table.titulo td {\n"
            "    padding: 12px 16px !important;\n"
            "    font-weight: 700 !important;\n"
            "    font-size: 11px !important;\n"
            "    text-transform: uppercase !important;\n"
            "    letter-spacing: 0.05em !important;\n"
            "    color: #0f172a !important; /* Charcoal dark text */\n"
            "    border-bottom: 1px solid #e2e8f0 !important;\n"
            "}\n\n"
            "div.llamadas {\n"
            "    background-color: #ffffff !important;\n"
            "    border: 1px solid #e2e8f0 !important;\n"
            "    border-bottom-left-radius: 8px !important;\n"
            "    border-bottom-right-radius: 8px !important;\n"
            "    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;\n"
            "    overflow-y: auto !important; /* Habilitar scrollbar vertical para ver todos los gestores */\n"
            "    overflow-x: hidden !important;\n"
            "}\n\n"
            "div.llamadas table > tbody > tr > td {\n"
            "    padding: 12px 16px !important;\n"
            "    border-bottom: 1px solid #f1f5f9 !important;\n"
            "    font-size: 13px !important;\n"
            "    color: #1e293b !important;\n"
            "}\n\n"
            "div.llamadas table > tbody > tr:hover {\n"
            "    background-color: #f8fafc !important;\n"
            "}\n\n"
            ".dialing-call-row {\n"
            "    background-color: #e8f0fe !important; /* Soft premium pastel blue */\n"
            "}\n\n"
        )

        css_content_norm = new_v2_block + css_content_norm

        if '\r\n' in css_content:
            css_content_norm = css_content_norm.replace('\n', '\r\n')

        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content_norm)
        print("CSS successfully updated with lighter V2 styles.")
    else:
        print(f"Error: CSS file not found at {css_file}")
        return 1

    # 2. Update TPL file
    if os.path.exists(tpl_file):
        print(f"Modifying TPL: {tpl_file}")
        with open(tpl_file, 'r', encoding='utf-8') as f:
            tpl_content = f.read()

        tpl_content_norm = tpl_content.replace('\r\n', '\n')

        # First restore borders to original template format in memory if modified
        tpl_content_norm = tpl_content_norm.replace('class="campaign-table" border="1"', 'class="campaign-table"')
        tpl_content_norm = tpl_content_norm.replace('class="campaign-table-outgoing" border="1"', 'class="campaign-table-outgoing"')

        old_tr_style = '<tr style="background-color:#00e7ffa6" {{bindAttr class="reciente"}}>'
        new_tr_style = '<tr class="dialing-call-row" {{bindAttr class="reciente"}}>'

        if old_tr_style in tpl_content_norm:
            tpl_content_norm = tpl_content_norm.replace(old_tr_style, new_tr_style)
            print("TPL successfully replaced cyan inline color with class.")
        else:
            print("Warning: Inline style for dialing rows not found or already replaced in TPL.")

        if '\r\n' in tpl_content:
            tpl_content_norm = tpl_content_norm.replace('\n', '\r\n')

        with open(tpl_file, 'w', encoding='utf-8') as f:
            f.write(tpl_content_norm)
        print("TPL successfully updated.")
    else:
        print(f"Error: TPL file not found at {tpl_file}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
