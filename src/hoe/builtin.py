
from rpython.rlib.rpath import rabspath, rjoin
from hoe.runtime import (Env, Type, Int, Float,
                         Str, Bool, Null, Array,
                         Object,
                         null, true, false)
from hoe.lib import socket

def builtin_type(engine, payload):
    if isinstance(payload, Int):
        return Str('int')
    elif isinstance(payload, Float):
        return Str('float')
    elif isinstance(payload, Str):
        return Str('str')
    elif isinstance(payload, Bool):
        return Str('bool')
    elif isinstance(payload, Null):
        return Str('null')
    elif isinstance(payload, Array):
        return Str('array')
    elif isinstance(payload, Object):
        return Str('object')
    else:
        raise Exception('unknown data type.')

def builtin_plus(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type')
    if isinstance(payload.array_val[0], Float) or isinstance(payload.array_val[0], Int):
        return builtin_plus_number(engine, payload)
    elif isinstance(payload.array_val[0], Str):
        return builtin_plus_string(engine, payload)
    else:
        raise Exception('unknown element type')

def builtin_plus_number(engine, payload):
    i = 0
    f = 0.0
    has_float = False
    for el in payload.array_val:
        if isinstance(el, Float):
            has_float = True
            f += el.float_val
        elif isinstance(el, Int):
            i += el.int_val
        else:
            raise Exception('unknown element type')
    if has_float:
        return Float(f + i)
    else:
        return Int(i)

def builtin_plus_string(engine, payload):
    str_array = [x.str_val for x in payload.array_val]
    return Str(''.join(str_array))

def builtin_minus(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown parameter')
    if len(payload.array_val) == 0:
        return Int(0)
    elif len(payload.array_val) == 1:
        return payload.array_val[0]
    else:
        i = 1
        val = Int(0)
        while i < len(payload.array_val):
            val = builtin_minus_atom(payload.array_val[i-1], payload.array_val[i])
            i += 1
        return val

def builtin_minus_atom(left, right):
    if isinstance(left, Int) and isinstance(right, Float):
        return Float(left.int_val - right.float_val)
    elif isinstance(left, Float) and isinstance(right, Float):
        return Float(left.float_val - right.float_val)
    elif isinstance(left, Float) and isinstance(right, Int):
        return Float(left.float_val - right.int_val)
    elif isinstance(left, Int) and isinstance(right, Int):
        return Int(left.int_val - right.int_val)
    else:
        raise Exception('unknown data type')

def builtin_mul(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown parameter')
    if len(payload.array_val) == 0:
        return Int(1)
    elif len(payload.array_val) == 1:
        return payload.array_val[0]
    else:
        i = 1
        val = Int(1)
        while i < len(payload.array_val):
            val = builtin_mul_atom(payload.array_val[i-1], payload.array_val[i])
            i += 1
        return val

def builtin_mul_atom(left, right):
    if isinstance(left, Int) and isinstance(right, Float):
        return Float(left.int_val * right.float_val)
    elif isinstance(left, Float) and isinstance(right, Float):
        return Float(left.float_val * right.float_val)
    elif isinstance(left, Float) and isinstance(right, Int):
        return Float(left.float_val * right.int_val)
    elif isinstance(left, Int) and isinstance(right, Int):
        return Int(left.int_val * right.int_val)
    else:
        raise Exception('unknown data type')

def builtin_div(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown parameter')
    if len(payload.array_val) == 0:
        return Int(1)
    elif len(payload.array_val) == 1:
        return payload.array_val[0]
    else:
        i = 1
        val = Int(1)
        while i < len(payload.array_val):
            val = builtin_div_atom(payload.array_val[i-1], payload.array_val[i])
            i += 1
        return val


def builtin_div_atom(left, right):
    if isinstance(right, Int) and right.int_val == 0:
        raise Exception('unknown data type')
    elif isinstance(right, Float) and right.float_val == 0.0:
        raise Exception('unknown data type')
    elif isinstance(left, Int) and isinstance(right, Float):
        return Float(left.int_val / right.float_val)
    elif isinstance(left, Float) and isinstance(right, Float):
        return Float(left.float_val / right.float_val)
    elif isinstance(left, Float) and isinstance(right, Int):
        return Float(left.float_val / right.int_val)
    elif isinstance(left, Int) and isinstance(right, Int):
        return Int(left.int_val / right.int_val)
    else:
        raise Exception('unknown data type')



def builtin_eq(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown parameter')
    prev = None
    for el in payload.array_val:
        if prev is not None:
            if isinstance(prev, Array) and isinstance(el, Array):
                if len(prev.array_val) != len(el.array_val):
                    return false
                for i in range(len(el.array_val)):
                    left = prev.array_val[i]
                    right = el.array_val[i]
                    if not builtin_eq_atom(left, right).bool_val:
                        return false
                return true
            else:
                # XXX: Support object eq comparison.
                if not builtin_eq_atom(prev, el).bool_val:
                    return false
        prev = el
    return true

def builtin_eq_atom(left, right):
    if isinstance(left, Int) and isinstance(right, Int) and left.int_val == right.int_val:
        return true
    elif isinstance(left, Int) and isinstance(right, Float) and float(left.int_val) == right.float_val:
        return true
    elif isinstance(left, Float) and isinstance(right, Int) and left.float_val == float(right.int_val):
        return true
    elif isinstance(left, Float) and isinstance(right, Float) and left.float_val == right.float_val:
        return true
    elif isinstance(left, Str) and isinstance(right, Str) and left.str_val == right.str_val:
        return true
    elif isinstance(left, Null) and isinstance(right, Null):
        return true
    elif isinstance(left, Bool) and isinstance(right, Bool) and left.bool_val == right.bool_val:
        return true
    else:
        return false

def builtin_io_puts(engine, payload):
    print payload.__str__()

def builtin_str(engine, payload):
    return Str(payload.__str__())

def builtin_abs(engine, payload):
    if isinstance(payload, Int):
        return Int(0-payload.int_val)
    elif isinstance(payload, Float):
        return Float(0-payload.float_val)
    else:
        raise Exception('unknown data type.')

def builtin_all(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type.')
    for el in payload.array_val:
        if not builtin_bool(engine, el).bool_val:
            return false
    return true

def builtin_any(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type.')
    for el in payload.array_val:
        if builtin_bool(engine, el).bool_val:
            return true
    return false

def builtin_bool(engine, payload):
    if isinstance(payload, Null):
        return false
    elif isinstance(payload, Bool) and payload.bool_val == False:
        return false
    else:
        return true

def builtin_bin(engine, payload):
    if not isinstance(payload, Int):
        raise Exception('unknown data type.')
    raise Exception('not supported yet.')
    #return Str(bin(payload.int_val))


def _dirname(path):
    start = len(path) - 1
    while start > 0:
        if path[start] == '/':
            break
        start -= 1
    if start > 0:
        return path[0:start]
    else:
        raise Exception('wrong path')

def builtin_import(engine, payload):
    if not isinstance(payload, Str):
        raise Exception('unknown data type.')
    stack = engine.current_stack()
    executable_path = rabspath(engine.executable)
    pkg = rjoin(_dirname(_dirname(executable_path)), 'pkg')
    path = rjoin(pkg, '%s.ho' % payload.str_val)
    with open(path) as f:
        env = engine.run_module_code(f.read())
        stack = engine.current_stack()
        stack.namespace.update(env.namespace)
        stack.defs.update(env.defs)
    return null

def builtin_cmp(engine, payload):
    if isinstance(payload, Array):
        raise Exception('unknown data type.')

def builtin_len(engine, payload):
    if isinstance(payload, Str):
        return Int(len(payload.str_val))
    elif isinstance(payload, Array):
        return Int(len(payload.array_val))
    elif isinstance(payload, Object):
        return Int(len(payload.object_val))
    else:
        raise Exception('unknown data type.')

def builtin_map(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type.')
    if len(payload.array_val) != 2:
        raise Exception('unknown data type.')
    func_name = payload.array_val[0]
    iterable = payload.array_val[1]
    if not isinstance(func_name, Str):
        raise Exception('unknown data type.')
    if not isinstance(iterable, Array):
        raise Exception('unknown data type.')
    new_array_val = []
    for el in iterable.array_val:
        engine.stack.append(Env())
        macro = """
            eval %s %s
        """ % (func_name.__str__(), el.__str__())
        new_val = engine.run_macro_code(macro)
        new_array_val.append(new_val)
    return Array(new_array_val)

def builtin_filter(engine, payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type.')
    if len(payload.array_val) != 2:
        raise Exception('unknown data type.')
    func_name = payload.array_val[0]
    iterable = payload.array_val[1]
    if not isinstance(func_name, Str):
        raise Exception('unknown data type.')
    if not isinstance(iterable, Array):
        raise Exception('unknown data type.')
    new_array_val = []
    for el in iterable.array_val:
        engine.stack.append(Env())
        macro = """
            eval %s %s
        """ % (func_name.__str__(), el.__str__())
        new_val = engine.run_macro_code(macro)
        if builtin_bool(engine, new_val).bool_val:
            new_array_val.append(el)
    return Array(new_array_val)

def builtin_eval(engine, payload):
    if not isinstance(payload, Str):
        raise Exception('unknown data type')
    engine.stack.append(Env())
    return engine.run_macro_code(payload.str_val)

def builtin_socket_gethostname(engine, payload):
    return socket.hoe_gethostname()

BUILTINS = {
    '+': builtin_plus,
    '-': builtin_minus,
    '*': builtin_mul,
    '/': builtin_div,
    '=': builtin_eq,
    'abs': builtin_abs,
    'all': builtin_all,
    'any': builtin_any,
    'bool': builtin_bool,
    'bin': builtin_bin,
    'eval': builtin_eval,
    'filter': builtin_filter,
    'len': builtin_len,
    'map': builtin_map,
    'import': builtin_import,
    'io.puts': builtin_io_puts,
    'str': builtin_str,
    'socket._gethostname': builtin_socket_gethostname,
    'type': builtin_type,
}

def is_builtin(op):
    return op in BUILTINS

def builtin(engine, op, payload):
    return BUILTINS[op](engine, payload)
