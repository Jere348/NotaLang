class SemanticError(Exception):
    def __init__(self, codigo: str, message: str, line: int = 0):
        super().__init__(f'[Error Semántico {codigo}, línea {line}] {message}')
        self.codigo = codigo
        self.line = line


class Symbol:
    def __init__(self, name, type_, scope, line):
        self.name = name
        self.type_ = type_
        self.scope = scope
        self.line = line
        self.evaluaciones = {}  # cursos: evaluacion -> peso

    def __repr__(self):
        return f"Symbol({self.name}: {self.type_} @ {self.scope}, línea {self.line})"


class SymbolTable:
    def __init__(self):
        self._table: dict[str, dict[str, Symbol]] = {'global': {}}
        self._scope_stack: list[str] = ['global']

    @property
    def current_scope(self) -> str:
        return self._scope_stack[-1]

    def enter_scope(self, name: str):
        self._scope_stack.append(name)
        self._table.setdefault(name, {})

    def exit_scope(self):
        self._scope_stack.pop()

    def declare(self, name: str, type_: str, line: int) -> Symbol:
        scope = self.current_scope
        if name in self._table[scope]:
            raise SemanticError('E2', f"Identificador '{name}' ya declarado en el ámbito '{scope}'", line)
        sym = self._table[scope][name] = Symbol(name, type_, scope, line)
        return sym

    def lookup(self, name: str) -> Symbol | None:
        for scope in reversed(self._scope_stack):
            if name in self._table.get(scope, {}):
                return self._table[scope][name]
        return None

    def dump(self) -> str:
        lines = []
        for scope, syms in self._table.items():
            for s in syms.values():
                extra = f"  evaluaciones={s.evaluaciones}" if s.type_ == 'curso' else ''
                lines.append(f"  {scope:<14} {s.name:<16} {s.type_:<8} línea {s.line}{extra}")
        return '\n'.join(lines)
