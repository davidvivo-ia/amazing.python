# Postmortem — AMAZING 2026

Reescribir 108 líneas de BASIC de 1978 en Python 2026 es como restaurar
un mueble del XIX con herramientas modernas: lo que tarda no es la
restauración, es decidir qué dejar tal cual y qué actualizar.

## Qué se ganó

- **Legibilidad**: el flujo del programa es ahora un solo bucle `while`
  con pila y cuatro acciones (mover NESO). El original tenía 55 `GOTO`s
  y un árbol de decisión escrito a mano de 250 líneas.
- **Testabilidad**: 86 tests, propiedades con `hypothesis` que barren
  miles de semillas, dominio puro sin I/O.
- **Robustez**: tres bugs latentes del original corregidos (validación
  de `1×N`, fallback de salida, sesgo de escaneo).
- **Interactividad real**: pasamos de un generador (escupir un
  laberinto estático y terminar) a un juego (navegarlo en tiempo real
  con cronómetro, estadísticas y temas visuales).
- **Reproducibilidad**: `--seed` garantiza el mismo laberinto entre
  ejecuciones, algo que Hauber dejó al azar inicial de `RND` sin
  `RANDOMIZE`.

## Qué se perdió

- **Densidad**: el listado original cabe en una pantalla de Teletipo.
  Nuestra versión son 23 archivos Python y 10 de documentación. Es el
  coste de la modularidad y la testabilidad — y aun así, sigue siendo
  un proyecto modesto.
- **El olor a 1978**: la estética la respeta una opción (`legacy`,
  `phosphor`), pero ya no la *es*. Quien busque la experiencia íntegra
  puede correr el `legacy/ibm-pc/amazing.bas` en un intérprete BASIC
  contemporáneo y comparar.
- **La sorpresa**: el original te imprimía el laberinto y se acababa.
  Nuestra versión, con su pantalla de splash y sus animaciones,
  performa más. Quien busque la elegancia austera del listado puede
  usar `amazing print`, que vuelca y termina como el primer día.

## Qué dice del oficio en 40 años

En 1978, Hauber tenía 4 KB de RAM, un intérprete sin estructuras de
datos y un libro que le pagaba por línea de código. Su solución es
elegante a su manera: un algoritmo correcto, escrito con las únicas
herramientas que la máquina toleraba. El programa "funciona", que es
todo lo que se le podía pedir.

En 2026, una sola línea de `pyproject.toml` arrastra 40 dependencias
transitivas y un intérprete de 30 MB. A cambio, podemos escribir
`set[Cell]` y olvidarnos. La asimetría es brutal: lo que les costó a
ellos un mes de paciencia, a nosotros nos cuesta cinco minutos y la
posibilidad de equivocarnos en abstracciones que ellos nunca pudieron
permitirse.

Pero algo ha cambiado para mejor que no es trivial: la **lectura**. El
listado de Hauber se entiende en una tarde si se conoce BASIC; el
nuestro se entiende en una tarde por cualquiera que lea Python.
Mantener el código a 47 años vista es responsabilidad nuestra, no del
lenguaje. Por eso este proyecto se llama *amazing.python* y no
*amazing.basic-translated*: no es traducción, es traslación de un
artefacto bonito a otro tiempo, con la esperanza de que dure otros
cuarenta años.

Y si no dura, al menos quedó el `legacy/ibm-pc/amazing.bas` en su
sitio. Como debe ser.
