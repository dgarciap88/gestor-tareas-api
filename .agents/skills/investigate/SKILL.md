---
name: investigate
description: Investiga el código y produce un informe con referencias exactas.
---

## Objetivo

Investigar un tema o área del código indicado por el usuario y producir un informe
conciso con referencias exactas (archivo y línea).

## Pasos

1. Identifica el tema o área a investigar según la solicitud del usuario.
2. Usa `grep` y lectura de archivos para localizar el código relevante.
3. Lee los archivos encontrados para entender la lógica y las relaciones.
4. Documenta los hallazgos con referencias exactas (`archivo:línea`).

## Formato del informe

Presenta los resultados al usuario con:

- **Resumen**: descripción breve de lo encontrado (2-3 frases).
- **Referencias**: lista de archivos y líneas relevantes usando `<ref_snippet>` tags.
- **Relaciones**: cómo se conectan los componentes encontrados (dependencias, flujo de datos).
- **Observaciones**: posibles mejoras o problemas detectados (solo si aplica).
