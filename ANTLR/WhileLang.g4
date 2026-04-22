grammar WhileLang;

// Парсер
program : stat+ EOF ;

stat    : 'while' '(' condition ')' '{' body '}' ';' ;

condition : expression (logical_op expression)* ;

expression : term comp_op term ;

term    : ID | NUMBER ;

body    : assignment+ ;

assignment : ID ('++' | '--') ';' ;

comp_op    : '<' | '>' | '==' | '>=' | '<=' | '!=' ;
logical_op : '||' | '&&' ;

// Лексер
ID     : '$' [a-zA-Z] [a-zA-Z0-9_]* ;
NUMBER : [0-9]+ ;
WS     : [ \t\r\n]+ -> skip ;

// Обработка непредвиденных символов
UNKNOWN : . ;