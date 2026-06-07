<?php
/* Issabel module installer for coordinator_dashboard
 * This file is called by the Issabel framework when installing/updating the module.
 * It registers the menu entry and ACL resource using the native Installer API.
 */

require_once 'libs/paloSantoInstaller.class.php';
require_once 'libs/paloSantoMenu.class.php';
require_once 'libs/paloACL.class.php';
require_once 'libs/paloSantoDB.class.php';

$oInstaller = new Installer();

// ---- 1. Register menu entry ----
$oMenu = new PaloSantoMenu();
$oInstaller->addMenu($oMenu, array(
    'menuid'  => 'coordinator_dashboard',
    'tag'     => 'Dashboard Coordinador',
    'parent'  => 'call_center',
    'type'    => 'module',
    'link'    => '',
    'order'   => '5',
));

// ---- 2. Register ACL resource and grant to Administrators ----
$pDB_acl = new paloDB(generarDSNSistema('acl'));
$oACL    = new paloACL($pDB_acl);
$oInstaller->addResourceMembership($oACL, array(
    'menuid' => 'coordinator_dashboard',
    'tag'    => 'Dashboard Coordinador',
));

// ---- 3. Refresh Issabel menu cache ----
$oInstaller->refresh();

echo "coordinator_dashboard instalado correctamente.\n";
?>
