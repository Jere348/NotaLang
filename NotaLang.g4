grammar NotaLang;

// NotaLang

// ========== REGLAS DEL PARSER ==========

// ---------- PROGRAMA
programa : sentencias EOF ;

sentencias
    : sentencia sentencias
    |                               // epsilon
    ;

sentencia
    : declVar
    | asignacion
    | siStmt
    | mientrasStmt
    | paraStmt
    | leerStmt
    | mostrarStmt
    | declCurso
    | bloque
    ;

bloque : LLAVE_IZQ sentencias LLAVE_DER ;

// ---------- C1. DECLARACION DE VARIABLES
declVar : VAR ID DOS_PUNTOS tipo inicializacion PUNTO_COMA ;

tipo : ENTERO | DECIMAL | TEXTO | LOGICO ;

inicializacion
    : ASIGNA expr
    |                               // epsilon
    ;

// ---------- C2. ASIGNACION
asignacion : destino ASIGNA expr PUNTO_COMA ;

destino
    : ID
    | ID PUNTO ID
    ;

// ---------- C3. EXPRESIONES
expr
    : expr O exprY
    | exprY
    ;

exprY
    : exprY Y exprNo
    | exprNo
    ;

exprNo
    : NO exprNo
    | exprRel
    ;

exprRel
    : exprArit opRel exprArit
    | exprArit
    ;

exprArit
    : exprArit opSuma termino
    | termino
    ;

termino
    : termino opMul factor
    | factor
    ;

factor
    : PAR_IZQ expr PAR_DER
    | MENOS factor
    | NUM_ENT
    | NUM_DEC
    | CADENA
    | VERDADERO
    | FALSO
    | ID
    | ID PUNTO ID
    | PROMEDIO PAR_IZQ ID PAR_DER
    | NECESITO PAR_IZQ ID COMA expr PAR_DER
    ;

opRel  : MENOR | MAYOR | MENOR_IG | MAYOR_IG | IGUAL | DISTINTO ;
opSuma : MAS | MENOS ;
opMul  : POR | DIV | MOD ;

// ---------- C4. SELECTIVA
siStmt : SI PAR_IZQ expr PAR_DER bloque sinoParte ;

sinoParte
    : SINO bloque
    | SINO siStmt
    |                               // epsilon
    ;

// ---------- C5. ITERATIVAS
mientrasStmt : MIENTRAS PAR_IZQ expr PAR_DER bloque ;

paraStmt : PARA ID DESDE expr HASTA expr bloque ;

// ---------- C6. ENTRADA / SALIDA
leerStmt : LEER PAR_IZQ destino PAR_DER PUNTO_COMA ;

mostrarStmt : MOSTRAR PAR_IZQ argumentos PAR_DER PUNTO_COMA ;

argumentos : expr masArgumentos ;

masArgumentos
    : COMA expr masArgumentos
    |                               // epsilon
    ;

// ---------- C7. DECLARACION DE CURSO
declCurso : CURSO ID LLAVE_IZQ evaluaciones LLAVE_DER ;

evaluaciones
    : evaluacion evaluaciones
    | evaluacion
    ;

evaluacion : ID DOS_PUNTOS PORCENTAJE notaOpcional PUNTO_COMA ;

notaOpcional
    : ASIGNA expr
    |                               // epsilon
    ;


// ========== REGLAS DEL LEXER ==========

// ---------- PALABRAS CLAVE
VAR       : 'var' ;
CURSO     : 'curso' ;
SI        : 'si' ;
SINO      : 'sino' ;
MIENTRAS  : 'mientras' ;
PARA      : 'para' ;
DESDE     : 'desde' ;
HASTA     : 'hasta' ;
LEER      : 'leer' ;
MOSTRAR   : 'mostrar' ;
PROMEDIO  : 'promedio' ;
NECESITO  : 'necesito' ;

// ---------- TIPOS DE DATOS
ENTERO    : 'entero' ;
DECIMAL   : 'decimal' ;
TEXTO     : 'texto' ;
LOGICO    : 'logico' ;

// ---------- LOGICOS
VERDADERO : 'verdadero' ;
FALSO     : 'falso' ;
Y         : 'y' ;
O         : 'o' ;
NO        : 'no' ;
MOD       : 'mod' ;

// ---------- OPERADORES RELACIONALES
MENOR_IG  : '<=' ;
MAYOR_IG  : '>=' ;
IGUAL     : '==' ;
DISTINTO  : '!=' ;
MENOR     : '<' ;
MAYOR     : '>' ;

// ---------- OPERADORES ARITMETICOS Y ASIGNACION
MAS       : '+' ;
MENOS     : '-' ;
POR       : '*' ;
DIV       : '/' ;
ASIGNA    : '=' ;

// ---------- DELIMITADORES
PAR_IZQ    : '(' ;
PAR_DER    : ')' ;
LLAVE_IZQ  : '{' ;
LLAVE_DER  : '}' ;
DOS_PUNTOS : ':' ;
PUNTO_COMA : ';' ;
COMA       : ',' ;
PUNTO      : '.' ;

// ---------- LITERALES
PORCENTAJE : [0-9]+ ('.' [0-9]+)? '%' ;
NUM_DEC    : [0-9]+ '.' [0-9]+ ;
NUM_ENT    : [0-9]+ ;
CADENA     : '"' ~["\r\n]* '"' ;

// ---------- IDENTIFICADORES
ID : [a-zA-Z_] [a-zA-Z_0-9]* ;

// ---------- IGNORADOS
COMENTARIO_LINEA  : '//' ~[\r\n]* -> skip ;
COMENTARIO_BLOQUE : '/*' .*? '*/' -> skip ;
WS                : [ \t\r\n]+ -> skip ;

// ---------- ERROR LEXICO
ERROR_LEXICO : . ;
