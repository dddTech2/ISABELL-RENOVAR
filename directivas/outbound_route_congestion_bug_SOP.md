# SOP - Outbound Route Congestion Destination Saving Bug

## Objetivo
Resolver el problema por el cual el "Destino opcional en caso de Congestión" (Optional Destination on Congestion) no se guarda en las Rutas Salientes (Outbound Routes) de Issabel y siempre se revierte a "Congestión Normal" (Normal Congestion) al hacer clic en Enviar/Guardar.

## Entradas y Salidas
- **Entrada:** Datos enviados por el formulario de la ruta saliente en `page.routing.php`, que incluye `$_REQUEST['goto0']` con el nombre del módulo destino (ej. `app-blackhole0`, `announcement0`).
- **Salida:** Guardar correctamente el valor del destino seleccionado (`$dest`) en la base de datos (tabla `outbound_routes`, columna `dest`) en lugar de almacenar un valor vacío.

## Lógica y Pasos

### 1. Diagnóstico del Error
- En `drawselects()`, el valor del primer select (`goto0`) se genera agregando el índice `$i` (ej. `app-blackhole0`).
- Al enviar el formulario, el script PHP `page.routing.php` recibe `$_REQUEST['goto0']` como `app-blackhole0` (o similar).
- El código original en la línea 165 de `page.routing.php` intenta recuperar el destino haciendo:
  `$dest = $goto ? $_REQUEST[$goto . '0'] : '';`
- Dado que `$goto` ya contiene el `'0'` al final (debido al comportamiento de `drawselects()`), concatenar otro `'0'` genera la clave `app-blackhole00`.
- Como `app-blackhole00` no existe en la petición (la caja del destino hijo se llama `app-blackhole0`), `$dest` se evalúa como vacío (`''`), causando que se ignore la selección y se revierta a "Congestión Normal".

### 2. Solución en Código
- Modificar el archivo `admin/modules/core/page.routing.php` en la línea 165.
- Cambiar la asignación de `$dest` para que busque tanto `$goto` directamente (caso con sufijo integrado `app-blackhole0`) como `$goto . '0'` (caso legacy sin sufijo):
  ```php
  $dest = $goto ? (isset($_REQUEST[$goto]) ? $_REQUEST[$goto] : (isset($_REQUEST[$goto . '0']) ? $_REQUEST[$goto . '0'] : '')) : '';
  ```
  Esto permite obtener el valor del destino hijo sin importar si `$goto` viene con o sin el sufijo de índice.

## Restricciones y Trampas Conocidas
- **Compatibilidad con múltiples destinos:** Aunque esta sección en rutas salientes solo tiene un selector de destino (índice 0), es importante mantener la compatibilidad hacia adelante por si en el futuro se incrementa el número de selectores o para otros módulos de FreePBX/Issabel que usan una lógica similar.
