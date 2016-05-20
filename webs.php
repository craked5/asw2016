<?php
require_once "lib/nusoap.php";

function valorActualDoItem($id)  {
	$url = 'http://163.172.132.51/php/valorActualDoItem';
	$ch = curl_init($url);

	$data = array(
	    'userID'	=> $id,
	);

	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

	$response = curl_exec($ch);
	curl_close($ch);

	echo $response;
	return $response;
}

function licitaItem($id, $valor, $username, $password) {
	$url = 'http://163.172.132.51/php/licitaItem';
	$ch = curl_init($url);

	$data = array(
	    'userID'	=> $id,
	    'valor'	=> $valor,
	    'username'	=> $username,
	    'password' => $password,
	);

	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

	$response = curl_exec($ch);
	curl_close($ch);

	if ($response == "Aceite") {
		$s= "Aceite";
	} elseif $response == "Nao Aceite" {
		$s= "Nao Aceite";
	} else {
		$s="Terminado";
	}

	echo $s;
	return $s;
}

$server = new soap_server();
$server->configureWSDL('items', 'http://188.166.146.154/items');

$server->register("valorActualDoItem", // nome metodo
	array('id' => 'xsd:decimal'), // input
	array('return' => 'xsd:string'), // output 
	'http://188.166.146.154/items', // namespace
	'http://188.166.146.154/items#valorActualDoItem', // SOAPAction
	'rpc', // estilo
	'encoded' // uso
);

$server->register("licitaItem", // nome metodo
	array('id' => 'xsd:decimal', 'valor' => 'xsd:decimal', 'username' => 'xsd:string', 'password' => 'xsd:string'), // input
	array('return' => 'xsd:string'), // output 
	'http://188.166.146.154/items', // namespace
	'http://188.166.146.154/items#licitaItem', // SOAPAction
	'rpc', // estilo
	'encoded' // uso
);

$HTTP_RAW_POST_DATA = isset($HTTP_RAW_POST_DATA) ? $HTTP_RAW_POST_DATA : '';
$server->service($HTTP_RAW_POST_DATA);

?>