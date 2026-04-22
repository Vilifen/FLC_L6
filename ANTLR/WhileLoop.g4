grammar WhileLoop;

program
    : (whileStatement)* EOF
    ;

whileStatement
    : WHILE LPAREN condition RPAREN LBRACE body RBRACE SEMI
    ;

condition
    : expression (LOGIC_OP expression)*
    ;

expression
    : (VAR | ID | NUMBER) COMP_OP (VAR | ID | NUMBER)
    ;

body
    : (statement)*
    ;

statement
    : (VAR | ID) INC_DEC_OP SEMI
    ;

WHILE    : 'while' ;
VAR      : '$' [a-zA-Z0-9_]* ;
NUMBER   : [0-9]+ ;
COMP_OP  : '<' | '>' | '==' | '>=' | '<=' | '!=' ;
LOGIC_OP : '||' | '&&' ;
INC_DEC_OP : '++' | '--' ;
LPAREN   : '(' ;
RPAREN   : ')' ;
LBRACE   : '{' ;
RBRACE   : '}' ;
SEMI     : ';' ;
ID       : [a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]* ;
WS       : [ \t\r\n]+ -> skip ;

ANY      : . ;