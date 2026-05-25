import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    target_file = os.path.join(workspace_dir, "admin", "modules", "core", "page.routing.php")

    print(f"Target file: {target_file}")

    if not os.path.exists(target_file):
        print(f"Error: Target file not found at {target_file}")
        return 1

    with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Target block to replace
    target_line = "$dest = $goto ? $_REQUEST[$goto . '0'] : '';"
    replacement_line = "$dest = $goto ? (isset($_REQUEST[$goto]) ? $_REQUEST[$goto] : (isset($_REQUEST[$goto . '0']) ? $_REQUEST[$goto . '0'] : '')) : '';"

    if target_line not in content:
        print("Error: Target line was not found in the file.")
        return 1

    content_modified = content.replace(target_line, replacement_line)

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content_modified)

    print("Success: page.routing.php has been successfully updated.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
