grammar ard546;

script     : testcase*; // Some number of commands
testcase
           : ('@GLOBAL') conditions
           | ('@CMD' command '@COND' conditions)
           | ('@CMD' command); // command and condition

//// parser
// command
command    : '[' line+ ']';
line       : title ':' attr+;
title      : id;
attr       : attrname '=' attrdata;
attrname   : id;
attrdata   : hexnum | num | id;

// testing
conditions : clause+;
clause     : cname carg;
cname      : '@EXPECT' | '@REJECT';
carg       : id | idlist;
idlist     : '[' id (',' id)* ']';

//// lexer
hexnum     : '0x' num | '0X' num;
id         : (' '..'~')+;
string     : '"' (' '..'~')* '"';
int        : '0'..'9'+;
ws         : [ \t\n\r]+ -> skip ;

