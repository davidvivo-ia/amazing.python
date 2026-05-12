# ADR 0004 — Estética: fósforo CRT con homenaje tipográfico

- Estado: Aceptada
- Fecha: 2026-05-12

## Contexto

`docs/design.md` define los detalles; este ADR registra la decisión
fundacional: ¿qué *vibe* tiene AMAZING 2026?

## Opciones

1. **Estética moderna pura**: temas claros tipo Notion, sans-serif,
   colores corporativos. Mata el alma del original.
2. **Cosplay retro**: imitar exactamente la salida de un ASR-33 con
   tipografía pixelada y errores artificiales. Cute, agotador.
3. **Fusión moderna-retro** sobre paleta de fósforo verde, con
   tipografía monospace contemporánea (JetBrains Mono) y
   microinteracciones sutiles (phosphor trail).

## Decisión

Opción 3. La estética debe ser **reconociblemente retro** al primer
vistazo y **agradable** sin esfuerzo en uso prolongado. Paleta de
fósforo verde + acento ámbar + trailing fade. Tres variantes para no
forzar (`phosphor`, `paper`, `amber`).

## Consecuencias

- `assets/tui.tcss` define tres temas como variantes de CSS de Textual.
- El "phosphor trail" se implementa con un decorador de timer en
  Textual; coste insignificante a 60fps simulados (Textual va a 30fps
  por defecto).
- Riesgo de que la animación moleste en sesiones largas: mitigado con
  `--no-trail` y `--no-animate`.
- En modo `print` (one-shot a stdout), nada de esto aplica: salida fiel
  ASCII 1978.
