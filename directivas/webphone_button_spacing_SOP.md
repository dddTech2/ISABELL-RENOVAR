# SOP - Espaciado de Botones en el WebPhone

## Objetivo
1. Asegurar un espaciado visual consistente, limpio y premium entre los botones de control del WebPhone (Llamar, Colgar, Hold, Transferir, Silenciar, Contestar, Reconectar, Gestión).
2. Prevenir que los botones se toquen o se superpongan en pantallas con distintas resoluciones o navegadores heredados en terminales de call center.

## Entradas y Salidas
- **Entradas:**
  - Estructura HTML de los botones en `.webphone-buttons` dentro de `agent_console.tpl`.
- **Salidas:**
  - Reglas de CSS actualizadas en `webphone.css` con espaciados definidos vía CSS Grid (`row-gap` y `column-gap`).

## Lógica y Pasos

### 1. Modificación de Estilos en la Rejilla CSS
En `webphone.css`:
- Definir un espaciado vertical (`row-gap` / `grid-row-gap`) de `8px` en el contenedor `.webphone-buttons`.
- Definir un espaciado horizontal (`column-gap` / `grid-column-gap`) de `8px` en el contenedor `.webphone-buttons`.
- Remover cualquier margen individual conflictivo de `.webphone-btn` para delegar el control de flujo completamente a CSS Grid, o usar `margin: 0 !important` si es necesario para evitar sobrescrituras de temas globales.

### 2. Estructura de Clases
Asegurar que todas las combinaciones de botones visibles y ocultos utilicen las reglas CSS de Grid de forma limpia:
```css
.webphone-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 8px;
    grid-column-gap: 8px;
    row-gap: 8px;
    grid-row-gap: 8px;
    width: 100%;
}
```

## Restricciones y Trampas Conocidas
- **Busters de Caché:** Dado que Issabel almacena archivos CSS agresivamente en el navegador, asegurar que al realizar despliegues se incremente el tag de versión (por ejemplo, `webphone.css?v=4`) tanto en `agent_console.tpl` como en `index.php` para asegurar que el navegador cargue el nuevo archivo de estilos.
- **Navegadores antiguos:** Para navegadores muy viejos que no soportan completamente `row-gap` en Grid, el uso de prefijos heredados como `grid-row-gap` y `grid-column-gap` actúa como fallback de compatibilidad.
