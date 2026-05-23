#!/usr/bin/env php
<?php
/**
 * Script de Consola para Finalizar Descanso de un Agente (Fin Descanso)
 * Uso: php scripts/unbreak_agent.php <identificador_de_agente>
 */

// Establecer el directorio de trabajo a la raíz del proyecto para que las rutas relativas se resuelvan correctamente.
$base_dir = dirname(__DIR__);
chdir($base_dir);

// Configurar los paths de inclusión para las librerías globales de Issabel y del módulo de consola de agente.
ini_set('include_path', "$base_dir:$base_dir/libs:$base_dir/modules/agent_console/libs:" . ini_get('include_path'));

// Carga de dependencias fundamentales del framework
include_once "libs/misc.lib.php";
include_once "configs/default.conf.php";
include_once "libs/paloSantoDB.class.php";
require_once "modules/agent_console/libs/paloSantoConsola.class.php";

// Validar argumentos de la línea de comandos
if ($argc < 2) {
    echo "Uso: php " . basename($argv[0]) . " <identificador_de_agente>\n";
    echo "Ejemplos:\n";
    echo "  php " . basename($argv[0]) . " PJSIP/2009\n";
    echo "  php " . basename($argv[0]) . " Agent/1001\n";
    echo "  php " . basename($argv[0]) . " 2009\n";
    exit(1);
}

$agentInput = trim($argv[1]);
$agentChannel = $agentInput;

// Si el parámetro no contiene una barra '/', intentamos buscar su tipo en la base de datos de call_center.
if (strpos($agentInput, '/') === false) {
    echo "Buscando canal para el agente número: $agentInput...\n";

    if (!isset($arrConf['cadena_dsn'])) {
        echo "\033[0;31mERROR: No se encontró la configuración 'cadena_dsn' para la base de datos.\033[0m\n";
        exit(1);
    }

    $oDB = new paloDB($arrConf['cadena_dsn']);
    if (!empty($oDB->errMsg)) {
        echo "\033[0;31mERROR de conexión a base de datos:\033[0m " . $oDB->errMsg . "\n";
        exit(1);
    }

    // Buscamos el agente activo ('A') correspondiente al número provisto
    $query = "SELECT type, number FROM agent WHERE number = ? AND estatus = 'A'";
    $row = $oDB->getFirstRowQuery($query, TRUE, array($agentInput));

    if (is_array($row) && count($row) > 0 && isset($row['type'])) {
        $agentChannel = $row['type'] . '/' . $row['number'];
        echo "Canal resuelto desde la base de datos: $agentChannel\n";
    } else {
        echo "\033[0;33mADVERTENCIA: Agente '$agentInput' no encontrado como activo en la base de datos.\033[0m\n";
        // Intentamos usar Agent/ como fallback por defecto
        $agentChannel = "Agent/" . $agentInput;
        echo "Usando canal fallback: $agentChannel\n";
    }
}

echo "Intentando quitar descanso (Fin Descanso) al agente: $agentChannel...\n";

try {
    // Instanciar el objeto de control de la consola del agente
    $oConsola = new PaloSantoConsola($agentChannel);
    
    // Ejecutar el método para terminar el descanso
    $exito = $oConsola->terminarBreak();

    if ($exito) {
        echo "\033[0;32mÉXITO: El descanso del agente $agentChannel ha sido finalizado correctamente y ha regresado a la cola.\033[0m\n";
        exit(0);
    } else {
        echo "\033[0;31mERROR: No se pudo terminar el descanso del agente.\033[0m\n";
        echo "Detalle del error: " . $oConsola->errMsg . "\n";
        exit(1);
    }
} catch (Exception $e) {
    echo "\033[0;31mEXCEPCIÓN: Ocurrió un error al ejecutar la acción.\033[0m\n";
    echo "Mensaje: " . $e->getMessage() . "\n";
    exit(1);
}
