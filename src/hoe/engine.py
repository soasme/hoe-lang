# -*- coding: utf-8 -*-

from hoe.runtime import Env
from hoe.interpreter import eval_source_code, eval_statements

class Engine(object):

    def __init__(self):
        self.stack = []

    def current_stack(self):
        return self.stack[len(self.stack) - 1]

    def run_script(self, path):
        try:
            with open(path) as f:
                try:
                    eval_source_code(self, f.read())
                    return 0
                except Exception as e:
                    print e
                    return 1
        except Exception as e:
            print e
            return 1
