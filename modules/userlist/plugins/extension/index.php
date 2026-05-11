<?php
/* vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
 Codificación: UTF-8
 +----------------------------------------------------------------------+
 | Issabel version 0.5                                                  |
 | http://www.issabel.org                                               |
 +----------------------------------------------------------------------+
 | Copyright (c) 2006 Palosanto Solutions S. A.                         |
 +----------------------------------------------------------------------+
 | The contents of this file are subject to the General Public License  |
 | (GPL) Version 2 (the "License"); you may not use this file except in |
 | compliance with the License. You may obtain a copy of the License at |
 | http://www.opensource.org/licenses/gpl-license.php                   |
 |                                                                      |
 | Software distributed under the License is distributed on an "AS IS"  |
 | basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See  |
 | the License for the specific language governing rights and           |
 | limitations under the License.                                       |
 +----------------------------------------------------------------------+
 | The Initial Developer of the Original Code is PaloSanto Solutions    |
 +----------------------------------------------------------------------+
 $Id: paloSantoACL.class.php,v 1.1.1.1 2007/07/06 21:31:55 gcarrillo Exp $ */

class paloUserPlugin_extension extends paloSantoUserPluginBase
{
    function userReport_labels()
    {
        return array(_tr("Extension"));
    }

    function userReport_data($username, $id_user)
    {
        $ext = $this->_pACL->getUserExtension($username);
        if (is_null($ext) || $ext == '')
            $ext = _tr("No extension associated");
        return array(
            htmlentities($ext, ENT_COMPAT, 'UTF-8'),
        );
    }

    function addFormElements($privileged)
    {
        if ($privileged) {
            // --- INICIO AUTO-FILTRO EXTENSIONES LIBRES ---
            $arrData = array(
                '' => _tr("no extension")
            );

            // Obtenemos la extensión actual en caso de que estemos EDITANDO un usuario
            $ext_actual = isset($_POST['extension']) ? $_POST['extension'] : (isset($_GET['extension']) ? $_GET['extension'] : '');

            // Cargar lista de extensiones conocidas desde FreePBX
            $dsn = generarDSNSistema('asteriskuser', 'asterisk');
            $pDBa = new paloDB($dsn);
            $rs = $pDBa->fetchTable('SELECT extension, name FROM users ORDER BY extension', TRUE);
            
            // Nos conectamos a la DB de usuarios
            global $arrConf;
            $pDB_acl = new paloDB($arrConf['issabel_dsn']['acl']);
            $usadas = $pDB_acl->fetchTable("SELECT extension FROM acl_user WHERE extension != '' AND extension IS NOT NULL", true);
            
            $arrUsadas = array();
            if(is_array($usadas)){
                foreach($usadas as $row){
                    $arrUsadas[] = $row['extension'];
                }
            }

            if (is_array($rs)) {
                foreach ($rs as $item) {
                    // Solo la mostramos si no está usada, o si es la extensión del usuario que estamos editando
                    if(!in_array($item['extension'], $arrUsadas) || $item['extension'] == $ext_actual) {
                        $arrData[$item["extension"]] = $item["extension"] . " - " . $item["name"];
                    }
                }
            }
            // --- FIN AUTO-FILTRO ---

            return array(
                "extension"   => array(
                    "LABEL"                  => _tr("Extension"),
                    "REQUIRED"               => "no",
                    "INPUT_TYPE"             => "SELECT",
                    "INPUT_EXTRA_PARAM"      => $arrData,
                    "VALIDATION_TYPE"        => "text",
                    "VALIDATION_EXTRA_PARAM" => ""
                ),
            );
        } else {
            return array(
                "extension"   => array(
                    "LABEL"                  => _tr("Extension"),
                    "REQUIRED"               => "no",
                    "INPUT_TYPE"             => "TEXT",
                    "INPUT_EXTRA_PARAM"      => '',
                    "VALIDATION_TYPE"        => "text",
                    "VALIDATION_EXTRA_PARAM" => "",
                    'EDITABLE'               => 'no',
                ),
            );
        }
    }

    function loadFormEditValues($username, $id_user)
    {
        if (!isset($_POST['extension'])) {
            $_POST['extension'] = $this->_pACL->getUserExtension($username);
        }
    }

    function fetchForm($smarty, $oForm, $local_templates_dir, $pvars)
    {
        $smarty->assign('LBL_EXTENSION_FIELDS', _tr("PBX Profile"));
        return $oForm->fetchForm("$local_templates_dir/new_extension.tpl", '', $pvars);
    }

    function runPostCreateUser($smarty, $username, $id_user)
    {
        $r = $this->_pACL->setUserExtension($username,
            (trim($_POST['extension']) == '') ? NULL : trim($_POST['extension']));
        if (!$r) {
            $smarty->assign(array(
                'mb_title'  =>  'ERROR',
                'mb_message'=>  $this->_pACL->errMsg,
            ));
            return FALSE;
        }

        // --- INICIO AUTO-CREAR AGENTE CALL CENTER ---
        $ext_agente = isset($_POST['extension']) ? trim($_POST['extension']) : '';
        
        // Si se le asignó una extensión válida
        if (!empty($ext_agente) && $ext_agente != "") {
            
            // Leemos las credenciales de base de datos nativas de Issabel
            $amp_conf = parse_ini_file('/etc/amportal.conf');
            $dsnCC = "mysql://".$amp_conf['AMPDBUSER'].":".$amp_conf['AMPDBPASS']."@".$amp_conf['AMPDBHOST']."/call_center";
            $pDB_cc = new paloDB($dsnCC);

            // Validamos si el agente ya existe para no duplicarlo
            $check = $pDB_cc->getFirstRowQuery("SELECT id FROM agent WHERE number = '$ext_agente'", true);
            
            if(!is_array($check) || count($check) == 0) {
                // Obtenemos el nombre del formulario
                $nombre_agente = isset($_POST['description']) ? $_POST['description'] : 'Agente '.$ext_agente; 
                if(empty($nombre_agente)) $nombre_agente = $_POST['name'];
                
                $pass_agente = "1234"; // Por defecto
                $eccp = sha1(uniqid(rand(), true)); // Hash aleatorio seguro para la app ECCP interna

                // Insertamos el agente como PJSIP (estándar de Issabel 5)
                $sql = "INSERT INTO agent (type, number, name, password, estatus, eccp_password) 
                        VALUES ('PJSIP', '$ext_agente', '$nombre_agente', '$pass_agente', 'A', '$eccp')";
                
                $pDB_cc->genQuery($sql);
            } else {
                 // Si el agente existe, lo actualizamos (nombre) por si acaso cambiaron la descripción
                 $nombre_agente = isset($_POST['description']) ? $_POST['description'] : 'Agente '.$ext_agente; 
                 if(empty($nombre_agente)) $nombre_agente = $_POST['name'];
                 $sql = "UPDATE agent SET name = '$nombre_agente' WHERE number = '$ext_agente'";
                 $pDB_cc->genQuery($sql);
            }
        }
        // --- FIN AUTO-CREAR AGENTE CALL CENTER ---

        return TRUE;
    }

    function runPostUpdateUser($smarty, $username, $id_user, $privileged)
    {
        // Sólo el usuario con editany puede cambiar la extensión
        return $privileged ? $this->runPostCreateUser($smarty, $username, $id_user) : TRUE;
    }
}
