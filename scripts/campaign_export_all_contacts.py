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

# Replace 1: Add retries to SQL SELECT list in sqlLlamadas
orig1 = """SELECT
    c.id                AS id,
    c.phone             AS telefono,
    c.status            AS estado,
    a.number            AS number,
    c.start_time        AS fecha_hora,
    c.duration          AS duracion,
    c.uniqueid          AS uniqueid,
    c.failure_cause     AS failure_cause,
    c.failure_cause_txt AS failure_cause_txt
FROM calls c"""

repl1 = """SELECT
    c.id                AS id,
    c.phone             AS telefono,
    c.status            AS estado,
    a.number            AS number,
    c.start_time        AS fecha_hora,
    c.duration          AS duracion,
    c.uniqueid          AS uniqueid,
    c.failure_cause     AS failure_cause,
    c.failure_cause_txt AS failure_cause_txt,
    c.retries           AS intentos
FROM calls c"""

# Replace 2: Add Retries label translation
orig2 = """                'LABEL' =>  array(
                    'id_call',
                    _tr('Phone Customer'),
                    _tr('Status Call'),
                    "Agente",
                    _tr('Date & Time'),
                    _tr('Duration'),
                    'Uniqueid',
                    _tr('Failure Code'),
                    _tr('Failure Cause'),
                ),"""

repl2 = """                'LABEL' =>  array(
                    'id_call',
                    _tr('Phone Customer'),
                    _tr('Status Call'),
                    "Agente",
                    _tr('Date & Time'),
                    _tr('Duration'),
                    'Uniqueid',
                    _tr('Failure Code'),
                    _tr('Failure Cause'),
                    _tr('Retries'),
                ),"""

# Verification of presence
all_ok = True
for label, orig in [("sqlLlamadas_retries", orig1), ("labels_retries", orig2)]:
    if orig not in content:
        print(f"Error: Could not find exact text match for {label} in {target_file}", file=sys.stderr)
        all_ok = False

if not all_ok:
    sys.exit(1)

# Apply replacements
content = content.replace(orig1, repl1)
content = content.replace(orig2, repl2)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated paloSantoCampaignCC.class.php to export retries count for campaign contacts.")
