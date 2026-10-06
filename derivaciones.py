# Derivaciones mas a la izquierda de los ejemplos de cada construccion
# Uso: python3 derivaciones.py [--html]
import sys
from html import escape
from antlr4 import CommonTokenStream, InputStream, Token
from antlr4.tree.Tree import TerminalNode
from gen.NotaLangLexer import NotaLangLexer
from gen.NotaLangParser import NotaLangParser

# nombre del terminal en la gramatica
TERMINAL = {'ID': 'id', 'NUM_ENT': 'num_ent', 'NUM_DEC': 'num_dec',
            'CADENA': 'cadena', 'PORCENTAJE': 'porcentaje'}

# (construccion, regla inicial, no-terminales a expandir, ejemplos)
CONSTRUCCIONES = [
    ('C1. Declaración de variables', 'declVar', {'declVar', 'tipo', 'inicializacion'}, [
        'var nota : decimal = 14.5;',
        'var n : entero;',
        'var nombre : texto = "Ana";',
        'var aprobado : logico = verdadero;',
        'var total : decimal = suma / n;',
    ]),
    ('C2. Asignación', 'asignacion', {'asignacion', 'destino'}, [
        'x = 10;',
        'prom = suma / n;',
        'Compiladores.PC1 = 15;',
        'ok = promedio(Calculo) >= 10.5;',
        'nombre = "Ana" + " Perez";',
    ]),
    ('C3. Expresiones aritméticas, relacionales y lógicas', 'expr', None, [
        'a + b * 2',
        '(x - 1) / 2',
        'nota >= 10.5 y no fin',
        'promedio(C) < 11 o C.EF == 0',
        'necesito(Calculo, 13) - n mod 2',
    ]),
    ('C4. Sentencia selectiva (si / sino)', 'siStmt', {'siStmt', 'sinoParte', 'bloque'}, [
        'si (x > 3) { mostrar(x); }',
        'si (ok) { n = 1; } sino { n = 0; }',
        'si (p >= 10.5) { mostrar("A"); } sino si (p >= 8) { mostrar("S"); }',
        'si (a == b) { }',
        'si (no ok) { leer(x); } sino { x = 0; }',
    ]),
    ('C5a. Sentencia iterativa mientras', 'mientrasStmt', {'mientrasStmt', 'bloque'}, [
        'mientras (i < 10) { i = i + 1; }',
        'mientras (verdadero) { }',
        'mientras (no ok y ef <= 20) { ef = ef + 1; }',
        'mientras (x != 0) { leer(x); mostrar(x); }',
        'mientras (promedio(C) < 10.5) { C.EF = C.EF + 1; }',
    ]),
    ('C5b. Sentencia iterativa para', 'paraStmt', {'paraStmt', 'bloque'}, [
        'para i desde 1 hasta 10 { mostrar(i); }',
        'para k desde 0 hasta n { }',
        'para j desde a hasta b + 1 { s = s + j; }',
        'para i desde 1 hasta 3 { leer(nota); suma = suma + nota; }',
        'para x desde n hasta 2 * n { }',
    ]),
    ('C6a. Entrada (leer)', 'leerStmt', {'leerStmt', 'destino'}, [
        'leer(x);',
        'leer(nota);',
        'leer(Compiladores.EB);',
        'leer(Calculo.PC);',
        'leer(n);',
    ]),
    ('C6b. Salida (mostrar)', 'mostrarStmt', {'mostrarStmt', 'argumentos', 'masArgumentos'}, [
        'mostrar(x);',
        'mostrar("Hola");',
        'mostrar("Promedio: ", promedio(C));',
        'mostrar(a, b, c);',
        'mostrar("Necesitas ", necesito(C, 13), " en el EF");',
    ]),
    ('C7. Declaración de curso', 'declCurso', {'declCurso', 'evaluaciones', 'evaluacion', 'notaOpcional'}, [
        'curso Arte { EF : 100%; }',
        'curso Calculo { PC : 40% = 12; EF : 60%; }',
        'curso Fisica { T1 : 50% = 14; T2 : 50% = 16.5; }',
        'curso Quimica { PC1 : 20%; PC2 : 20%; EF : 60% = 11; }',
        'curso Ingles { ORAL : 40% = 15.5; ESCRITO : 60%; }',
    ]),
]


def parsear(codigo, regla):
    lexer = NotaLangLexer(InputStream(codigo))
    stream = CommonTokenStream(lexer)
    parser = NotaLangParser(stream)
    parser.removeErrorListeners()
    tree = getattr(parser, regla)()
    ok = parser.getNumberOfSyntaxErrors() == 0 and stream.LA(1) == Token.EOF
    return tree, ok


def nombre_regla(ctx):
    return NotaLangParser.ruleNames[ctx.getRuleIndex()]


def terminal(node):
    nombre = NotaLangLexer.symbolicNames[node.symbol.type]
    return TERMINAL.get(nombre, node.getText())


def hojas(ctx):
    if isinstance(ctx, TerminalNode):
        return [('t', terminal(ctx))]
    return [h for c in (ctx.children or []) for h in hojas(c)]


def derivar(tree, expandir):
    forma = [tree]
    pasos = [(False, forma)]
    while True:
        i = next((k for k, n in enumerate(forma) if not isinstance(n, TerminalNode)), None)
        if i is None:
            break
        nodo = forma[i]
        if expandir is None or nombre_regla(nodo) in expandir:
            hijos, multi = list(nodo.children or []), False
        else:
            hijos, multi = [c for c in _terminales(nodo)], True
        forma = forma[:i] + hijos + forma[i + 1:]
        pasos.append((multi, forma))
    return [(m, [('t', terminal(n)) if isinstance(n, TerminalNode) else ('nt', nombre_regla(n)) for n in f])
            for m, f in pasos]


def _terminales(ctx):
    if isinstance(ctx, TerminalNode):
        return [ctx]
    return [t for c in (ctx.children or []) for t in _terminales(c)]


def texto(forma):
    return ' '.join(s for _, s in forma) or 'ε'


def a_html(forma):
    return ' '.join(f'<b>{escape(s)}</b>' if k == 't' else f'<i>{s}</i>' for k, s in forma) or 'ε'


def main():
    como_html = '--html' in sys.argv
    out, errores = [], 0
    for titulo, regla, expandir, ejemplos in CONSTRUCCIONES:
        out.append(f'<h1>{titulo}</h1>' if como_html else f'\n===== {titulo} =====')
        for n, codigo in enumerate(ejemplos, 1):
            tree, ok = parsear(codigo, regla)
            if not ok:
                errores += 1
                print(f'!! NO ACEPTADO por <{regla}>: {codigo}', file=sys.stderr)
                continue
            if n > 4:
                continue
            pasos = derivar(tree, expandir)
            if como_html:
                out.append(f'<div class="card"><div class="ch"><b>Ejemplo {n}</b><code>{escape(codigo)}</code></div><ol start="0">')
                for k, (multi, f) in enumerate(pasos):
                    flecha = '' if k == 0 else ('⇒<sup>*</sup><sub>lm</sub>' if multi else '⇒<sub>lm</sub>')
                    out.append(f'<li><span class="op">{flecha}</span>{a_html(f)}</li>')
                out.append('</ol></div>')
            else:
                out.append(f'\nEjemplo {n}: {codigo}')
                for k, (multi, f) in enumerate(pasos):
                    flecha = '   ' if k == 0 else (' =>*' if multi else ' => ')
                    out.append(f'{flecha} {texto(f)}')
    if como_html:
        with open('docs/derivaciones.html', 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(out))
        print('docs/derivaciones.html generado')
    else:
        print('\n'.join(out))
    print(f'Ejemplos no aceptados: {errores}', file=sys.stderr)
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
