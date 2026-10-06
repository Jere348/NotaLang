# NotaLang — Teoría de Compiladores 2026-2 (Hito 1)

Lenguaje de dominio específico para registrar cursos, evaluaciones con pesos y notas,
y calcular promedios ponderados (`promedio`) y la nota necesaria para aprobar (`necesito`).

## Estructura
| Ruta | Contenido |
|---|---|
| `NotaLang.g4` | Analizador léxico y sintáctico |
| `gen/` | Lexer/Parser/Visitor generados por ANTLR con `make` |
| `semantic/` | Tabla de símbolos y analizador semántico (Visitor) |
| `main.py` | Driver: léxico → sintáctico → semántico |
| `tests/` | Entradas válidas (`ok*`) y con errores léxicos, sintácticos y semánticos (`err_*`) |
| `docs/` | Informe, Anexo A (derivaciones) y presentación en PDF |

## Requisitos
- Java + `antlr-4.13.1-complete.jar` (por defecto en `/usr/local/lib/`)
- `pip install antlr4-python3-runtime==4.13.1`

## Uso
```bash
make                                   # genera gen/ (ANTLR_JAR=/ruta/al.jar si está en otra ruta)
python3 main.py tests/ok1_curso.nota --tokens --tabla
make test                              # corre todas las pruebas
```

## Errores semánticos verificados
E1 no declarado · E2 redeclarado · E3 tipos en asignación · E4 condición no lógica ·
E5 pesos ≠ 100 % · E6 nota fuera de [0, 20] · E7 evaluación inexistente / no es curso · E8 operación inválida
