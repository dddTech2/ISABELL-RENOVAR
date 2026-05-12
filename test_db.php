<?php
require_once "libs/paloSantoDB.class.php";
$dsn = "mysql://asterisk:asterisk@localhost/asterisk";
$db = new paloDB($dsn);
print_r($db->fetchTable("SHOW TABLES LIKE 'ps_%'"));
print_r($db->fetchTable("SELECT * FROM ps_auths LIMIT 1"));
print_r($db->fetchTable("SELECT data FROM sip WHERE keyword='secret' LIMIT 1"));
