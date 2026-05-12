# Análisis del programa original

Archivo de referencia: `legacy/ibm-pc/amazing.bas` (108 líneas, 1978).

## 1. Encuadre

| Campo | Valor |
| --- | --- |
| Nombre | AMAZING PROGRAM |
| Autor | Jack Hauber (Windsor, CT) |
| Editor | Creative Computing — *BASIC Computer Games* (Ahl, 1978) |
| Lenguaje | BASIC interpretado, dialecto Microsoft (BASICA / GW-BASIC / Vintage BASIC) |
| Plataforma canónica | IBM PC; portable a Spectrum, C64, Apple II, MSX |
| Año | 1978 (publicación) — la versión original venía de listados de Creative Computing de los primeros 70 |
| Tamaño | 108 líneas, ~2 KB |
| Modo | TTY puro: `PRINT` y `INPUT`. No usa color, sonido ni semigráficos. |
| Sinopsis | Genera un laberinto rectangular `H × V` perfecto (un único camino entre dos cualesquiera celdas), con una entrada en el borde superior y una salida en el borde inferior, y lo imprime con caracteres ASCII (`.`, `-`, `:`, `I`). |

### Lectura crítica

Pieza ejemplar de la primera ola de "computer recreations" del libro de
Ahl: cero IO interactiva más allá de pedir dimensiones, todo el peso
está en el algoritmo. El listado, sin embargo, es **brutal de leer**:
108 líneas, **55 GOTOs**, cero subrutinas (`GOSUB`), variables de una
letra, y un núcleo de decisión que es esencialmente un árbol de
decisión desplegado a mano con `IF ... GOTO`. Es un caso de estudio de
cómo se programaba un backtracker antes de tener pilas, recursión o
estructuras de datos decentes.

El algoritmo subyacente es un **hunt-and-kill** (Walter Pullen lo
formalizó así dos décadas después), variante perezosa del recursive
backtracker que cabe en una memoria sin pila: cuando una celda queda
sin vecinos, hace un *scan* lineal del tablero para encontrar la
siguiente celda visitada con vecinos libres y continúa desde ahí.

## 2. Arqueología

### 2.1 Inventario de variables

| Variable | Tipo | Significado |
| --- | --- | --- |
| `H` | int 1..n | Ancho del laberinto (columnas). Entrada de usuario. |
| `V` | int 1..n | Alto / "longitud" (filas). Entrada de usuario. |
| `W(H,V)` | int[][] | Matriz de "orden de visita": 0 = no visitada, `n` = visitada en el paso `n`. Equivale a un set de visitadas con metadato. |
| `V(H,V)` | int[][] | Matriz de paredes: 0 = ambas paredes (derecha e inferior) en pie; 1 = pared inferior abierta; 2 = pared derecha abierta; 3 = ambas abiertas. Encoding bit-a-bit camuflado. |
| `C` | int | Contador de celdas visitadas. Termina cuando `C = H*V + 1`. |
| `R`, `S` | int | Cursor de talla (columna, fila) actualmente bajo examen. |
| `X` | int | Reutilizada para dos cosas: columna de entrada en línea 160, y resultado del dado `INT(RND*N+1)` en el dispatch. |
| `Q` | flag 0/1 | "He intentado salir por abajo en esta visita". Sirve para diferir la creación de la salida hasta confirmar que no había otra opción. |
| `Z` | flag 0/1 | "La salida ya está creada". Evita crear más de una salida. |
| `I`, `J` | int | Índices de bucles `FOR` puramente locales (impresión). |

### 2.2 Inventario de "subrutinas" (etiquetadas por nosotros)

El programa no usa `GOSUB`. Identificamos seis bloques funcionales
saltando a número de línea:

| Etiqueta | Líneas | Función |
| --- | --- | --- |
| `INTRO` | 10–30 | Cabecera "AMAZING PROGRAM / CREATIVE COMPUTING". |
| `INPUT_DIMS` | 100–104 | Lee `H,V`. Rechaza el caso `H=1 AND V=1`. **[BUG]** ver §2.5. |
| `INIT` | 110–195 | Reserva matrices, elige columna de entrada `X`, imprime el borde superior con la apertura, marca la celda de entrada como visitada. |
| `SCAN` | 200–250 | Busca la siguiente celda visitada con vecinos libres, recorriendo el tablero en orden row-major con `wrap-around`. |
| `DECIDE` | 260–780 | Árbol de decisión: examina los cuatro vecinos (izq, arr, der, abj), cuenta cuántos están libres, tira `RND` y dispara `MOVE_*`. Aquí está enterrada la lógica de salida por abajo. |
| `MOVE_*` | 790–905 | Cuatro bloques de "mover y abrir pared": izquierda (790), arriba (820), derecha (860), abajo (910). El bloque "abajo" además gestiona la creación de la salida (960–980). |
| `RENDER` | 1010–1073 | Imprime el laberinto leyendo `V(I,J)`. |

### 2.3 Grafo de flujo (resumen ASCII)

```
INTRO ─► INPUT_DIMS ─► INIT ─┐
                              ▼
       ┌────────────────── SCAN ◄──────────┐
       │                                    │
       ▼                                    │
   DECIDE ── (4 vecinos libres / parciales) │
       │                                    │
       ├──► MOVE_LEFT  ──► [C++; check end] ┤
       ├──► MOVE_UP    ──► [C++; check end] ┤
       ├──► MOVE_RIGHT ──► [C++; check end] ┤
       └──► MOVE_DOWN  ──► [C++; check end] ┤
                                             │
                                       C == H*V+1?
                                             │
                                             ▼
                                          RENDER ─► END
```

### 2.4 Codificación de paredes en `V(I,J)`

| Valor | Pared derecha | Pared inferior |
| --- | --- | --- |
| 0 | en pie | en pie |
| 1 | en pie | abierta |
| 2 | abierta | en pie |
| 3 | abierta | abierta |

Es una codificación bit-a-bit pero no se manipula con `AND`/`OR` (BASIC
del 78 no los tenía portables): se actualiza con `IF V=0 THEN V=2 ELSE
V=3` y simétrico para inferior. La modernización a `IntFlag` es
trivial.

### 2.5 Bugs y rarezas detectadas

#### BUG-1: Validación de dimensiones rota

Línea 102: `IF H<>1 AND V<>1 THEN 110`. La intención evidente es
**rechazar `H=1 AND V=1`** (un laberinto de una sola celda no tiene
sentido). La condición correcta sería `IF H<>1 OR V<>1 THEN 110`
(continuar si no estamos en el caso degenerado). Tal como está, el
programa rechaza también `H=1, V=5` o `H=5, V=1`, que son laberintos
perfectamente válidos (un único corredor recto).

**Corrección en el port 2026**: aceptar cualquier `H>=1, V>=1` salvo
`H=1 AND V=1`. Se documenta en `CHANGELOG.md` bajo "Bugs corregidos".

#### BUG-2: Sesgo del scan lineal

Cuando una celda queda sin vecinos, el algoritmo escanea
row-major `(R+1,S) → (1,S+1) → (1,1) → ...` buscando la siguiente
visitada con vecinos. Esto sesga los laberintos: los corredores tienden
a ser más largos en la diagonal NW→SE. No es un bug funcional (todo el
laberinto se rellena), pero produce mazes visualmente reconocibles.

**Tratamiento en el port 2026**: lo conservamos en modo `--legacy-bias`
para fidelidad histórica, pero el modo por defecto usa un recursive
backtracker con stack que produce mazes estadísticamente más
uniformes. Documentado como [LICENCIA CREATIVA] en `CHANGELOG.md`.

#### BUG-3: Re-entrada infinita en grids 1×N

Combinado con BUG-1, en grids 1×N (que tras corregir BUG-1 se aceptan)
el bloque `DECIDE` puede no crear nunca la salida por abajo si N=1.
Resuelto en el port con un fallback explícito ("si al terminar no hay
salida, ábrela bajo la última celda").

#### Rareza: `GOTO 830` desde 695

La línea 695 hace `Q=1:GOTO 830`, pero `830` está en mitad de
`MOVE_UP`. Es un salto que **omite** la línea 820 (`W(R,S-1)=C`),
saltando directamente al incremento del contador y la apertura. Es
**intencionado**: se llega ahí cuando la única opción era "bajar" en la
última fila sin haber abierto la salida todavía; ese caso fuerza `Q=1`
y delega el manejo en 910–980. Es feo, pero funciona. En el port
desaparece: la lógica equivalente es "si no hay vecinos libres y estás
en la fila inferior y aún no hay salida, márcala aquí".

### 2.6 Generación de números aleatorios

El programa usa `RND(1)` (Microsoft BASIC) sin `RANDOMIZE`. Esto
significa que **dos ejecuciones consecutivas producen el mismo
laberinto** salvo que el usuario ejecute `RANDOMIZE TIMER` manualmente.
Era idiomático en el 78: te permitía reproducir laberintos. En el port
2026 se traduce a `random.Random` inyectable con `--seed`.

## 3. Conclusión arqueológica

AMAZING es un ejercicio precioso de **algoritmo elegante atrapado en un
lenguaje incapaz**. El backtracker con scan está bien pensado; el
problema es BASIC del 78, no Hauber. Reescrito con una pila y enums
cabe en 60 líneas legibles, conserva las mismas garantías topológicas
(laberinto perfecto, una entrada arriba, una salida abajo) y elimina
de paso tres bugs documentados.

El "alma" que conservamos:

1. La interfaz (pedir `H, V`, generar, renderizar como ASCII art).
2. El estilo del render (`.--.`, `:  :`, `I`).
3. La idea de **una sola entrada arriba y una sola salida abajo**.
4. La cabecera "AMAZING PROGRAM / CREATIVE COMPUTING".

Lo que reimaginamos:

1. El algoritmo (backtracker con pila explícita, no hunt-and-kill).
2. La interactividad (de generador a juego: el jugador navega).
3. El render (Textual TUI con colores, tema retro CRT opcional).
4. La estructura (capas, tests, tipos, RNG inyectable).
