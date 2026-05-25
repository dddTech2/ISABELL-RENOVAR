import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    php_lib = os.path.join(workspace_dir, "modules", "agent_journey", "libs", "paloSantoAgentJourney.class.php")
    index_file = os.path.join(workspace_dir, "modules", "agent_journey", "index.php")
    es_lang = os.path.join(workspace_dir, "modules", "agent_journey", "lang", "es.lang")
    en_lang = os.path.join(workspace_dir, "modules", "agent_journey", "lang", "en.lang")

    print(f"Modifying PHP library file: {php_lib}")
    print(f"Modifying index controller: {index_file}")
    print(f"Modifying Spanish lang file: {es_lang}")
    print(f"Modifying English lang file: {en_lang}")

    # 1. Modify modules/agent_journey/libs/paloSantoAgentJourney.class.php
    if not os.path.exists(php_lib):
        print(f"Error: PHP library file not found at {php_lib}")
        return 1

    with open(php_lib, 'r', encoding='utf-8') as f:
        php_lib_content = f.read()

    php_lib_norm = php_lib_content.replace('\r\n', '\n')

    old_sql_block = (
        "        // Outgoing call events\n"
        "        $sqlOutgoing = \"\n"
        "            SELECT agent.id, agent.number, agent.name,\n"
        "                calls.start_time AS event_time,\n"
        "                'OUTGOING_CALL' AS event_type,\n"
        "                CONCAT(calls.phone, ' (', IFNULL(calls.status, 'Unknown'), ')') AS event_detail,\n"
        "                calls.duration AS duration\n"
        "            FROM calls\n"
        "            JOIN agent ON calls.id_agent = agent.id\n"
        "            WHERE calls.id_agent IS NOT NULL\n"
        "                AND calls.start_time BETWEEN ? AND ?\n"
        "                $agentFilter\";\n"
        "\n"
        "        // Combine all queries with UNION\n"
        "        $sqlFull = \"($sqlLogin) UNION ALL ($sqlLogout) UNION ALL ($sqlBreak) UNION ALL ($sqlIncoming) UNION ALL ($sqlOutgoing) ORDER BY event_time ASC\";\n"
        "\n"
        "        // Build parameters array (each query needs date range + optional agent)\n"
        "        for ($i = 0; $i < 5; $i++) {"
    )

    new_sql_block = (
        "        // Outgoing call events\n"
        "        $sqlOutgoing = \"\n"
        "            SELECT agent.id, agent.number, agent.name,\n"
        "                calls.start_time AS event_time,\n"
        "                'OUTGOING_CALL' AS event_type,\n"
        "                CONCAT(calls.phone, ' (', IFNULL(calls.status, 'Unknown'), ')') AS event_detail,\n"
        "                calls.duration AS duration\n"
        "            FROM calls\n"
        "            JOIN agent ON calls.id_agent = agent.id\n"
        "            WHERE calls.id_agent IS NOT NULL\n"
        "                AND calls.start_time BETWEEN ? AND ?\n"
        "                $agentFilter\";\n"
        "\n"
        "        // Manual outgoing call events from Asterisk CDR\n"
        "        $sqlManualOutgoing = \"\n"
        "            SELECT agent.id, agent.number, agent.name,\n"
        "                cdr.calldate AS event_time,\n"
        "                'MANUAL_OUTGOING' AS event_type,\n"
        "                CONCAT(cdr.dst, ' (', cdr.disposition, ')') AS event_detail,\n"
        "                cdr.billsec AS duration\n"
        "            FROM asteriskcdrdb.cdr cdr\n"
        "            JOIN agent ON cdr.src = agent.number\n"
        "            WHERE cdr.calldate BETWEEN ? AND ?\n"
        "                AND cdr.uniqueid NOT IN (SELECT uniqueid FROM calls WHERE uniqueid IS NOT NULL)\n"
        "                AND cdr.uniqueid NOT IN (SELECT uniqueid FROM call_entry WHERE uniqueid IS NOT NULL)\n"
        "                AND cdr.dcontext != 'from-queue'\n"
        "                $agentFilter\";\n"
        "\n"
        "        // Manual incoming call events from Asterisk CDR\n"
        "        $sqlManualIncoming = \"\n"
        "            SELECT agent.id, agent.number, agent.name,\n"
        "                cdr.calldate AS event_time,\n"
        "                'MANUAL_INCOMING' AS event_type,\n"
        "                CONCAT(cdr.src, ' (', cdr.disposition, ')') AS event_detail,\n"
        "                cdr.billsec AS duration\n"
        "            FROM asteriskcdrdb.cdr cdr\n"
        "            JOIN agent ON cdr.dst = agent.number\n"
        "            WHERE cdr.calldate BETWEEN ? AND ?\n"
        "                AND cdr.uniqueid NOT IN (SELECT uniqueid FROM calls WHERE uniqueid IS NOT NULL)\n"
        "                AND cdr.uniqueid NOT IN (SELECT uniqueid FROM call_entry WHERE uniqueid IS NOT NULL)\n"
        "                AND cdr.dcontext != 'from-queue'\n"
        "                $agentFilter\";\n"
        "\n"
        "        // Combine all queries with UNION\n"
        "        $sqlFull = \"($sqlLogin) UNION ALL ($sqlLogout) UNION ALL ($sqlBreak) UNION ALL ($sqlIncoming) UNION ALL ($sqlOutgoing) UNION ALL ($sqlManualOutgoing) UNION ALL ($sqlManualIncoming) ORDER BY event_time ASC\";\n"
        "\n"
        "        // Build parameters array (each query needs date range + optional agent)\n"
        "        for ($i = 0; $i < 7; $i++) {"
    )

    if old_sql_block in php_lib_norm:
        php_lib_norm = php_lib_norm.replace(old_sql_block, new_sql_block)
        print("Success: Updated SQL queries and union structure in paloSantoAgentJourney.class.php")
    else:
        if "MANUAL_OUTGOING" in php_lib_norm:
            print("Notice: paloSantoAgentJourney.class.php already updated")
        else:
            print("Error: Target SQL block not found in paloSantoAgentJourney.class.php")
            return 1

    if '\r\n' in php_lib_content:
        php_lib_norm = php_lib_norm.replace('\n', '\r\n')

    with open(php_lib, 'w', encoding='utf-8') as f:
        f.write(php_lib_norm)

    # 2. Modify modules/agent_journey/index.php
    if not os.path.exists(index_file):
        print(f"Error: index.php not found at {index_file}")
        return 1

    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()

    index_norm = index_content.replace('\r\n', '\n')

    old_event_types = (
        "    $eventTypes = array(\n"
        "        'LOGIN' => _tr('Login'),\n"
        "        'LOGOUT' => _tr('Logout'),\n"
        "        'BREAK' => _tr('Break'),\n"
        "        'INCOMING_CALL' => _tr('Incoming Call'),\n"
        "        'OUTGOING_CALL' => _tr('Outgoing Call'),\n"
        "    );"
    )

    new_event_types = (
        "    $eventTypes = array(\n"
        "        'LOGIN' => _tr('Login'),\n"
        "        'LOGOUT' => _tr('Logout'),\n"
        "        'BREAK' => _tr('Break'),\n"
        "        'INCOMING_CALL' => _tr('Incoming Call'),\n"
        "        'OUTGOING_CALL' => _tr('Outgoing Call'),\n"
        "        'MANUAL_INCOMING' => _tr('Manual Incoming'),\n"
        "        'MANUAL_OUTGOING' => _tr('Manual Outgoing'),\n"
        "    );"
    )

    if old_event_types in index_norm:
        index_norm = index_norm.replace(old_event_types, new_event_types)
        print("Success: Updated eventType translations in index.php")
    else:
        if "MANUAL_OUTGOING" in index_norm:
            print("Notice: index.php already updated")
        else:
            print("Error: Target eventTypes block not found in index.php")
            return 1

    if '\r\n' in index_content:
        index_norm = index_norm.replace('\n', '\r\n')

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_norm)

    # 3. Modify modules/agent_journey/lang/es.lang
    if not os.path.exists(es_lang):
        print(f"Error: Spanish language file not found at {es_lang}")
        return 1

    with open(es_lang, 'r', encoding='utf-8') as f:
        es_content = f.read()

    es_norm = es_content.replace('\r\n', '\n')

    old_es_trans = (
        "\"Incoming Call\"                     => \"Llamada Entrante\",\n"
        "\"Outgoing Call\"                     => \"Llamada Saliente\","
    )

    new_es_trans = (
        "\"Incoming Call\"                     => \"Llamada Entrante\",\n"
        "\"Outgoing Call\"                     => \"Llamada Saliente\",\n"
        "\"Manual Incoming\"                   => \"Llamada Entrante Manual\",\n"
        "\"Manual Outgoing\"                   => \"Llamada Saliente Manual\","
    )

    if old_es_trans in es_norm:
        es_norm = es_norm.replace(old_es_trans, new_es_trans)
        print("Success: Added translations to es.lang")
    else:
        if "Llamada Entrante Manual" in es_norm:
            print("Notice: es.lang already updated")
        else:
            print("Error: Target translations not found in es.lang")
            return 1

    if '\r\n' in es_content:
        es_norm = es_norm.replace('\n', '\r\n')

    with open(es_lang, 'w', encoding='utf-8') as f:
        f.write(es_norm)

    # 4. Modify modules/agent_journey/lang/en.lang
    if not os.path.exists(en_lang):
        print(f"Error: English language file not found at {en_lang}")
        return 1

    with open(en_lang, 'r', encoding='utf-8') as f:
        en_content = f.read()

    en_norm = en_content.replace('\r\n', '\n')

    old_en_trans = (
        "\"Incoming Call\"                     => \"Incoming Call\",\n"
        "\"Outgoing Call\"                     => \"Outgoing Call\","
    )

    new_en_trans = (
        "\"Incoming Call\"                     => \"Incoming Call\",\n"
        "\"Outgoing Call\"                     => \"Outgoing Call\",\n"
        "\"Manual Incoming\"                   => \"Manual Incoming Call\",\n"
        "\"Manual Outgoing\"                   => \"Manual Outgoing Call\","
    )

    if old_en_trans in en_norm:
        en_norm = en_norm.replace(old_en_trans, new_en_trans)
        print("Success: Added translations to en.lang")
    else:
        if "Manual Incoming Call" in en_norm:
            print("Notice: en.lang already updated")
        else:
            print("Error: Target translations not found in en.lang")
            return 1

    if '\r\n' in en_content:
        en_norm = en_norm.replace('\n', '\r\n')

    with open(en_lang, 'w', encoding='utf-8') as f:
        f.write(en_norm)

    print("All agent journey modifications completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
