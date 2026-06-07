<?php
/* Issabel module installer for coordinator_dashboard
 * Run from /var/www/html as root:
 *   php modules/coordinator_dashboard/install.php
 */

$BASE = '/var/www/html';
set_include_path($BASE . PATH_SEPARATOR . get_include_path());

require_once $BASE . '/libs/paloSantoInstaller.class.php';
require_once $BASE . '/libs/paloSantoMenu.class.php';
require_once $BASE . '/libs/paloACL.class.php';
require_once $BASE . '/libs/paloSantoDB.class.php';
require_once $BASE . '/libs/misc.lib.php';

// Load DSN config
$arrConf = array();
require_once $BASE . '/configs/default.conf.php';

$oInstaller = new Installer();

// ---- 1. Register menu entry ----
echo "1. Registrando entrada de menú...\n";
$pDB_menu = new paloDB($arrConf['issabel_dsn']['menu']);
$oMenu    = new paloMenu($pDB_menu);

if ($oMenu->existeMenu('coordinator_dashboard')) {
    echo "   Ya existe en menú, omitiendo.\n";
} else {
    $ok = $oMenu->createMenu(
        'coordinator_dashboard',       // id
        'Dashboard Coordinador',       // name
        'call_center',                 // parent
        'module',                      // type
        '',                            // link
        5                              // order
    );
    if ($ok) {
        echo "   OK - Entrada creada bajo call_center\n";
    } else {
        echo "   ERROR: " . $oMenu->errMsg . "\n";
    }
}

// ---- 2. Register ACL resource and grant to Administrators ----
echo "2. Registrando recurso ACL...\n";
$pDB_acl = new paloDB($arrConf['issabel_dsn']['acl']);
$oACL    = new paloACL($pDB_acl);

$ok = $oInstaller->addResourceMembership($oACL, array(
    'menuid' => 'coordinator_dashboard',
    'tag'    => 'Dashboard Coordinador',
));
if ($ok) {
    echo "   OK - Recurso ACL creado y asignado al grupo Administrador\n";
} else {
    // Maybe resource already exists - try to just assign permission
    echo "   Nota: " . $oInstaller->_errMsg . " (puede que ya exista)\n";
}

// ---- 3. Clear Smarty cache ----
echo "3. Limpiando caché de Smarty...\n";
$oInstaller->refresh($BASE);
echo "   OK\n";

echo "\n=== Listo! Cierra sesión y vuelve a entrar en Issabel ===\n";
echo "    El módulo aparecerá bajo Call Center > Dashboard Coordinador\n";
?>
