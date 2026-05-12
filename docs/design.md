# Sistema de diseño — AMAZING 2026

## Concepto

> Un laberinto de 1978 servido en una terminal de 2026: tinta de fósforo
> sobre cristal CRT, con la respiración de las paredes en cada tecla.

Fusión moderna-retro respetando la estética TTY del original: nada de
imitar Windows 11; honramos al PC IBM 5150 con monitor MDA verde, pero
con el confort de Textual y Unicode.

## Paleta

Inspirada en monitores de fósforo verde (P1) de los 70-80, con dos
acentos cálidos para la retroalimentación del jugador.

| Token | Hex | Nombre | Rol |
| --- | --- | --- | --- |
| `--bg` | `#0a1410` | "midnight green" | fondo principal del CRT apagado |
| `--bg-elev` | `#0f1f18` | "midnight green +1" | panels, tarjetas |
| `--primary` | `#33ff66` | "phosphor" | paredes, texto principal |
| `--primary-dim` | `#1d8a39` | "phosphor dim" | paredes lejanas, separadores |
| `--accent` | `#ffb454` | "amber blip" | jugador, énfasis interactivo |
| `--success` | `#7df0a0` | "verdant glow" | salida descubierta, victoria |
| `--warning` | `#ffd166` | "warning beacon" | avisos no críticos |
| `--error` | `#ef476f` | "error pulse" | errores y muerte de partida |
| `--muted` | `#3a5a48` | "moss" | texto secundario, ayudas |

Contraste comprobado WCAG AA para `--primary` y `--accent` sobre `--bg`
(>4.5:1).

Modo claro alternativo (tecla `t` en la TUI): paleta sepia sobre papel
crema, que homenajea los listados impresos del libro de Ahl. Documentado
abajo en "Variantes".

### Variantes

- **Phosphor (default)**: descrita arriba.
- **Paper**: `--bg #faf3e0`, `--primary #2b2118`, `--accent #c1463a`.
  Activable con `t`.
- **Amber**: P3-amber CRT, `--primary #ffb000`, `--accent #ff5722`.
  Activable con `T`.

## Tipografía

| Uso | Familia | Tamaño / Peso |
| --- | --- | --- |
| Texto general | `JetBrains Mono`, fallback `Menlo`, `Consolas`, `monospace` | 14px / 400 |
| Cabeceras | `IBM Plex Mono Bold` o `JetBrains Mono Bold` | 16-22px / 700 |
| Renderizado del laberinto | misma mono que el general | 14px / 400, line-height 1.0 |
| Splash | `Press Start 2P` si disponible, si no `IBM Plex Mono Bold` | 24px |

Todo monospace estricto. Los caracteres del laberinto se calculan para
ser un grid de 2 columnas terminal × 1 fila (cada celda del laberinto
mide `3 × 2` celdas de terminal).

## Espaciado

Sistema 4-px (en CSS de Textual: `1` = 1 cell terminal ~= 8-10 px):

| Token | Valor | Uso |
| --- | --- | --- |
| `xs` | 1 | gaps internos de widget |
| `sm` | 2 | padding interno de panels |
| `md` | 4 | separación entre paneles |
| `lg` | 8 | márgenes de screens |
| `xl` | 16 | splash, modales |

## Iconografía

ASCII + Unicode box-drawing. No usamos Nerd Fonts (no asumimos
instalación). Mapa de caracteres canónicos:

| Símbolo | Significado | Modo legacy | Modo unicode |
| --- | --- | --- | --- |
| Esquina | nodo de pared | `.` / `:` | `+` o `┼` |
| Muro horizontal | pared horizontal | `--` | `──` |
| Muro vertical | pared vertical | `I` | `│` |
| Hueco horizontal | pasillo abierto | `  ` | `  ` |
| Hueco vertical | pasillo abierto | ` ` | ` ` |
| Jugador | posición del jugador | `*` | `◉` |
| Entrada | flecha entrada | `v` | `▼` |
| Salida | flecha salida | `^` | `▲` |
| Rastro | celdas visitadas | `·` | `·` |

`--unicode` en la CLI activa la columna derecha; por defecto, modo
legacy fiel al listado del 78.

## Estados clave

1. **Splash** (1.5 s): cabecera "AMAZING PROGRAM / CREATIVE COMPUTING"
   con un efecto de escritura mecánica, fondo CRT respirando.
2. **Configurador**: tres `Input` (ancho, alto, semilla opcional), un
   `Switch` para Unicode, botón "GENERAR" con foco automático.
3. **Generación**: laberinto materializándose celda a celda con
   animación opcional (`--animate`), tiempo ~250 ms para 10×10.
4. **Juego**: el laberinto a pantalla completa, footer con teclas, panel
   lateral con cronómetro, contador de pasos y mini-mapa.
5. **Victoria**: el camino correcto se ilumina en `--success`, modal con
   estadísticas y opción "OTRA PARTIDA / SALIR".
6. **Carga / error**: mensaje breve sobre `--bg`, color `--error` con
   bordes ASCII estilo `+-----+`.

## Microinteracciones

- **Cada movimiento**: el carácter del jugador parpadea 1 frame (40 ms)
  en `--accent` brillante antes de asentarse. Sensación de "click".
- **Pared bloqueada**: el muro afectado tiembla 2 cells (3 frames) y
  destella `--error`. El jugador no avanza.
- **Cerca de la salida** (radio Manhattan ≤ 3): la salida pulsa cada
  800 ms en `--success`.
- **Splash**: el subtítulo "MORRISTOWN, NEW JERSEY" escribe a 60 ms/char,
  como en un Teletipo ASR-33.

## Accesibilidad

- Navegación 100 % teclado: `flechas` o `wasd`/`hjkl` mover, `q` salir,
  `r` reiniciar, `t`/`T` cambiar tema, `?` ayuda.
- No depender solo del color: el jugador es `*`/`◉`, la salida es `^`/`▲`.
  Ambos distinguibles en blanco y negro.
- Modo claro `Paper` para usuarios sensibles a esquemas oscuros.
- `--no-animate` desactiva todas las transiciones.

## El toque distintivo

**Estela de fósforo** (`--phosphor-trail`, on por defecto): cada celda
visitada por el jugador deja un punto `·` que se desvanece de `--primary`
a `--primary-dim` a transparente a lo largo de 2 segundos. Es sutil,
delicioso, y le da al laberinto la sensación de respirar bajo tus pies.

Para gente puritana: `--no-trail` lo desactiva.

## Estados con previsualización

### Splash (legacy mode)

```
                            AMAZING PROGRAM
               CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY



               press [enter] to begin   q to quit
```

### Laberinto (legacy mode, 10×6)

```
.--.  .--.--.--.--.--.--.--.--.
I     I                 I     I
:  :--:--:--:  :--:--:  :  :  .
I           I        I     I  I
:--:--:--:  :  :--:  :--:--:  .
I  I        I     I  *     I  I
:  :  :--:--:--:--:--:--:  :  .
I     I                 I  I  I
:  :--:--:  :  :--:--:  :  :  .
I        I  I  I     I     I  I
:--:--:  :--:  :  :--:--:--:  .
I              I              I
:  :--:--:--:--:--:--:--:--:--.
                              ▲
```
