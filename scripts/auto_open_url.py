import os

def main():
    filepath = r"\\wsl.localhost\Ubuntu\home\daviddaza\isabell\ISABELL-RENOVAR\modules\agent_console\themes\default\js\javascript.js"
    if not os.path.exists(filepath):
        # fallback for relative path if absolute wsl path doesn't resolve in windows python
        filepath = os.path.join("modules", "agent_console", "themes", "default", "js", "javascript.js")
    
    print(f"Reading file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Modify abrir_url_externo definitions to accept autoOpen
    # function abrir_url_externo(urlopentype, url, title)
    old_def1 = "function abrir_url_externo(urlopentype, url, title)"
    new_def1 = "function abrir_url_externo(urlopentype, url, title, autoOpen)"
    
    old_def2 = "function abrir_url_externo2(urlopentype, url2, title)"
    new_def2 = "function abrir_url_externo2(urlopentype, url2, title, autoOpen)"
    
    old_def3 = "function abrir_url_externo3(urlopentype, url3, title)"
    new_def3 = "function abrir_url_externo3(urlopentype, url3, title, autoOpen)"

    content = content.replace(old_def1, new_def1)
    content = content.replace(old_def2, new_def2)
    content = content.replace(old_def3, new_def3)

    # 2. Modify case 'window' for each to execute window.open(url, '_blank') if autoOpen is true
    # We locate the click listener mapping and insert the autoOpen condition
    # For abrir_url_externo:
    old_case1 = """            if (url != null) {
                $('<button id="externalurl-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl-btn').on('click', function () {
                    if (url) {
                        window.open(url, '_blank');
                    }
                });
            }"""
    new_case1 = """            if (url != null) {
                $('<button id="externalurl-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl-btn').on('click', function () {
                    if (url) {
                        window.open(url, '_blank');
                    }
                });

                if (autoOpen) {
                    window.open(url, '_blank');
                }
            }"""

    # For abrir_url_externo2:
    old_case2 = """            if (url2 != null) {
                // Agregar el botón con un ID
                $('<button id="externalurl2-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl2-btn').on('click', function () {
                    if (url2) {
                        window.open(url2, '_blank');
                    }
                });
            }"""
    new_case2 = """            if (url2 != null) {
                // Agregar el botón con un ID
                $('<button id="externalurl2-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl2-btn').on('click', function () {
                    if (url2) {
                        window.open(url2, '_blank');
                    }
                });

                if (autoOpen) {
                    window.open(url2, '_blank');
                }
            }"""

    # For abrir_url_externo3:
    old_case3 = """            if (url3 != null) {
                $('<button id="externalurl3-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl3-btn').on('click', function () {
                    if (url3) {
                        window.open(url3, '_blank');
                    }
                });
            }"""
    new_case3 = """            if (url3 != null) {
                $('<button id="externalurl3-btn" class="externalurl-btn">' + title + '</button>')
                    .appendTo('#issabel-callcenter-cejillas-contenido > .ui-tabs-nav');

                // Agregar evento de clic al botón
                $('#externalurl3-btn').on('click', function () {
                    if (url3) {
                        window.open(url3, '_blank');
                    }
                });

                if (autoOpen) {
                    window.open(url3, '_blank');
                }
            }"""

    content = content.replace(old_case1, new_case1)
    content = content.replace(old_case2, new_case2)
    content = content.replace(old_case3, new_case3)

    # 3. Modify initialize_client_state calls to pass false
    old_init = """    iniciar_cronometro((nuevoEstado.timer_seconds !== '') ? nuevoEstado.timer_seconds : null);
    abrir_url_externo3(nuevoEstado.urlopentype3, nuevoEstado.url3, nuevoEstado.urldescription3);
    abrir_url_externo2(nuevoEstado.urlopentype2, nuevoEstado.url2, nuevoEstado.urldescription2);
    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription);"""
    new_init = """    iniciar_cronometro((nuevoEstado.timer_seconds !== '') ? nuevoEstado.timer_seconds : null);
    abrir_url_externo3(nuevoEstado.urlopentype3, nuevoEstado.url3, nuevoEstado.urldescription3, false);
    abrir_url_externo2(nuevoEstado.urlopentype2, nuevoEstado.url2, nuevoEstado.urldescription2, false);
    abrir_url_externo(nuevoEstado.urlopentype, nuevoEstado.url, nuevoEstado.urldescription, false);"""
    
    content = content.replace(old_init, new_init)

    # 4. Modify manejarRespuestaStatus calls to pass true
    old_linked = """            if (!respuesta[i].urlopentype3){
                respuesta[i].urlopentype3 = "DELETE";
            }
            abrir_url_externo3(respuesta[i].urlopentype3, respuesta[i].url3, respuesta[i].urldescription3);

            if (!respuesta[i].urlopentype2){
                respuesta[i].urlopentype2 = "DELETE";
            }
            abrir_url_externo2(respuesta[i].urlopentype2, respuesta[i].url2, respuesta[i].urldescription2);

            if (!respuesta[i].urlopentype){
                respuesta[i].urlopentype = "DELETE";
            }
			abrir_url_externo(respuesta[i].urlopentype, respuesta[i].url, respuesta[i].urldescription);"""
    new_linked = """            if (!respuesta[i].urlopentype3){
                respuesta[i].urlopentype3 = "DELETE";
            }
            abrir_url_externo3(respuesta[i].urlopentype3, respuesta[i].url3, respuesta[i].urldescription3, true);

            if (!respuesta[i].urlopentype2){
                respuesta[i].urlopentype2 = "DELETE";
            }
            abrir_url_externo2(respuesta[i].urlopentype2, respuesta[i].url2, respuesta[i].urldescription2, true);

            if (!respuesta[i].urlopentype){
                respuesta[i].urlopentype = "DELETE";
            }
			abrir_url_externo(respuesta[i].urlopentype, respuesta[i].url, respuesta[i].urldescription, true);"""

    # Wait, check if there is an issue with indentation or carriage returns \r\n vs \n
    # Standardize line endings to \n temporarily, replace, then write
    content_normalized = content.replace("\r\n", "\n")
    old_linked_normalized = old_linked.replace("\r\n", "\n")
    new_linked_normalized = new_linked.replace("\r\n", "\n")
    
    if old_linked_normalized in content_normalized:
        content_normalized = content_normalized.replace(old_linked_normalized, new_linked_normalized)
    else:
        print("Warning: old_linked pattern not found directly, performing line-by-line replace or alternative matching.")
        # Let's try matching with different indentations
        # We can do exact line replacement
        content_normalized = content_normalized.replace(
            "abrir_url_externo3(respuesta[i].urlopentype3, respuesta[i].url3, respuesta[i].urldescription3);",
            "abrir_url_externo3(respuesta[i].urlopentype3, respuesta[i].url3, respuesta[i].urldescription3, true);"
        )
        content_normalized = content_normalized.replace(
            "abrir_url_externo2(respuesta[i].urlopentype2, respuesta[i].url2, respuesta[i].urldescription2);",
            "abrir_url_externo2(respuesta[i].urlopentype2, respuesta[i].url2, respuesta[i].urldescription2, true);"
        )
        content_normalized = content_normalized.replace(
            "abrir_url_externo(respuesta[i].urlopentype, respuesta[i].url, respuesta[i].urldescription);",
            "abrir_url_externo(respuesta[i].urlopentype, respuesta[i].url, respuesta[i].urldescription, true);"
        )
        
    print(f"Writing updated file: {filepath}")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(content_normalized)
    print("Done successfully!")

if __name__ == "__main__":
    main()
