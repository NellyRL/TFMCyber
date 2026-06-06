<!--
  AUTHOR: Nelly Ramos
  Local reading/compose/search page for the data-leakage scenario.

  Gives TTS/dyslexia extensions real material (long selectable prose, headings,
  an editable area, a search box). Canary slots are filled at runtime by
  src/capture/web_actions.py so only the URL carries the url_token; the rest are
  injected into the DOM/inputs to keep leak channels separated.
-->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lectura accesible</title>
  <style>
    body {
      font-family: 'Georgia', serif;
      margin: 0;
      padding: 40px;
      background: #fafafa;
      color: #222;
      line-height: 1.7;
    }
    main { max-width: 760px; margin: 0 auto; }
    h1 { font-size: 2.4em; color: #2c3e50; }
    h2 { font-size: 1.5em; color: #34495e; margin-top: 1.6em; }
    p { font-size: 1.15em; margin: 0 0 1.1em 0; }
    .tools { margin-top: 2.5em; padding-top: 1.5em; border-top: 1px solid #ddd; }
    textarea { width: 100%; height: 120px; font-size: 1.05em; padding: 10px; box-sizing: border-box; }
    input[type="text"] { font-size: 1.05em; padding: 8px; width: 70%; }
    label { display: block; margin: 1.2em 0 0.4em 0; font-weight: bold; }
    .canary { color: #777; font-size: 0.95em; }
  </style>
</head>
<body>
  <main>
    <h1>Lectura accesible y tecnologías de apoyo</h1>

    <article id="reader-text">
      <p>La lectura digital se ha convertido en una actividad cotidiana para millones de personas.
      Los textos que consumimos a diario aparecen en pantallas de distintos tamaños, con tipografías
      y contrastes muy variados. Para muchas personas, ajustar estos elementos no es una cuestión de
      comodidad, sino de acceso real a la información.</p>

      <h2>Por qué importa la legibilidad</h2>
      <p>Una buena legibilidad reduce el esfuerzo necesario para comprender un texto. El tamaño de la
      letra, el espaciado entre líneas y la separación entre párrafos influyen directamente en la
      velocidad de lectura y en la fatiga visual. Cuando estos factores se cuidan, el contenido se
      vuelve más accesible para un público amplio.</p>

      <h2>Tecnologías de apoyo a la lectura</h2>
      <p>Las herramientas de lectura en voz alta convierten el texto en audio, permitiendo seguir un
      documento sin mirar la pantalla de forma continua. Las ayudas para la dislexia, por su parte,
      reestructuran la presentación del texto: cambian la fuente, aumentan el interlineado o resaltan
      sílabas para facilitar el reconocimiento de palabras.</p>

      <p>Estas tecnologías procesan el contenido de la página para poder transformarlo. Comprender
      qué datos leen y a dónde los envían es esencial para evaluar su impacto en la privacidad,
      especialmente cuando las usan personas que dependen de ellas a diario.</p>

      <p class="canary" id="content-canary"></p>
    </article>

    <section class="tools">
      <label for="compose">Escribe una nota sobre la lectura:</label>
      <textarea id="compose" name="compose" placeholder="Tus notas..."></textarea>

      <form id="search-form" onsubmit="return false;">
        <label for="search">Buscar en esta página:</label>
        <input id="search" name="search" type="text" placeholder="Buscar...">
        <button type="submit">Buscar</button>
      </form>

      <input id="auth-canary" type="hidden" value="">
    </section>
  </main>
</body>
</html>
