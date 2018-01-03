# -*- coding: utf-8 -*-

from hoe.grammar import parse_source
from hoe.builtin import is_builtin, builtin, builtin_bool
from hoe.runtime import (Env, Type, Int, Float,
                         Str, Bool, Null, Array,
                         Object,
                         null, true, false)

def eval(engine, source_code):
    return eval_source_code(engine, source_code)

def eval_source_code(engine, source_code):
    ast = parse_source(source_code)
    return eval_statements(engine, ast.children)

def eval_module(engine, source_code):
    ast = parse_source(source_code)
    env = Env()
    engine.stack.append(env)
    for statement in ast.children:
        eval_statement(engine, statement)
    engine.stack.pop()
    del env.namespace['^']
    return env


def eval_statements(engine, statements):
    for statement in statements:
        eval_statement(engine, statement)
    return engine.stack.pop().present()

def eval_statement(engine, statement):
    if len(engine.stack) == 0:
        engine.stack.append(Env())

    if len(statement.children) == 1:
        return eval_statement_without_identifier(engine, statement)
    elif len(statement.children) == 2:
        return eval_statement_with_identifier(engine, statement)
    else:
        raise Exception('unknown statement: %s' % statement)


def eval_statement_with_identifier(engine, statement):
    stack = engine.current_stack()
    stack.identifier = statement.children[0].additional_info
    val = eval_command(engine, statement.children[1])
    stack.push(val)
    return val

def eval_statement_without_identifier(engine, statement):
    stack = engine.current_stack()
    stack.identifier = '^'
    val = eval_command(engine, statement.children[0])
    stack.push(val)
    return val

def eval_command(engine, statement):
    if statement.symbol == 'value':
        return eval_value(engine, statement)
    elif statement.symbol == 'eval':
        return eval_eval(engine, statement)
    elif statement.symbol == 'begin':
        return eval_begin(engine, statement)
    elif statement.symbol == 'cond':
        return eval_cond(engine, statement)
    elif statement.symbol == 'iter':
        return eval_iter(engine, statement)
    elif statement.symbol == 'def':
        return eval_def(engine, statement)
    else:
        raise Exception('unknown command %s' % statement)

def eval_eval(engine, statement):
    def_STRING = statement.children[0]
    func_name = extract_STRING(def_STRING)
    payload = eval_expression(engine, statement.children[1]) \
            if len(statement.children) == 2 else null
    if func_name == 'eval' and isinstance(payload, Str):
        engine.stack.append(Env())
        return eval_source_code(engine, payload.str_val)
    if is_builtin(func_name):
        return builtin(engine, func_name, payload)
    statements = None
    for env in reversed(engine.stack):
        if env.has_def(func_name):
            statements = env.get_def(func_name)
            break
    if not statements:
        raise Exception('unknown def: %s' % func_name)
    env = Env()
    env.set('$', payload)
    engine.stack.append(env)
    return eval_statements(engine, statements)

def eval_def(engine, statement):
    def_name = extract_STRING(statement.children[0])
    engine.current_stack().define_def(def_name, statement.children[1:])
    return null

def eval_iter(engine, statement):
    iter_object = eval_expression(engine, statement.children[0])
    if isinstance(iter_object, Bool):
        return eval_iter_bool(engine, iter_object, statement.children[1:])
    elif isinstance(iter_object, Int):
        return eval_iter_n_times(engine, iter_object, statement.children[1:])
    elif isinstance(iter_object, Array):
        return eval_iter_array(engine, iter_object, statement.children[1:])
    else:
        raise Exception('not implemented: iter')

def eval_iter_bool(engine, bool, statements):
    if not bool.bool_val:
        return null
    while True:
        for statement in statements:
            eval_statement(engine, statement)

def eval_iter_array(engine, array, statements):
    stack = engine.current_stack()
    iter_obj_identifier = stack.identifier
    for el in array.array_val:
        stack.set(iter_obj_identifier, el)
        for statement in statements:
            eval_statement(engine, statement)
    return array

def eval_iter_n_times(engine, n, statements):
    stack = engine.current_stack()
    iter_obj_identifier = stack.identifier
    stack.set(iter_obj_identifier, Int(0))
    x = 0
    while x < n.int_val:
        for statement in statements:
            eval_statement(engine, statement)
        x += 1
        stack.set(iter_obj_identifier, Int(x))
    return n

def type_cast_to_bool(engine, val):
    return builtin_bool(engine, val)

def eval_cond(engine, statement):
    statements_count = len(statement.children)
    if statements_count % 2 != 0:
        raise Exception('cond branches not match.')
    for i in range(statements_count / 2):
        index = i * 2
        condition, block = statement.children[index], statement.children[index+1]
        if type_cast_to_bool(engine, eval_command(engine, condition)).bool_val:
            return eval_command(engine, block)
    return null

def eval_value(engine, statement):
    return eval_expression(engine, statement.children[0])

def eval_begin(engine, statement):
    begin_stack = Env()
    engine.stack.append(begin_stack)
    for stmt in statement.children:
        eval_statement(engine, stmt)
    return engine.stack.pop().present()

def eval_expression(engine, expr):
    if expr.symbol == 'NUMBER' and '.' in expr.additional_info:
        return eval_float(engine, expr)
    elif expr.symbol == 'NUMBER':
        return eval_int(engine, expr)
    elif expr.symbol == 'STRING':
        return eval_str(engine, expr)
    elif expr.symbol == 'array':
        return eval_array(engine, expr)
    elif expr.symbol == 'object':
        return eval_object(engine, expr)
    elif expr.symbol == 'variable':
        return eval_variable(engine, expr)
    elif expr.symbol == 'payload':
        return eval_payload(engine, expr)
    elif expr.additional_info == 'true':
        return true
    elif expr.additional_info == 'false':
        return false
    elif expr.additional_info == 'null':
        return null
    else:
        raise Exception('unknown expression')

def eval_payload(engine, expr):
    for env in reversed(engine.stack):
        if env.has('$'):
            val = env.get('$')
            if len(expr.children) == 0:
                return val
            else:
                for index in expr.children:
                    val = get_value_by_index(engine, val, index)
                return val
    raise Exception('invalid payload getter.')

def eval_payload_with_index(engine, expr):
    for getter_ast in expr.children:
        getter = eval_expression(engine, getter_ast)
        if isinstance(val, Array) and isinstance(getter, Int):
            val = val.array_val[getter.int_val]
        elif isinstance(val, Object) and isinstance(getter, Str):
            val = val.object_val[getter.str_val] # XXX object_val need to be raw str.
        else:
            raise Exception('invalid payload getter.')
    return val

def get_value_by_index(engine, var, index_ast):
    indexer = eval_expression(engine, index_ast)
    if isinstance(indexer, Str) and isinstance(var, Object):
        return var.object_val[indexer.str_val]
    elif isinstance(indexer, Int) and isinstance(var, Array):
        return var.array_val[indexer.int_val]
    else:
        raise Exception('unknown data type')

def eval_variable(engine, expr):
    stack = engine.current_stack()
    val = stack.get(expr.children[0].additional_info)
    if len(expr.children) >= 1:
        for index in expr.children[1:]:
            val = get_value_by_index(engine, val, index)
    return val

def eval_float(engine, expr):
    return Float(float(expr.additional_info))

def eval_int(engine, expr):
    return Int(int(expr.additional_info))

def extract_STRING(expr):
    start = 1
    end = max(len(expr.additional_info) -1, 1)
    return expr.additional_info[start:end]

def eval_str(engine, expr):
    return Str(extract_STRING(expr))

def eval_array(engine, expr):
    array = []
    for child in expr.children:
        element = eval_expression(engine, child)
        array.append(element)
    return Array(array)

def eval_object(engine, expr):
    _object = {}
    for child in expr.children:
        key = eval_expression(engine, child.children[0])
        value = eval_expression(engine, child.children[1])
        if not isinstance(key, Str):
            raise Exception('unknown data type.')
        _object[key.str_val] = value
    return Object(_object)

