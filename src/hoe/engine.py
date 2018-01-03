# -*- coding: utf-8 -*-

import os

from hoe.runtime import Env
from hoe.interpreter import eval_source_code, eval_statements, eval_module

class Engine(object):

    def __init__(self, executable):
        self.executable = executable
        self.stack = []

    def get_cwd(self):
        return os.getcwd()

    def current_stack(self):
        return self.stack[len(self.stack) - 1]

    def run_module_code(self, source_code):
        env = eval_module(self, source_code)
        return env

    def run_script(self, path):
        try:
            with open(path) as f:
                try:
                    eval_source_code(self, f.read())
                    return 0
                except Exception as e:
                    print e
                    return 1
        except KeyboardInterrupt as e:
            return 1
        except Exception as e:
            print e
            return 1
