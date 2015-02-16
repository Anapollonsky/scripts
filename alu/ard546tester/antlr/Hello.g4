grammar ard546;

// parser
script : command_wrap*; // Some number of commands
command_wrap : '@CMD' command '@COND' condition; // command and condition

command: '[' line+ ']';
line: title ':' attr+;
attr: attrname '=' attrdata;
        



// lexer
title: string;
attrname: string;
attrdata: hexnum | num | string
        

string : (' '..'~')+;
int    : '0'..'9'+;
ws     : [ \t\n\r]+ -> skip ;

