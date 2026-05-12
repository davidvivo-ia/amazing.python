# ADR 0001 — Capa de presentación: Textual (TUI)

- Estado: Aceptada
- Fecha: 2026-05-12

## Contexto

El programa original es TTY puro: `PRINT` + `INPUT`, sin colores ni
semigráficos. La reinterpretación 2026 puede ir desde un script CLI
clásico hasta un juego gráfico con pygame.

## Opciones consideradas

1. **CLI puro con `typer` + `rich`**. Imprime el laberinto en una
   pasada; sin interactividad real. Mínima fricción, máxima fidelidad.
2. **TUI con `textual`**. Pantalla completa, widgets, CSS, navegación
   con teclado.
3. **Gráfico con `pygame-ce`**. Sprites, sonido AY-3-8912 sintetizado,
   scroll. Atractivo, pero traiciona la naturaleza TTY del original.

## Decisión

**Textual**. El original es TTY → respetamos la naturaleza textual. Pero
queremos convertirlo en *juego*, no en *generador*, y eso pide
interactividad: mover al jugador con flechas, ver cronómetro, mini-mapa,
estados de victoria. Textual da todo eso sin salir del terminal.

`CLAUDE.md` lo respalda explícitamente: "Si el original usa caracteres
semigráficos (...) → TUI con Textual". `.--.--.` es exactamente eso.

## Consecuencias

- Bonito y portable: corre en cualquier terminal moderno.
- Permite efectos sutiles (phosphor trail, pulse de salida) sin entrar
  en territorio de gráficos.
- Dependencia añadida: `textual >= 0.80` (no es ligera, pero estable).
- Tests: la propia infra de Textual ofrece `App.run_test()` para
  pruebas E2E sin abrir terminal.
- Limita la presentación a monoespaciado y a la rejilla de la terminal;
  el render del laberinto se diseñó con esa restricción en mente.
- También mantenemos un comando `amazing print` que vuelca el laberinto
  en una pasada a stdout (modo "fidelidad 1978"), útil para piping.
