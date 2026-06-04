# SOP - Directorio de Extensiones en WebPhone

## Objetivo
1. Permitir al agente visualizar una libreta o directorio de todas las extensiones configuradas en el sistema directamente en el panel del WebPhone.
2. Mostrar en tiempo real (o al consultar) el estado de disponibilidad (registro SIP/PJSIP) de cada extensión (verde para disponible/online, rojo para no disponible/offline).
3. Habilitar la búsqueda/filtrado interactivo por número de extensión o por nombre de usuario.
4. Facilitar la marcación y la transferencia rápida de llamadas haciendo clic en cualquier extensión del directorio.

## Entradas y Salidas
- **Entradas:** 
  - Clic en el botón de directorio (`#webphone-btn-directory`) al lado del campo de marcación.
  - Texto ingresado en el buscador del directorio (`#webphone-directory-search`).
  - Clic en un elemento/fila de extensión del directorio.
- **Salidas:**
  - Consulta AJAX al endpoint `index.php?menu={moduleName}&action=getExtensionsList`.
  - Renderizado dinámico de la tabla de extensiones con indicadores de estado de color.
  - Inserción de la extensión seleccionada en el input activo (`#webphone-number` o `#webphone-transfer-number`).

## Lógica y Pasos

### 1. Backend PHP (`modules/agent_console/index.php`)
- Interceptar la petición de `action=getExtensionsList` en `_moduleContent` (antes de la verificación del estado de sesión) para permitir que funcione en la pantalla de login.
- Definir la función `manejarSesionActiva_getExtensionsList`.
- En esta función:
  - Liberar la sesión (`session_commit()`) para evitar bloquear otras peticiones paralelas.
  - Conectar a la base de datos de Asterisk y obtener la lista de extensiones (`SELECT id, description, tech FROM devices ORDER BY id ASC`).
  - Conectarse al Asterisk Manager Interface (AMI) y ejecutar los comandos `sip show peers` y `pjsip show endpoints`.
  - Procesar las salidas de ambos comandos para identificar qué extensiones están registradas/online.
  - Devolver la lista en formato JSON: `[{"extension": "1001", "name": "Nombre", "tech": "pjsip", "status": "online"}, ...]`.

### 2. Interfaz Gráfica (HTML/TPL)
- En `agent_console.tpl` y `login_agent.tpl`, modificar el contenedor `.webphone-number-row` para incluir un botón a la derecha del input:
  ```html
  <button type="button" id="webphone-btn-directory" class="webphone-btn-directory" title="Libreta de Extensiones">📖</button>
  ```
- Agregar el contenedor del panel del directorio debajo de `.webphone-number-row`:
  ```html
  <div id="webphone-directory-panel" class="webphone-directory-panel" style="display: none;">
      <div class="directory-header">
          <span>Directorio</span>
          <button type="button" id="webphone-directory-close" class="directory-close-btn">&times;</button>
      </div>
      <div class="directory-search-row">
          <input type="text" id="webphone-directory-search" placeholder="Filtrar por nombre o ext..." autocomplete="off" />
      </div>
      <div class="directory-list-container">
          <div class="directory-loading">Cargando...</div>
          <table class="directory-table" style="display: none;">
              <thead>
                  <tr>
                      <th>Ext</th>
                      <th>Nombre</th>
                      <th>Estado</th>
                  </tr>
              </thead>
              <tbody id="webphone-directory-list"></tbody>
          </table>
      </div>
  </div>
  ```

### 3. Estilos Visuales (CSS)
- En `webphone.css`, agregar el diseño responsivo del directorio y del botón:
  - `.webphone-btn-directory` con fondo claro, bordes redondeados a la derecha, y hover.
  - `.webphone-directory-panel` con sombra sutil, fondo blanco y espaciado correcto.
  - `.status-dot` con `width: 8px; height: 8px; border-radius: 50%` y colores verde (`#5cb85c`) para `online` y rojo (`#d9534f`) para `offline`.
  - Ajustes de `max-height` y scroll para `.directory-list-container`.

### 4. Controlador de Eventos en JavaScript (`sip-phone.js`)
- Agregar `moduleName` a las variables de inicialización del WebPhone.
- Al hacer clic en `#webphone-btn-directory`:
  - Si el panel está abierto, ocultarlo.
  - Si está cerrado, mostrarlo, limpiar el buscador, mostrar "Cargando..." y llamar a la función interna para cargar la lista.
- En la función de carga:
  - Ejecutar petición GET/JSON al endpoint de PHP.
  - Guardar el listado recibido en una variable interna de caché para filtrado rápido.
  - Dibujar las filas de la tabla con las clases `.status-dot.online` u `.offline` según corresponda.
- Al escribir en `#webphone-directory-search`:
  - Filtrar localmente en base a la caché comparando el texto ingresado contra la extensión o el nombre de usuario (sin distinción de mayúsculas/minúsculas).
- Al hacer clic en una fila de la tabla:
  - Copiar el número de extensión al input de transferencia si el panel de transferencia está visible, o al campo principal de marcación en caso contrario.

## Restricciones y Trampas Conocidas
- **Rendimiento de Conexión AMI:** La consulta de Peers de Asterisk vía AMI tarda fracciones de segundo. El listado no debe consultarse en cada pulsación de tecla, sino únicamente cuando el usuario abre el directorio.
- **Seguridad en DB:** Usar sentencias preparadas o saneamiento de DSN provisto por el framework (`generarDSNSistema`).
- **Llamadas jQuery dentro del WebPhone (Closure):** Dentro de `WebPhone`, `$` está redefinido como una función personalizada para manejar el contexto Picture-in-Picture (`window.pipWindow`). No tiene métodos estáticos como `$.getJSON`. Debe usarse `window.jQuery.getJSON` en su lugar.
