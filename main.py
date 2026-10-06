# Uso: python3 main.py archivo.nota [--tokens] [--arbol] [--tabla]
import sys
from antlr4 import CommonTokenStream, FileStream, Token
from antlr4.error.ErrorListener import ErrorListener
from gen.NotaLangLexer import NotaLangLexer
from gen.NotaLangParser import NotaLangParser
from semantic.semantic_visitor import SemanticVisitor


class ErroresSintacticos(ErrorListener):
    def __init__(self):
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append(f'[Error Sintáctico, línea {line}:{column}] {msg}')


def main():
    archivo, opciones = sys.argv[1], sys.argv[2:]
    lexer = NotaLangLexer(FileStream(archivo, encoding='utf-8'))
    stream = CommonTokenStream(lexer)
    stream.fill()

    # analisis lexico
    errores_lex = []
    if '--tokens' in opciones:
        print('=== TOKENS ===')
    for tok in stream.tokens:
        if tok.type == Token.EOF:
            continue
        nombre = NotaLangLexer.symbolicNames[tok.type]
        if tok.type == NotaLangLexer.ERROR_LEXICO:
            errores_lex.append(f"[Error Léxico, línea {tok.line}:{tok.column}] carácter no reconocido '{tok.text}'")
        elif '--tokens' in opciones:
            print(f'  {tok.line:>3}:{tok.column:<3} {nombre:<12} {tok.text}')
    if errores_lex:
        print('\n=== ERRORES LÉXICOS ===')
        print('\n'.join('  ' + e for e in errores_lex))
        return 1

    # analisis sintactico
    parser = NotaLangParser(stream)
    parser.removeErrorListeners()
    listener = ErroresSintacticos()
    parser.addErrorListener(listener)
    tree = parser.programa()
    if listener.errores:
        print('\n=== ERRORES SINTÁCTICOS ===')
        print('\n'.join('  ' + e for e in listener.errores))
        return 1
    print('Análisis léxico y sintáctico: OK')
    if '--arbol' in opciones:
        print(tree.toStringTree(recog=parser))

    # analisis semantico
    visitor = SemanticVisitor()
    visitor.visit(tree)
    if '--tabla' in opciones:
        print('\n=== TABLA DE SÍMBOLOS ===')
        print(visitor.symtab.dump())
    if visitor.errors:
        print('\n=== ERRORES SEMÁNTICOS ===')
        print('\n'.join(f'  {e}' for e in visitor.errors))
        return 1
    print('Análisis semántico: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
