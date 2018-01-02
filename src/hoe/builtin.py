
from hoe.runtime import (Env, Type, Int, Float,
                         Str, Bool, Null, Array,
                         Object,
                         null, true, false)

def is_builtin(op):
    return op in [
        '+', '-', '*', '/',
        '=', '>', '<', '>=', '<=', '!=',
        'type',
        'io.puts',
    ]

def builtin(op, payload):
    if op == 'type':
        return builtin_type(payload)
    elif op == '+':
        return builtin_plus(payload)
    elif op == '-':
        return builtin_minus(payload)
    elif op == '*':
        return builtin_mul(payload)
    elif op == '/':
        return builtin_div(payload)
    elif op == '=':
        return builtin_eq(payload)
    elif op == 'io.puts':
        return builtin_io_puts(payload)

def builtin_type(payload):
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

def builtin_plus(payload):
    if not isinstance(payload, Array):
        raise Exception('unknown data type')
    if isinstance(payload.array_val[0], Float) or isinstance(payload.array_val[0], Int):
        return builtin_plus_number(payload)
    elif isinstance(payload.array_val[0], Str):
        return builtin_plus_string(payload)
    else:
        raise Exception('unknown element type')

def builtin_plus_number(payload):
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

def builtin_plus_string(payload):
    str_array = [x.str_val for x in payload.array_val]
    return Str(''.join(str_array))

def builtin_minus(payload):
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

def builtin_mul(payload):
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

def builtin_div(payload):
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



def builtin_eq(payload):
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

def builtin_io_puts(payload):
    print payload.__str__()
