# Guion del video (máx. 5 min)

1. (0:00–0:40) Presentación del grupo, problema y por qué NotaLang (diapositivas 2–3).
2. (0:40–1:20) Mostrar `NotaLang.g4`: tokens y reglas; correr `make`.
3. (1:20–2:00) Léxico: `python3 main.py tests/ok1_curso.nota --tokens` y `python3 main.py tests/err_lex1.nota`.
4. (2:00–2:50) Sintáctico: `python3 main.py tests/ok2_control.nota --arbol`, luego `err_sin1.nota` y `err_sin2.nota`.
5. (2:50–4:20) Semántico: `python3 main.py tests/ok1_curso.nota --tabla`, luego `err_sem5_pesos.nota`,
   `err_sem6_rango.nota`, `err_sem3_tipos.nota`, `err_sem1_no_declarada.nota` (o `make test`).
6. (4:20–5:00) `python3 derivaciones.py | head -40` (derivaciones) y cierre.
