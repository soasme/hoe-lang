# -*- coding: utf-8 -*-

class Type(object): pass

class Int(Type):
    def __init__(self, int_val):
        self.int_val = int_val
    def __str__(self):
        return '%d' % self.int_val

class Float(Type):
    def __init__(self, float_val):
        self.float_val = float_val
    def __str__(self):
        return '%f' % self.float_val

class Str(Type):
    def __init__(self, str_val):
        self.str_val = str_val
    def __str__(self):
        return '"%s"' % self.str_val

class Null(Type):
    def __str__(self):
        return 'null'

class Bool(Type):
    def __init__(self, bool_val):
        self.bool_val = bool_val
    def __str__(self):
        return 'true' if self.bool_val else 'false'

class Array(Type):
    def __init__(self, array_val):
        self.array_val = array_val
    def __str__(self):
        return '[%s]' % (', '.join([x.__str__() for x in self.array_val]))

class Object(Type):
    def __init__(self, object_val):
        self.object_val = object_val
    def __str__(self):
        return '{%s}' % (', '.join(['%s: %s' % (k, v.__str__()) for k, v in self.object_val.items()]))

null = Null()
true = Bool(True)
false = Bool(False)

class Env(object):
    def __init__(self):
        self.identifier = '^'
        self.namespace = {}
        self.defs = {}
    def has(self, key):
        return key in self.namespace
    def get(self, key):
        if key in self.namespace:
            return self.namespace[key]
        else:
            raise Exception('undefined label: %s' % key)
    def set(self, key, value):
        self.namespace[key] = value
    def push(self, value):
        if self.identifier != '^':
            self.set(self.identifier, value)
        self.set('^', value)
        self.identifier = '^'
    def present(self):
        return self.get(self.identifier) if self.has(self.identifier) else null
    def define_def(self, def_name, statements):
        self.defs[def_name] = statements
    def has_def(self, def_name):
        return def_name in self.defs
    def get_def(self, def_name):
        return self.defs[def_name]
