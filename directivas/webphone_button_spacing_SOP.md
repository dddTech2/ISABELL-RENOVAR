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
- Definir espaciados verticales y horizontales (`gap`, `grid-gap`, `row-gap`, `column-gap`, etc.) de `8px` en el contenedor `.webphone-buttons`.
- Remover `width: 100%` de `.webphone-btn` para evitar que los botones excedan el contenedor (overflow) en ciertas implementaciones antiguas de CSS Grid.
- Remover cualquier margen individual conflictivo de `.webphone-btn` para delegar el control de flujo completamente a CSS Grid, o usar `margin: 0 !important` si es necesario.
- El botón `Llamar` (`#webphone-btn-call`) debe usar `grid-column: span 1` (su valor por defecto al remover `span 2`) para que se coloque lado a lado con el botón `Gestión` cuando el agente inicia sesión. En la pantalla de login, al estar oculto el botón de Gestión, el botón `Llamar` ocupará la primera columna, conservando un diseño balanceado sin exceder límites.

### 2. Estructura de Clases
Asegurar que todas las combinaciones de botones visibles y ocultos utilicen las reglas CSS de Grid de forma limpia:
```css
.webphone-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    grid-gap: 8px;
    column-gap: 8px;
    grid-column-gap: 8px;
    row-gap: 8px;
    grid-row-gap: 8px;
    width: 100%;
}
```

## Restricciones y Trampas Conocidas
- **Busters de Caché:** Dado que Issabel almacena archivos CSS agresivamente en el navegador, asegurar que al realizar despliegues se incremente el tag de versión (por ejemplo, `webphone.css?v=5`) tanto en `agent_console.tpl` como en `index.php` para asegurar que el navegador cargue el nuevo archivo de estilos.
- **Navegadores antiguos:** Para navegadores muy viejos que no soportan completamente `row-gap` o `gap` en Grid, es imperativo declarar `grid-gap`, `grid-row-gap` y `grid-column-gap` juntos.
- **Overflow de Botones en Grid:** La regla `width: 100%` en elementos hijos de Grid con `padding` suele romper la caja (box model) y desbordar la cuadrícula si el navegador ignora `box-sizing: border-box` dentro del contexto flex/grid. Remover el ancho fijo y confiar en `justify-self: stretch` (default del Grid) resuelve la salida fuera del `.webphone-panel`.
