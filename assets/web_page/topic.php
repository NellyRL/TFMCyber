<?php
// AUTHOR: Nelly Ramos
// Generic distinct page used to build a multi-page browsing history.
// The history canary token travels in the URL query (?ref=...) ONLY; it is never
// echoed into the body, so a "history/URL leak" stays a separate channel from the
// page-content channel. Only the non-secret topic slug is rendered.
$topic = isset($_GET['t']) ? preg_replace('/[^a-zA-Z0-9 ]/', '', $_GET['t']) : 'general';
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tema: <?php echo htmlspecialchars($topic); ?></title>
  <style>
    body { font-family: 'Georgia', serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #222; line-height: 1.7; }
    h1 { color: #2c3e50; text-transform: capitalize; }
    p { font-size: 1.12em; }
  </style>
</head>
<body>
  <main id="reader-text">
    <h1><?php echo htmlspecialchars($topic); ?></h1>
    <p>Esta es una página de ejemplo sobre <strong><?php echo htmlspecialchars($topic); ?></strong>.
    Forma parte de una secuencia de navegación utilizada para comprobar si una extensión recopila el
    historial de páginas visitadas. El contenido es neutro y está pensado únicamente para que la
    extensión tenga texto que procesar mientras se registra la navegación.</p>
    <p>Las personas que usan tecnologías de apoyo navegan a diario por temas muy distintos. Observar si
    esa secuencia de páginas se transmite a terceros es clave para evaluar la privacidad.</p>
  </main>
</body>
</html>
