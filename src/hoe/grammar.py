# -*- coding: utf-8 -*-

from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.parsing import ParseError
from rpython.rlib.parsing.deterministic import LexerError

EBNF = """
IDENTIFIER: "[a-zA-Z_][a-zA-Z0-9_]*";
STRING: "\\"[^\\\\"]*\\"";
NUMBER: "\-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][\+\-]?[0-9]+)?";
IGNORE: " |\n";

main: >statement+<;

command: <quote> | <send> | <recv> | <eval> | <proc> | <begin> | <patch> | <cond> | <iter>;
statement: (IDENTIFIER [":"])? command;

quote: ["quote"] value;
eval: ["eval"] STRING value?;

proc: ["proc"] STRING >statement*< ["end"];
begin: ["begin"] >statement*< ["end"];
cond: ["cond"] >command*< ["end"];
iter: ["iter"] value >statement*< ["end"];

send: ["send"] STRING value;
recv: ["recv"] STRING;
patch: ["patch"] store value;

value: <STRING> | <NUMBER> | <object> | <array> | <"true"> | <"false"> | <"null"> | <store> | <payload> | <variable>;

variable: IDENTIFIER index*;
payload: ["$"] index*;
store: ["$$"] index*;
index: ["["] <value> ["]"];

object: ["{"] (entry [","])* entry* ["}"];
array: ["["] (value [","])* value* ["]"];
entry: value [":"] value;
"""

regexes, rules, _to_ast = parse_ebnf(EBNF)
parse = make_parse_function(regexes, rules, eof=True)
to_ast = _to_ast()

def ignore_comment(content):
    lines = content.splitlines()
    return '\n'.join(
        [n for n in lines if not n.strip().startswith('#')]
    )

def parse_source(content):
    try:
        source = ignore_comment(content)
        tree = parse(source)
        ast = to_ast.transform(tree)
        return ast
    except ParseError as e:
        print(e.nice_error_message('syntax error'))
        raise e
    except LexerError as e:
        print(e.nice_error_message('syntax error'))
        raise e
