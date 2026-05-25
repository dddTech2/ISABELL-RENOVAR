import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    consola_file = os.path.join(workspace_dir, "modules", "agent_console", "libs", "paloSantoConsola.class.php")

    print(f"Modifying Console class file: {consola_file}")

    if not os.path.exists(consola_file):
        print(f"Error: Console class file not found at {consola_file}")
        return 1

    with open(consola_file, 'r', encoding='utf-8') as f:
        consola_content = f.read()

    consola_content_norm = consola_content.replace('\r\n', '\n')

    consola_target = (
        "                    $callNumber = $chan['exten'];\n"
        "                    if (empty($callNumber) || $callNumber == 's') {\n"
        "                        $callNumber = $chan['callerid'];\n"
        "                    }\n"
        "                    if (preg_match('/<(\\d+)>/', $callNumber, $matches)) {\n"
        "                        $callNumber = $matches[1];\n"
        "                    }"
    )

    consola_replace = (
        "                    $callNumber = $chan['exten'];\n"
        "                    $isOutbound = FALSE;\n"
        "                    $cleanCallerId = $chan['callerid'];\n"
        "                    if (preg_match('/<(\\d+)>/', $cleanCallerId, $matches)) {\n"
        "                        $cleanCallerId = $matches[1];\n"
        "                    }\n"
        "                    if ($cleanCallerId == $id) {\n"
        "                        $isOutbound = TRUE;\n"
        "                    }\n"
        "\n"
        "                    if ($isOutbound) {\n"
        "                        $dialed = null;\n"
        "                        if (preg_match('/(?:PJSIP|SIP|IAX2|Local)\\/(?:[^\\/]+\\/)?(\\d+)/i', $chan['data'], $matches)) {\n"
        "                            $dialed = $matches[1];\n"
        "                        }\n"
        "                        if (!empty($dialed)) {\n"
        "                            $callNumber = $dialed;\n"
        "                        } elseif (!empty($chan['exten']) && $chan['exten'] != 's' && $chan['exten'] != $id) {\n"
        "                            $callNumber = $chan['exten'];\n"
        "                        } else {\n"
        "                            $callNumber = $chan['callerid'];\n"
        "                        }\n"
        "                    } else {\n"
        "                        $callNumber = $chan['callerid'];\n"
        "                    }\n"
        "\n"
        "                    if (preg_match('/<(\\d+)>/', $callNumber, $matches)) {\n"
        "                        $callNumber = $matches[1];\n"
        "                    }"
    )

    if consola_target not in consola_content_norm:
        print("Error: Console target not found in paloSantoConsola.class.php")
        return 1
    consola_content_norm = consola_content_norm.replace(consola_target, consola_replace)

    if '\r\n' in consola_content:
        consola_content_norm = consola_content_norm.replace('\n', '\r\n')

    with open(consola_file, 'w', encoding='utf-8') as f:
        f.write(consola_content_norm)
    print("Success: Updated paloSantoConsola.class.php")

    print("Agent Active Call Number resolution updates applied successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
