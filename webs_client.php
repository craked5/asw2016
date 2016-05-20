<?php
	require_once "lib/nusoap.php";
	$client = new nusoap_client("http://188.166.146.154/webs.php");
	$error = $client->getError();
	$result = $client->call("valorActualDoItem", 1);
	//handle errors
	if ($client->fault) {
		//check faults
		echo "<h2>$result</h2>"
	} else {
		$error = $client->getError();
		//handle errors
		echo "<h2>$result</h2>";
	} 
?>