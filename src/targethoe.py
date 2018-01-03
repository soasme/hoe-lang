import os
import sys

from rpython.jit.codewriter.policy import JitPolicy

from hoe.engine import Engine

def main(argv):
    engine = Engine(argv[0])
    return engine.run_script(argv[1])

def target(driver, args):
    driver.exe_name = 'hoe'
    return main, None

def jitpolicy(driver):
    return JitPolicy()

if __name__ == '__main__':
    main(sys.argv)
