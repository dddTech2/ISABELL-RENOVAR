# SOP - Mantenimiento de Conexión (Keepalive) y Auto-Reconexión de WebPhone

## Objetivo
1. Evitar que Asterisk cierre las conexiones WebSocket (WSS) inactivas mediante el envío de keep-alives (CRLF) periódicos desde el navegador.
2. Habilitar la reconexión automática y transparente en el WebPhone cuando la conexión se pierde por inactividad, suspensión de pestaña o microcortes de red.
3. Reiniciar el contador de intentos de registro en conexiones nuevas para evitar el bloqueo permanente por límite de intentos.
4. Detectar cuando la pestaña de la consola vuelve al primer plano para forzar la reconexión inmediata si se encuentra desconectada.

## Entradas y Salidas
- **Entradas:** 
  - Inicialización del WebPhone en la consola del agente.
  - Evento de reconexión de WebSocket.
  - Evento de cambio de visibilidad de la página (`visibilitychange`).
- **Salidas:**
  - Envío de CRLF keep-alives cada 15 segundos sobre el WebSocket.
  - Re-intentos de reconexión automática (hasta 10 intentos cada 5 segundos).
  - Reinicio del contador de intentos (`registerAttempts = 0`) en la función `onConnect`.
  - Disparo de `reconnect()` si el agente vuelve a la pestaña inactiva y el WebPhone estaba desconectado.

## Lógica y Pasos

### 1. Modificación de `sip-phone.js` (Configuración de Transport)
- Agregar las opciones `keepAliveInterval: 15`, `keepAliveDebounce: 10`, `reconnectionAttempts: 10` y `reconnectionDelay: 5` (en lugar del obsoleto `reconnectionTimeout`) al objeto `transportOptions` en `createUserAgent()`.
- Agregar `logLevel: 'warn'` al objeto principal de configuración del `UserAgent` para evitar el volcado de configuración verbose en la consola del navegador.

### 2. Reiniciar Contador de Intentos de Registro
- En la función de callback `userAgent.transport.onConnect`, establecer `registerAttempts = 0` antes de invocar `register()`.

### 3. Recuperación por Enfoque de Pestaña (Page Visibility)
- Suscribirse al evento `visibilitychange` a nivel de `document` dentro de `sip-phone.js`. 
- Si `document.hidden` es falso, verificar si existe `userAgent` y el estado no es `registered` ni `authFailed`. En ese caso, invocar `reconnect()`.

## Restricciones y Trampas Conocidas
- **Deprecación de reconnectionTimeout:** En versiones modernas de SIP.js (>= 0.16.0), el parámetro de espera de reconexión pasó a llamarse `reconnectionDelay`. El uso de `reconnectionTimeout` genera advertencias en consola.
- **Bloqueos por Fail2ban:** Mantener `maxRegisterAttempts = 1` para respuestas de credenciales incorrectas (401/403) para evitar bloqueos por fuerza bruta, pero permitir reconexiones en caídas de red normales reiniciando el contador únicamente al lograr un handshake exitoso de WebSocket (`onConnect`).

