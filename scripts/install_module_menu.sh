#!/bin/bash
# Script para registrar el módulo Coordinator Dashboard en Issabel
# Debe ejecutarse como root desde /var/www/html/issabel

BASE="/var/www/html"
MENU_DB="$BASE/db/menu.db"
ACL_DB="$BASE/db/acl.db"

echo "=== Registrando coordinator_dashboard en Issabel ==="

# 1. Registrar en el menú (columnas reales: id, Name, Type, Link, IdParent, order_no)
echo "1. Insertando en menu.db..."
sqlite3 "$MENU_DB" "DELETE FROM menu WHERE id = 'coordinator_dashboard';"
sqlite3 "$MENU_DB" "INSERT INTO menu (id, Name, Type, Link, IdParent, order_no) VALUES ('coordinator_dashboard', 'Dashboard Coordinador', 'module', '', 'call_center', 5);"
if [ $? -eq 0 ]; then
    echo "   OK - Entrada de menú creada bajo call_center"
else
    echo "   ERROR al insertar en menu.db"
    exit 1
fi

# 2. Registrar el recurso en ACL
echo "2. Insertando recurso en acl.db..."
sqlite3 "$ACL_DB" "DELETE FROM acl_resource WHERE name = 'coordinator_dashboard';"
sqlite3 "$ACL_DB" "INSERT INTO acl_resource (name, description) VALUES ('coordinator_dashboard', 'Dashboard Coordinador');"
if [ $? -eq 0 ]; then
    echo "   OK - Recurso ACL creado"
else
    echo "   ERROR al insertar recurso ACL"
    exit 1
fi

# 3. Dar permisos al grupo Administrador (id_group=1)
echo "3. Asignando permisos al grupo Administrador..."
RESOURCE_ID=$(sqlite3 "$ACL_DB" "SELECT id FROM acl_resource WHERE name = 'coordinator_dashboard';")
echo "   Resource ID: $RESOURCE_ID"
sqlite3 "$ACL_DB" "DELETE FROM acl_group_permission WHERE id_group = 1 AND id_resource = $RESOURCE_ID;"
sqlite3 "$ACL_DB" "INSERT INTO acl_group_permission (id_action, id_group, id_resource) VALUES (1, 1, $RESOURCE_ID);"
if [ $? -eq 0 ]; then
    echo "   OK - Permisos asignados"
else
    echo "   ERROR al asignar permisos"
    exit 1
fi

# 4. Limpiar caché de Smarty
echo "4. Limpiando caché de Smarty..."
rm -rf "$BASE/var/templates_c/*" 2>/dev/null
echo "   OK"

echo ""
echo "=== Listo! Cierra sesión y vuelve a entrar en Issabel ==="
echo "    El módulo aparecerá bajo Call Center > Dashboard Coordinador"
