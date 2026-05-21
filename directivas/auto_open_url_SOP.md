# SOP - Auto-Open External URL on Agent Console

## Objetivo
Configurar la consola de agente de Issabel para que, cuando ingrese una llamada activa (evento `agentlinked`), el enlace externo configurado de tipo ventana (window) se abra automáticamente en una nueva pestaña del navegador.

## Entradas y Salidas
- **Entrada:** Evento `agentlinked` en el sondeo de estado del agente (`manejarRespuestaStatus`).
- **Salida:** Ejecución automática de `window.open` para la URL externa sin requerir interacción manual del operador en el botón verde.

## Lógica y Pasos
1. **Modificar las funciones de apertura de URLs externas:** En `abrir_url_externo`, `abrir_url_externo2` y `abrir_url_externo3` del archivo `javascript.js`, añadir un cuarto parámetro opcional llamado `autoOpen`.
2. **Implementar apertura automática en el caso 'window':** Dentro de la lógica del caso `window` de cada una de estas funciones, verificar si `autoOpen` es verdadero y la URL no es nula. Si se cumplen las condiciones, invocar `window.open(url, '_blank')`.
3. **Condicionar la llamada a las funciones:**
   - En `manejarRespuestaStatus` (cuando se recibe el evento `agentlinked` en vivo), pasar `true` como argumento de `autoOpen` a `abrir_url_externo`, `abrir_url_externo2` y `abrir_url_externo3`.
   - En `initialize_client_state` (carga inicial de la página / refresco), pasar `false` para evitar la duplicación de pestañas abiertas al refrescar.

## Restricciones y Trampas Conocidas
- **Bloqueadores de Ventanas Emergentes:** La apertura de ventanas por código sin acción del usuario suele ser bloqueada por los navegadores. Los gestores y operadores deben configurar el navegador para "Permitir popups y redirecciones" para el dominio/IP de la consola de Issabel.
