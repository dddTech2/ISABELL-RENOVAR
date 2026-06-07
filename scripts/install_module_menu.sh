#!/bin/bash
# Script para registrar el módulo Coordinator Dashboard en Issabel
# Debe ejecutarse como root en el servidor Issabel

MENU_DB="/var/www/db/menu.db"
ACL_DB="/var/www/db/acl.db"

# 1. Registrar en el menú (bajo Call Center)
echo "Registrando en menu.db..."
sqlite3 $MENU_DB "DELETE FROM menu WHERE id = 'coordinator_dashboard';"
sqlite3 $MENU_DB "INSERT INTO menu (id, id_menuparent, link, type, order_no) VALUES ('coordinator_dashboard', 'callcenter', '', 'module', 10);"

# 2. Registrar el recurso en ACL
echo "Registrando en acl.db..."
sqlite3 $ACL_DB "DELETE FROM acl_resource WHERE name = 'coordinator_dashboard';"
sqlite3 $ACL_DB "INSERT INTO acl_resource (name, description) VALUES ('coordinator_dashboard', 'Dashboard Coordinador');"

# 3. Dar permisos al grupo Administrador (id_group = 1, id_action = 1)
echo "Asignando permisos al grupo Administrador..."
RESOURCE_ID=$(sqlite3 $ACL_DB "SELECT id FROM acl_resource WHERE name = 'coordinator_dashboard';")
sqlite3 $ACL_DB "DELETE FROM acl_group_permission WHERE id_group = 1 AND id_resource = $RESOURCE_ID;"
sqlite3 $ACL_DB "INSERT INTO acl_group_permission (id_action, id_group, id_resource) VALUES (1, 1, $RESOURCE_ID);"

echo "¡Módulo registrado con éxito! Refresca la página en Issabel."
