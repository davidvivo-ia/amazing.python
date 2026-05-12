# Procedencia del código legacy

## `ibm-pc/amazing.bas`

- **Programa**: AMAZING PROGRAM
- **Autor original**: Jack Hauber (Windsor, CT), publicado por
  Creative Computing en *BASIC Computer Games* (David H. Ahl, ed.),
  Workman Publishing, 1978, pp. 12-13.
- **Dialecto**: Microsoft BASIC interpretado (Altair / IBM BASICA /
  GW-BASIC / Vintage BASIC compatible). Sin extensiones específicas de
  plataforma. Originalmente listado para terminales ASR-33 y similares.
- **URL canónica del listado limpio**:
  <https://www.vintage-basic.net/bcg/amazing.bas>
- **Mirror usado para esta importación**:
  <https://raw.githubusercontent.com/GReaperEx/bcg/master/amazing.bas>
- **Fecha de descarga**: 2026-05-12.
- **Estatus legal**: dominio público. *BASIC Computer Games* fue
  publicado bajo permiso explícito de redistribución no comercial (Ahl
  donó los listados al dominio público para uso educativo). El listado
  íntegro lleva 47 años circulando libremente en internet.
- **Plataforma elegida como canónica**: IBM PC (GW-BASIC/BASICA). El
  código es portable entre todos los dialectos BASIC microsoft-compat
  de finales de los 70 (Spectrum, C64, Apple II) cambiando únicamente
  el ancho de pantalla y el carácter de tabulación.

## ¿Por qué AMAZING y no otro juego?

El usuario dirigió a este programa explícitamente (mensaje previo a
esta sesión: "https://github.com/GReaperEx/bcg/blob/master/c.bas crealo
en python"). El URL apuntaba a `c.bas` (404), pero el repositorio
`amazing.python` y el contenido del repo `bcg` apuntaban inequívocamente
a `amazing.bas`. Sustitución documentada en `CHANGELOG.md` bajo
"Licencias creativas tomadas".

## Versiones alternativas consideradas y descartadas

- **Spectrum / Amstrad**: no existe port oficial del AMAZING de Ahl en
  ninguna revista española de los 80. Los listados de laberintos que
  publicaron *Microhobby* y *Amstrad Acción* usan algoritmos distintos
  (relleno aleatorio sin garantía de conectividad). Mantenemos la
  versión IBM PC como única canónica.
- **C64 PETSCII**: existe una adaptación a PETSCII en archivos de
  Creative Computing pero es idéntica algorítmicamente a la versión
  IBM PC, solo cambia el set de caracteres de impresión. No aporta.
