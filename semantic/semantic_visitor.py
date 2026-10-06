from .symbol_table import SymbolTable, SemanticError
from gen.NotaLangVisitor import NotaLangVisitor

NUMERICOS = ('entero', 'decimal')

# tipos resultantes de + - * /
ARITH_COMPAT = {
    ('entero', 'entero'): 'entero',
    ('entero', 'decimal'): 'decimal',
    ('decimal', 'entero'): 'decimal',
    ('decimal', 'decimal'): 'decimal',
}

NOTA_MIN, NOTA_MAX = 0, 20


def asignable(destino, origen):
    return destino == origen or (destino == 'decimal' and origen == 'entero')


def constante(ctx):
    try:
        return float(ctx.getText())
    except ValueError:
        return None


class SemanticVisitor(NotaLangVisitor):
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors: list[SemanticError] = []
        self._bloques = 0

    def _error(self, codigo, msg, ctx):
        self.errors.append(SemanticError(codigo, msg, ctx.start.line))
        return 'error'

    def _buscar(self, name, ctx):
        sym = self.symtab.lookup(name)
        if sym is None:
            self._error('E1', f"Identificador '{name}' no declarado", ctx)
        return sym

    def _buscar_curso(self, name, ctx):
        sym = self._buscar(name, ctx)
        if sym is not None and sym.type_ != 'curso':
            self._error('E7', f"'{name}' no es un curso", ctx)
            return None
        return sym

    def _verificar_nota(self, expr_ctx, ctx):
        t = self.visit(expr_ctx)
        if t == 'error':
            return
        if t not in NUMERICOS:
            self._error('E3', f"Una nota debe ser numérica, se obtuvo '{t}'", ctx)
            return
        v = constante(expr_ctx)
        if v is not None and not (NOTA_MIN <= v <= NOTA_MAX):
            self._error('E6', f"Nota {expr_ctx.getText()} fuera del rango [{NOTA_MIN}, {NOTA_MAX}]", ctx)

    # bloque
    def visitBloque(self, ctx):
        self._bloques += 1
        self.symtab.enter_scope(f'bloque{self._bloques}_L{ctx.start.line}')
        self.visit(ctx.sentencias())
        self.symtab.exit_scope()

    # C1. declaracion
    def visitDeclVar(self, ctx):
        name, tipo = ctx.ID().getText(), ctx.tipo().getText()
        init = ctx.inicializacion().expr()
        if init is not None:
            t = self.visit(init)
            if t != 'error' and not asignable(tipo, t):
                self._error('E3', f"No se puede inicializar '{name}' ({tipo}) con un valor '{t}'", ctx)
        try:
            self.symtab.declare(name, tipo, ctx.start.line)
        except SemanticError as e:
            self.errors.append(e)

    # C2. asignacion
    def visitAsignacion(self, ctx):
        d = ctx.destino()
        if d.PUNTO():
            if self._tipo_destino(d) != 'error':
                self._verificar_nota(ctx.expr(), ctx)
            return
        destino = self._tipo_destino(d)
        t = self.visit(ctx.expr())
        if 'error' in (destino, t):
            return
        if not asignable(destino, t):
            self._error('E3', f"No se puede asignar '{t}' a '{d.getText()}' ({destino})", ctx)

    def _tipo_destino(self, d):
        ids = d.ID()
        if d.PUNTO():
            curso = self._buscar_curso(ids[0].getText(), d)
            if curso is None:
                return 'error'
            if ids[1].getText() not in curso.evaluaciones:
                return self._error('E7', f"El curso '{curso.name}' no tiene la evaluación '{ids[1].getText()}'", d)
            return 'decimal'
        sym = self._buscar(ids[0].getText(), d)
        return sym.type_ if sym else 'error'

    # C4 / C5. selectiva e iterativas
    def _condicion(self, ctx, nombre):
        t = self.visit(ctx.expr())
        if t not in ('logico', 'error'):
            self._error('E4', f"La condición de '{nombre}' debe ser logico, se obtuvo '{t}'", ctx)

    def visitSiStmt(self, ctx):
        self._condicion(ctx, 'si')
        self.visit(ctx.bloque())
        self.visit(ctx.sinoParte())

    def visitMientrasStmt(self, ctx):
        self._condicion(ctx, 'mientras')
        self.visit(ctx.bloque())

    def visitParaStmt(self, ctx):
        for e in ctx.expr():
            t = self.visit(e)
            if t not in ('entero', 'error'):
                self._error('E8', f"Los límites de 'para' deben ser entero, se obtuvo '{t}'", ctx)
        self.symtab.enter_scope(f'para_L{ctx.start.line}')
        try:
            self.symtab.declare(ctx.ID().getText(), 'entero', ctx.start.line)
        except SemanticError as e:
            self.errors.append(e)
        self.visit(ctx.bloque())
        self.symtab.exit_scope()

    # C6. leer
    def visitLeerStmt(self, ctx):
        t = self._tipo_destino(ctx.destino())
        if t == 'curso':
            self._error('E3', f"No se puede leer un curso completo ('{ctx.destino().getText()}')", ctx)

    # C7. curso
    def visitDeclCurso(self, ctx):
        name = ctx.ID().getText()
        try:
            curso = self.symtab.declare(name, 'curso', ctx.start.line)
        except SemanticError as e:
            self.errors.append(e)
            curso = None
        total = 0.0
        ev = ctx.evaluaciones()
        while ev is not None:
            e = ev.evaluacion()
            eval_name = e.ID().getText()
            peso = float(e.PORCENTAJE().getText()[:-1])
            total += peso
            if curso is not None:
                if eval_name in curso.evaluaciones:
                    self._error('E2', f"Evaluación '{eval_name}' repetida en el curso '{name}'", e)
                curso.evaluaciones[eval_name] = peso
            if e.notaOpcional().expr() is not None:
                self._verificar_nota(e.notaOpcional().expr(), e)
            ev = ev.evaluaciones()
        if abs(total - 100) > 1e-9:
            self._error('E5', f"Los pesos del curso '{name}' suman {total:g}% (deben sumar 100%)", ctx)

    # C3. expresiones
    def _binaria(self, ctx, izq, der, op):
        t1, t2 = self.visit(izq), self.visit(der)
        if 'error' in (t1, t2):
            return 'error'
        if op in ('y', 'o'):
            if t1 == t2 == 'logico':
                return 'logico'
        elif op in ('<', '>', '<=', '>='):
            if t1 in NUMERICOS and t2 in NUMERICOS:
                return 'logico'
        elif op in ('==', '!='):
            if (t1 in NUMERICOS and t2 in NUMERICOS) or (t1 == t2 and t1 != 'curso'):
                return 'logico'
        elif op == 'mod':
            if t1 == t2 == 'entero':
                return 'entero'
        elif op == '+' and t1 == t2 == 'texto':
            return 'texto'
        elif (t1, t2) in ARITH_COMPAT:
            return 'decimal' if op == '/' else ARITH_COMPAT[(t1, t2)]
        return self._error('E8', f"Operación '{t1} {op} {t2}' no válida", ctx)

    def visitExpr(self, ctx):
        if ctx.O() is None:
            return self.visit(ctx.exprY())
        return self._binaria(ctx, ctx.expr(), ctx.exprY(), 'o')

    def visitExprY(self, ctx):
        if ctx.Y() is None:
            return self.visit(ctx.exprNo())
        return self._binaria(ctx, ctx.exprY(), ctx.exprNo(), 'y')

    def visitExprNo(self, ctx):
        if ctx.NO() is None:
            return self.visit(ctx.exprRel())
        t = self.visit(ctx.exprNo())
        if t not in ('logico', 'error'):
            return self._error('E8', f"Operación 'no {t}' no válida", ctx)
        return t

    def visitExprRel(self, ctx):
        a = ctx.exprArit()
        if ctx.opRel() is None:
            return self.visit(a[0])
        return self._binaria(ctx, a[0], a[1], ctx.opRel().getText())

    def visitExprArit(self, ctx):
        if ctx.opSuma() is None:
            return self.visit(ctx.termino())
        return self._binaria(ctx, ctx.exprArit(), ctx.termino(), ctx.opSuma().getText())

    def visitTermino(self, ctx):
        if ctx.opMul() is None:
            return self.visit(ctx.factor())
        return self._binaria(ctx, ctx.termino(), ctx.factor(), ctx.opMul().getText())

    def visitFactor(self, ctx):
        if ctx.NUM_ENT():   return 'entero'
        if ctx.NUM_DEC():   return 'decimal'
        if ctx.CADENA():    return 'texto'
        if ctx.VERDADERO() or ctx.FALSO(): return 'logico'
        if ctx.PAR_IZQ() and ctx.ID() == []:
            return self.visit(ctx.expr())
        if ctx.MENOS():
            t = self.visit(ctx.factor())
            if t not in NUMERICOS and t != 'error':
                return self._error('E8', f"Operación '-{t}' no válida", ctx)
            return t
        if ctx.PROMEDIO():
            return 'decimal' if self._buscar_curso(ctx.ID(0).getText(), ctx) else 'error'
        if ctx.NECESITO():
            curso = self._buscar_curso(ctx.ID(0).getText(), ctx)
            t = self.visit(ctx.expr())
            if t not in NUMERICOS and t != 'error':
                return self._error('E8', f"La nota objetivo de 'necesito' debe ser numérica, se obtuvo '{t}'", ctx)
            return 'decimal' if curso else 'error'
        if ctx.PUNTO():
            ids = ctx.ID()
            curso = self._buscar_curso(ids[0].getText(), ctx)
            if curso is None:
                return 'error'
            if ids[1].getText() not in curso.evaluaciones:
                return self._error('E7', f"El curso '{curso.name}' no tiene la evaluación '{ids[1].getText()}'", ctx)
            return 'decimal'
        sym = self._buscar(ctx.ID(0).getText(), ctx)
        return sym.type_ if sym else 'error'
