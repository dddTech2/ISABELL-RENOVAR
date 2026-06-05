# SOP - Control de Múltiples Pestañas y Transferencia de Registro (Takeover)

## Objetivo
1. Evitar conflictos de registro SIP, timbrados dobles y errores de audio/WebRTC que ocurren cuando un usuario abre la consola de agentes de Issabel en múltiples pestañas del navegador simultáneamente.
2. Garantizar que únicamente una pestaña (la más reciente o la que solicite reconexión) mantenga el registro SIP activo con Asterisk.
3. Notificar de forma visual y clara en las pestañas inactivas que el teléfono ha sido abierto en otro lugar, deshabilitando la capacidad de llamar y ofreciendo un botón rápido para recuperar la conexión ("Reconectar").

## Entradas y Salidas
- **Entradas:**
  - Inicialización del WebPhone en una pestaña nueva.
  - Clic en el botón "Reconectar" (`#webphone-btn-reconnect`) en una pestaña desactivada.
  - Recepción del evento `'takeover'` a través del canal de comunicación del navegador (`BroadcastChannel`).
- **Salidas:**
  - Envío del mensaje de difusión `'takeover'` al canal `issabel_webphone_{extension}`.
  - Desconexión y desregistro de la sesión SIP (`disconnect()`) en las pestañas viejas.
  - Actualización del estado visual en las pestañas desplazadas (mostrar estado "Abierto en otra pestaña" con color amarillo/advertencia y habilitar botón "Reconectar").

## Lógica y Pasos

### 1. Interfaz de Usuario y Estilos (CSS/HTML)
- En `webphone.css`, agregar el estilo para el estado desplazado `.webphone-taken-over`:
  ```css
  .webphone-taken-over {
      background: #fcf8e3;
      color: #8a6d3b;
      border: 1px solid #f0ad4e;
  }
  .webphone-taken-over .status-indicator {
      background: #f0ad4e;
      box-shadow: 0 0 6px #f0ad4e;
  }
  ```
- En `sip-phone.js`, dentro de `updateUI()`:
  - Manejar el estado `state.takenOver` antes de otros estados genéricos:
    - Establecer la clase `.webphone-taken-over` al contenedor de estado `#webphone-status`.
    - Cambiar el texto de estado a `"Abierto en otra pestaña"`.
    - Ocultar botones de gestión y deshabilitar botón de marcado.
  - Si `state.takenOver` o `state.authFailed` es verdadero, mostrar el botón de reconexión (`#webphone-btn-reconnect`). En caso contrario, ocultarlo.

### 2. Comunicación entre Pestañas (`BroadcastChannel` en `sip-phone.js`)
- Definir la variable de canal `var broadcastChannel = null;` en la parte superior del módulo.
- En la función `init(cfg, cbs)`:
  - Si el navegador soporta `window.BroadcastChannel`, inicializar una nueva instancia asociada a la extensión del agente:
    ```javascript
    broadcastChannel = new window.BroadcastChannel('issabel_webphone_' + config.extension);
    ```
  - Registrar el listener de mensajes `onmessage` del canal:
    - Si el mensaje recibido es `'takeover'`:
      - Establecer `state.takenOver = true`.
      - Ejecutar `disconnect()` para colgar llamadas activas, cancelar el registro SIP y apagar el UserAgent en esta pestaña.
  - Enviar de inmediato un mensaje `'takeover'` al canal (`broadcastChannel.postMessage('takeover')`) para indicarle a cualquier pestaña previa que entregue el registro.

### 3. Reclamar el Registro (Función `reconnect()`)
- En la función `reconnect()`:
  - Establecer `state.takenOver = false` (para permitir que la pestaña actual intente registrarse y el watchdog funcione).
  - Si `broadcastChannel` existe, enviar un mensaje `'takeover'` antes de iniciar la reconexión, obligando a cualquier otra pestaña a ceder el control.
  - Proceder con la recreación del UserAgent y el registro SIP normal.

### 4. Restricción del Watchdog, Foco de Pestaña y Cooldown de Conexión
- Modificar tanto el watchdog (`setInterval`) como el listener de `visibilitychange` en `sip-phone.js` para que:
  - **No** fuercen la reconexión si la pestaña ha sido desplazada por takeover (`!state.takenOver` debe ser verdadero), evitando peleas infinitas por el registro entre múltiples pestañas al alternar o enfocar pestañas inactivas.
  - Respeten un tiempo de espera o cooldown (mínimo 15 segundos) desde la última llamada a `reconnect()` o creación del UserAgent (`state.lastConnectTime`), previniendo disparar múltiples reconexiones en paralelo cuando el socket está en fase de establecimiento (lo que genera errores "Connect aborted" y cierres abruptos de WebSocket).
- Configurar la propiedad `requestDelegate` con la función `onReject` al instanciar `SIP.Registerer` para interceptar de manera robusta los códigos de error del servidor (como 403 o 401) y detener los intentos para evitar bloqueos.
- Al desconectar o reconectar, asegurarse de llamar a `registerer.dispose()` para limpiar referencias del registro anterior y evitar reintentos colisionados.

## Restricciones y Trampas Conocidas
- **Nombres de Canales Únicos:** El `BroadcastChannel` debe incluir el número de extensión en el nombre del canal (ej. `issabel_webphone_1005`) para evitar que pestañas de agentes diferentes interfieran entre sí si comparten la misma red o navegador en la misma máquina física.
- **Bucle de Pelea de Pestañas (Ping-Pong):** Si la reconexión automática del watchdog o de focus de página (`visibilitychange`) no respetase la bandera `takenOver`, dos pestañas entrarían en un ciclo infinito de quitarse el registro mutuamente. La bandera `takenOver` se debe limpiar estrictamente bajo acción explícita del usuario (clic en "Reconectar").
- **Carreras de Conexión y Abortos de Socket (Connect Aborted):** No intentar apagar el UserAgent (`stop()`) mientras se está conectando. Utilizar la marca temporal `state.lastConnectTime` para establecer un cooldown de 15 segundos antes de que el watchdog o los eventos de visibilidad de la pestaña puedan forzar una nueva reconexión.
- **Pérdida de Mensajes de Desconexión en Reconexión Manual (CRÍTICO):** Al hacer clic en "Reconectar", es imperativo limpiar el estado `state.takenOver = false` y enviar de inmediato el mensaje `'takeover'` a través del `BroadcastChannel`. Si no se hace esto, la pestaña anterior no desactivará su registro SIP y Asterisk rechazará la nueva solicitud con un error `403 Forbidden` debido a la colisión de sesión. Esto activará el detector de error de autenticación, deteniendo la reconexión.
- **Limpieza del Registro Activo (Unregister):** Solo llamar a `registerer.unregister()` en la desconexión si `state.registered` es verdadero, y llamar siempre a `registerer.dispose()` para prevenir que se intente enviar un desregistro si ya hay una transacción de registro en curso, lo que produce advertencias críticas en la consola de SIP.js.
- **Soporte de Navegador:** BroadcastChannel es ampliamente soportado en navegadores modernos. Si no está disponible en navegadores antiguos, el sistema no fallará (se envuelve en validación `if (window.BroadcastChannel)`), simplemente funcionará con el comportamiento tradicional de colisión SIP estándar.

