<?php
session_start();
if (!isset($_SESSION['usuario'])) {
  header("Location: index.html");
  exit;
}

$recetas = [
  ["nombre" => "Ensalada de Quinoa", "tipo" => "Saludable"],
  ["nombre" => "Tostadas Francesas", "tipo" => "Desayuno"],
  ["nombre" => "Wrap de Pollo", "tipo" => "Almuerzo"],
  ["nombre" => "Sopa Thai", "tipo" => "Cena"],
  ["nombre" => "Smoothie de Mango", "tipo" => "Bebida"]
];

$tipoFiltro = $_GET['tipo'] ?? '';
$recetasFiltradas = $tipoFiltro ? array_filter($recetas, fn($r) => $r['tipo'] === $tipoFiltro) : $recetas;
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recetario Elegante</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="home-container">
  <div class="top-bar">
  <h1>Bienvenido, <?php echo htmlspecialchars($_SESSION['usuario']); ?>!</h1>
  <a class="logout" href="logout.php">Cerrar sesión</a>
</div>
    <form method="get" class="filtro">
      <label for="tipo">Filtrar por tipo:</label>
      <select name="tipo" id="tipo" onchange="this.form.submit()">
        <option value="">Todos</option>
        <option value="Desayuno" <?= $tipoFiltro==='Desayuno'?'selected':'' ?>>Desayuno</option>
        <option value="Almuerzo" <?= $tipoFiltro==='Almuerzo'?'selected':'' ?>>Almuerzo</option>
        <option value="Cena" <?= $tipoFiltro==='Cena'?'selected':'' ?>>Cena</option>
        <option value="Saludable" <?= $tipoFiltro==='Saludable'?'selected':'' ?>>Saludable</option>
        <option value="Bebida" <?= $tipoFiltro==='Bebida'?'selected':'' ?>>Bebida</option>
      </select>
    </form>
    <div class="recetas-grid">
  <?php foreach ($recetasFiltradas as $receta): ?>
    <div class="receta-card">
      <h3><?= htmlspecialchars($receta['nombre']) ?></h3>
      <p><?= $receta['tipo'] ?></p>
    </div>
  <?php endforeach; ?>
</div>

  </div>
</body>
</html>