import json

import pytest

from hoe.engine import Engine
from hoe.runtime import Env
from hoe.interpreter import eval_source_code
from hoe.runtime import (Env, Type, Int, Float,
                         Str, Bool, Null, Array,
                         Object,
                         null, true, false)


@pytest.fixture
def engine():
    return Engine('./src/targethoe.py')

def test_value_int(engine):
    val = eval_source_code(engine, "value 1")
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_value_float(engine):
    val = eval_source_code(engine, "value 1.0")
    assert isinstance(val, Float)
    assert val.float_val == 1.0

def test_value_str(engine):
    val = eval_source_code(engine, 'value "hello, world"')
    assert isinstance(val, Str)
    assert val.str_val == "hello, world"

def test_value_array(engine):
    val = eval_source_code(engine, 'value []')
    assert isinstance(val, Array)
    assert val.array_val == []

def test_value_object(engine):
    val = eval_source_code(engine, 'value {}')
    assert isinstance(val, Object)
    assert val.object_val == {}

def test_value_object_with_kv(engine):
    val = eval_source_code(engine, 'value {"key": "value"}')
    assert isinstance(val, Object)
    items = val.object_val.items()
    assert items[0][0] == "key"
    assert items[0][1].str_val == "value"

def test_identifier_for_value(engine):
    val = eval_source_code(engine, '''
    a: value 1
    value a
    ''')
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_empty_begin_end_statement(engine):
    val = eval_source_code(engine, """
        begin
        end
    """)
    assert isinstance(val, Null)

def test_begin_end_has_one_statement_inside(engine):
    val = eval_source_code(engine, """
        begin
        value 1
        end
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_begin_end_has_multiple_statements(engine):
    val = eval_source_code(engine, """
        begin
        a: value 1
        value a
        end
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_identifier_for_begin_end_statement(engine):
    val = eval_source_code(engine, """
        x: begin
            value 1
        end
        value x
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_eval_plus_int(engine):
    val = eval_source_code(engine, """
        eval "+" [0, 1]
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_eval_plus_float(engine):
    val = eval_source_code(engine, """
        eval "+" [0, 1.0]
    """)
    assert isinstance(val, Float)
    assert val.float_val == 1.0

def test_eval_plus_string(engine):
    val = eval_source_code(engine, """
        eval "+" ["hello", ", ", "world"]
    """)
    assert isinstance(val, Str)
    assert val.str_val == "hello, world"

def test_identifier_for_eval_source_code(engine):
    val = eval_source_code(engine, """
        s0: value "hello"
        s1: value ", "
        s2: value "world"
        eval "+" [s0, s1, s2]
    """)
    assert isinstance(val, Str)
    assert val.str_val == "hello, world"

# def test_send_plus_need_same_types(engine):
    # val = eval_source_code(engine, """
        # eval "+" [1, "a"]
    # """)
    # assert isinstance(val, Str)
    # assert val.str_val == "hello, world"

def test_define_def_and_payload(engine):
    val = eval_source_code(engine, """
        proc "+1"
            eval "+" [1, $]
        end

        eval "+1" 0
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

# def test_nested_def_unsupported(engine):
    # with pytest.raises(Exception):
        # eval_source_code(engine, """
            # def "+1"
                # def "+2"
                # end
            # end
        # """)


def test_basic_cond(engine):
    val = eval_source_code(engine, """
        cond
            value false
                value "Never executed."
            value true
                value "Gotcha."
        end
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_cond_int_as_bool(engine):
    val = eval_source_code(engine, """
        cond
            value 1
                value "Gotcha."
            value true
                value "Never executed."
        end
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_identifier_for_cond(engine):
    val = eval_source_code(engine, """
        ret: cond
            value true
                value "Gotcha."
        end
        value ret
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_iter_int(engine):
    val = eval_source_code(engine, """
        y: value 0
        x: iter 3
            y: eval "+" [y, x]
        end
        value y
    """)
    assert isinstance(val, Int)
    assert val.int_val == 3 # 0 + 1 + 2

def test_iter_str(engine):
    val = eval_source_code(engine, """
        y: value ""
        x: iter "abc"
            y: eval "+" [y, x]
        end
        value y
    """)
    assert isinstance(val, Str)
    assert val.str_val == "abc" # "" + "a" + "b" + "c"

def test_iter_array(engine):
    val = eval_source_code(engine, """
        y: value 0
        x: iter [1, 2, 3]
            y: eval "+" [y, x]
        end
        value y
    """)
    assert isinstance(val, Int)
    assert val.int_val == 6 # 0 + 1 + 2 + 3

def test_fib(engine):
    val = eval_source_code(engine, """
        proc "fib"
            cond
                eval "=" [$, 0]
                    value 0
                eval "=" [$, 1]
                    value 1
                value true
                    begin
                        a: eval "-" [$, 1]
                        b: eval "fib" a
                        c: eval "-" [$, 2]
                        d: eval "fib" c
                        eval "+" [b, d]
                    end
            end
        end

        eval "fib" 10
    """)
    assert isinstance(val, Int)
    assert val.int_val == 55

def test_pow(engine):
    val = eval_source_code(engine, """
        proc "**"
            pow: value 1
            iter $[1]
                pow: eval "*" [pow, $[0]]
            end
            value pow
        end
        eval "**" [2, 10]
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1024

def test_eval_type(engine):
    val = eval_source_code(engine, """
        eval "type" 1
    """)
    assert val.str_val == 'int'
    val = eval_source_code(engine, """
        eval "type" 1.0
    """)
    assert val.str_val == 'float'
    val = eval_source_code(engine, """
        eval "type" "hello, world"
    """)
    assert val.str_val == 'str'
    val = eval_source_code(engine, """
        eval "type" true
    """)
    assert val.str_val == 'bool'
    val = eval_source_code(engine, """
        eval "type" null
    """)
    assert val.str_val == 'null'
    val = eval_source_code(engine, """
        eval "type" []
    """)
    assert val.str_val == 'array'
    val = eval_source_code(engine, """
        eval "type" {}
    """)
    assert val.str_val == 'object'

def test_minus_int(engine):
    val = eval_source_code(engine, """
        eval "-" [3, 2]
    """)
    assert val.int_val == 1

def test_minus_float(engine):
    val = eval_source_code(engine, """
        eval "-" [3, 2.0]
    """)
    assert val.float_val == 1.0

def test_mul_int(engine):
    val = eval_source_code(engine, """
        eval "*" [3, 2]
    """)
    assert val.int_val == 6

def test_mul_float(engine):
    val = eval_source_code(engine, """
        eval "*" [3, 2.0]
    """)
    assert val.float_val == 6.0

def test_div_int(engine):
    val = eval_source_code(engine, """
        eval "/" [3, 2]
    """)
    assert val.int_val == 1

def test_div_float(engine):
    val = eval_source_code(engine, """
        eval "/" [3, 2.0]
    """)
    assert val.float_val == 1.5

def test_eq(engine):
    val = eval_source_code(engine, """
        eval "=" [1, 1]
    """)
    assert val.bool_val == True

    val = eval_source_code(engine, """
        eval "=" [1.0, 1.0, 1.0]
    """)
    assert val.bool_val == True

    val = eval_source_code(engine, """
        eval "=" ["hello", "hello"]
    """)
    assert val.bool_val == True

    val = eval_source_code(engine, """
        eval "=" ["hello", "hello, world"]
    """)
    assert val.bool_val == False

def test_builtin_eval_value(engine):
    val = eval_source_code(engine, """
        eval "eval" "value 1"
    """)
    assert val.int_val == 1

def test_value_str_with_value_inside(engine):
    val = eval_source_code(engine, r"""
        value "\"hello, world\""
    """)
    assert val.str_val == r'\"hello, world\"'

def test_payload_object_str_index(engine):
    val = eval_source_code(engine, """
        object: value {"key": {"key": "value"}}
        value object["key"]["key"]
    """)
    assert val.str_val == "value"

def test_payload_array_int_index(engine):
    val = eval_source_code(engine, """
        array: value [[1, 2, 3]]
        value array[0][0]
    """)
    assert val.int_val == 1

def test_builtin_len(engine):
    val = eval_source_code(engine, """
        arr0_len: eval "len" []
        arr1_len: eval "len" [0]
        str0_len: eval "len" ""
        str1_len: eval "len" "a"
        obj0_len: eval "len" {}
        obj1_len: eval "len" {"key": "value"}
        value [arr0_len, arr1_len, str0_len, str1_len, obj0_len, obj1_len]
    """)
    lens = [el.int_val for el in val.array_val]
    assert lens == [0, 1, 0, 1, 0, 1]

def test_builtin_map(engine):
    val = eval_source_code(engine, """
        proc "+1" eval "+" [$, 1] end
        eval "map" ["+1", [1, 2, 3]]
    """)
    vals = [el.int_val for el in val.array_val]
    assert vals == [2, 3, 4]

def test_builtin_filter(engine):
    val = eval_source_code(engine, """
        proc "0?" eval "=" [$, 0] end
        eval "filter" ["0?", [0, 1, 0, 1]]
    """)
    vals = [el.int_val for el in val.array_val]
    assert vals == [0, 0]
