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
    return Engine()

def test_quote_int(engine):
    val = eval_source_code(engine, "quote 1")
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_quote_float(engine):
    val = eval_source_code(engine, "quote 1.0")
    assert isinstance(val, Float)
    assert val.float_val == 1.0

def test_quote_str(engine):
    val = eval_source_code(engine, 'quote "hello, world"')
    assert isinstance(val, Str)
    assert val.str_val == "hello, world"

def test_quote_array(engine):
    val = eval_source_code(engine, 'quote []')
    assert isinstance(val, Array)
    assert val.array_val == []

def test_quote_object(engine):
    val = eval_source_code(engine, 'quote {}')
    assert isinstance(val, Object)
    assert val.object_val == {}

def test_quote_object_with_kv(engine):
    val = eval_source_code(engine, 'quote {"key": "value"}')
    assert isinstance(val, Object)
    items = val.object_val.items()
    assert items[0][0].str_val == "key"
    assert items[0][1].str_val == "value"

def test_identifier_for_quote(engine):
    val = eval_source_code(engine, '''
    a: quote 1
    quote a
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
        quote 1
        end
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_begin_end_has_multiple_statements(engine):
    val = eval_source_code(engine, """
        begin
        a: quote 1
        quote a
        end
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

def test_identifier_for_begin_end_statement(engine):
    val = eval_source_code(engine, """
        x: begin
            quote 1
        end
        quote x
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
        s0: quote "hello"
        s1: quote ", "
        s2: quote "world"
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

def test_define_proc_and_payload(engine):
    val = eval_source_code(engine, """
        proc "+1"
            eval "+" [1, $]
        end

        eval "+1" 0
    """)
    assert isinstance(val, Int)
    assert val.int_val == 1

# def test_nested_proc_unsupported(engine):
    # with pytest.raises(Exception):
        # eval_source_code(engine, """
            # proc "+1"
                # proc "+2"
                # end
            # end
        # """)


def test_basic_cond(engine):
    val = eval_source_code(engine, """
        cond
            quote false
                quote "Never executed."
            quote true
                quote "Gotcha."
        end
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_cond_int_as_bool(engine):
    val = eval_source_code(engine, """
        cond
            quote 1
                quote "Gotcha."
            quote true
                quote "Never executed."
        end
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_identifier_for_cond(engine):
    val = eval_source_code(engine, """
        ret: cond
            quote true
                quote "Gotcha."
        end
        quote ret
    """)
    assert isinstance(val, Str)
    assert val.str_val == "Gotcha."

def test_iter_int(engine):
    val = eval_source_code(engine, """
        y: quote 0
        x: iter 3
            y: eval "+" [y, x]
        end
        quote y
    """)
    assert isinstance(val, Int)
    assert val.int_val == 3 # 0 + 1 + 2

def test_iter_array(engine):
    val = eval_source_code(engine, """
        y: quote 0
        x: iter [1, 2, 3]
            y: eval "+" [y, x]
        end
        quote y
    """)
    assert isinstance(val, Int)
    assert val.int_val == 6 # 0 + 1 + 2 + 3

def test_fib(engine):
    val = eval_source_code(engine, """
        proc "fib"
            cond
                eval "=" [$, 0]
                    quote 0
                eval "=" [$, 1]
                    quote 1
                quote true
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
            pow: quote 1
            iter $[1]
                pow: eval "*" [pow, $[0]]
            end
            quote pow
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
