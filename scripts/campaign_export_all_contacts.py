import os
import sys

# Compute path to target file relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
target_file = os.path.join(project_dir, "modules", "campaign_out", "libs", "paloSantoCampaignCC.class.php")

print(f"Target file path: {target_file}")

if not os.path.exists(target_file):
    print(f"Error: File {target_file} not found.", file=sys.stderr)
    sys.exit(1)

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace 1: sqlLlamadas status filter
orig1 = """WHERE
    c.id_campaign = ? AND
    (c.status='Success' OR c.status='Failure' OR c.status='ShortCall' OR c.status='NoAnswer' OR c.status='Abandoned')
ORDER BY"""

repl1 = """WHERE
    c.id_campaign = ?
ORDER BY"""

# Replace 2: sqlAtributos status filter
orig2 = """WHERE calls.id_campaign = ? AND calls.id = ? AND calls.id = call_attribute.id_call AND
    (calls.status='Success' OR calls.status='Failure' OR calls.status='ShortCall' OR calls.status='NoAnswer' OR calls.status='Abandoned')
ORDER BY calls.id, call_attribute.column_number"""

repl2 = """WHERE calls.id_campaign = ? AND calls.id = ? AND calls.id = call_attribute.id_call
ORDER BY calls.id, call_attribute.column_number"""

# Replace 3: sqlDatosForm status filter
orig3 = """WHERE fdr.id_calls = c.id AND fdr.id_form_field = ff.id AND c.id_campaign = ?
    AND ff.tipo <> 'LABEL'
    AND (c.status='Success' OR c.status='Failure' OR c.status='ShortCall' OR c.status='NoAnswer' OR c.status='Abandoned')
ORDER BY id_call, id_form, id_form_field"""

repl3 = """WHERE fdr.id_calls = c.id AND fdr.id_form_field = ff.id AND c.id_campaign = ?
    AND ff.tipo <> 'LABEL'
ORDER BY id_call, id_form, id_form_field"""

# Verification of presence
all_ok = True
for label, orig in [("sqlLlamadas", orig1), ("sqlAtributos", orig2), ("sqlDatosForm", orig3)]:
    if orig not in content:
        print(f"Error: Could not find exact text match for {label} in {target_file}", file=sys.stderr)
        all_ok = False

if not all_ok:
    sys.exit(1)

# Apply replacements
content = content.replace(orig1, repl1)
content = content.replace(orig2, repl2)
content = content.replace(orig3, repl3)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated paloSantoCampaignCC.class.php to export all campaign contacts.")
