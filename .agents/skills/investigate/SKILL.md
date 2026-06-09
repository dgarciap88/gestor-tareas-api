---
name: investigate
description: Investiga el código y produce un informe con referencias exactas.
allowed-tools: Read, Grep, ListDir
triggers: ["user"]
argument-hint: <tema o área a investigar>
---

## Objetivo

Investigar el tema o área indicada por el usuario y generar un informe
estructurado con referencias exactas al código fuente (archivo y línea).

## Pasos

1. **Identificar el alcance**: lee el argumento proporcionado por el usuario
   para determinar qué área del código investigar.
2. **Explorar la estructura**: usa `ListDir` para entender la organización
   de archivos y carpetas relevantes.
3. **Buscar referencias**: usa `Grep` para localizar símbolos, patrones o
   palabras clave relacionadas con el tema.
4. **Leer el código**: usa `Read` para examinar los archivos identificados
   y comprender la lógica en detalle.
5. **Documentar hallazgos**: redacta un informe claro con:
   - Resumen ejecutivo del área investigada.
   - Lista de archivos y líneas relevantes (`archivo:línea`).
   - Descripción de la lógica o flujo encontrado.
   - Observaciones o posibles mejoras (si aplica).

## Formato del informe

```
## Informe de investigación: <tema>

### Resumen
<descripción breve del hallazgo principal>

### Referencias
| Archivo | Línea(s) | Descripción |
|---------|----------|-------------|
| `ruta/archivo.py` | 10-25 | <qué hace ese fragmento> |

### Observaciones
- <punto relevante>
```

## Restricciones

- Solo usar las herramientas permitidas: Read, Grep, ListDir.
- No modificar ningún archivo del proyecto.
- Todas las referencias deben incluir archivo y número de línea exactos.
