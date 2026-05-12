# TODO

Cosas que sabemos que faltan o que mejoraríamos en futuras versiones.

## v1.1 (próxima minor)

1. **`--legacy-bias` flag**: implementar el algoritmo hunt-and-kill
   original de Hauber 1978 como opción opcional, para reproducir el
   sesgo direccional NW→SE del listado. Útil como modo "fidelidad
   arqueológica". Esqueleto previsto en
   `amazing.application.carve_maze.CarveAlgorithm`.
2. **Estela de fósforo animada**: el efecto fade-out de las celdas
   visitadas descrito en `docs/design.md` aún no está implementado;
   ahora mismo la estela es estática. Plan: usar `Timer` de Textual
   para regenerar el render cada 200 ms con un canal alpha decreciente.
3. **Récords visibles en la TUI**: persistimos los récords en JSON pero
   no los mostramos al final de partida. Añadir modal post-victoria con
   top-10 por dimensión.
4. **Sonido**: un beep sintetizado con `numpy` al ganar y al chocar
   contra una pared, opcional con `--sound`. Homenaje al PC-speaker.

## Limitaciones conocidas v1.0

- La TUI usa `App.bell()` para victoria, que en algunos terminales no
  hace nada audible. Hay que probar en iTerm, Windows Terminal y Linux
  console.
- No hay todavía un GIF en el README porque la generación con `textual`
  fuera de TTY interactivo da problemas. Sustituido por un bloque ASCII
  estático.

## Ideas que descartamos para v1.0

- **Multijugador local en split-screen**: bonito, pero rompe el espíritu
  introspectivo del original.
- **Generación 3D / isométrica**: queda fuera del concepto TTY.
- **Editor de laberintos**: ahora mismo no hay caso de uso claro.
