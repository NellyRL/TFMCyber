<?php
session_start();

// Usuarios válidos
$usuarios = [
  "ana" => "recetas123",
  "luis" => "cocina456"
];

$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

if (isset($usuarios[$username]) && $usuarios[$username] === $password) {
  $_SESSION['usuario'] = $username;
  header("Location: home.php");
  exit;
} else {
  header("Location: index.html?error=1");
  exit;
}
