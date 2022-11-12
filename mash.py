#!/usr/bin/python3
"""
Mash interpreter
"""
__author__ = "Marek Sedlacek"
__date__ = "September 2022"
__version__ = "0.2.0"
__email__ = "mr.mareksedlacek@gmail.com"

import argparse
import interpreter
import sys
from pathlib import Path
import mash_exceptions as mex
from lark.exceptions import LarkError

def print_version():
    """
    Prints Mash version
    """
    print("Mash {}".format(__version__))

class Mash:
    """
    Class that is to be extended by all interpreter parts
    """

    def error(self, msg, code=1):
        """
        Prints error and exits with passed in code
        """
        print("Error: {}.".format(msg), file=sys.stderr)
        exit(code)

class Initializer():
    """
    Main class that intializes all needed resources and handles arguments
    """

    def __init__(self, argparser):
        """
        Constructor
        """
        # Argument handling
        self.argparser = argparser
        self.add_arguments(argparser)
        self.opts = self.argparser.parse_args()
        if self.opts.lib_path is None:
            self.opts.lib_path = [Path(".")]
        else:
            self.opts.lib_path = [Path(i) for sublist in self.opts.lib_path for i in sublist]
        # TODO: Change it so that the lib is not read from a file and parsed?
        self.libmash_path = "libmash.ms"
        # --version
        if self.opts.print_version:
            print_version()
            exit(0)
        self.code = self.opts.code
        # If no code was passed on the command line then open stdin
        if self.code is None:
            if self.opts.mash_file is None:
                # Stdin
                self.code = sys.stdin.read()
            else:
                # File passed in
                with open(self.opts.mash_file, 'r', encoding='utf-8') as mash_file:
                    self.code = mash_file.read()
        if not self.opts.no_libmash:
            with open(self.libmash_path, 'r', encoding='utf-8') as mashlib_file:
                self.libmash_code = mashlib_file.read()
        else:
            self.libmash_code = None

    def interpret(self):
        """
        Starts code interpretation
        """
        interpreter.interpret(self.opts, self.code, self.libmash_code)

    def add_arguments(self, argparser):
        """
        Adds arguments to the argparser
        """
        argparser.add_argument('--version', action='store_true', dest='print_version',
                                help='Prints interpreter version to the output.')
        argparser.add_argument('-e', dest='code', default=None,
                                help='Mash code.')
        argparser.add_argument('-v', dest='verbose', default=False, action='store_true',
                                help='Verbose output for debugging.')
        argparser.add_argument('-s', dest='code_only', default=False, action='store_true',
                                help='Parse and output generated code.')
        argparser.add_argument('mash_file', default=None, nargs='?',
                                help='File with Mash code.')
        argparser.add_argument('--parse-only', action='store_true', dest='parse_only',
                                help='Runs only the parser.')
        argparser.add_argument('--no-libmash', action='store_true', default=False, dest='no_libmash',
                                help='Does not include libmash.')
        argparser.add_argument('-l', '--lib-path', action='append', help='Path to folders to search for imports', 
                                required=False, default=None, dest='lib_path', nargs='+')


    def error(self, msg):
        """
        Prints error to the stderr and fails
        """
        print("Error: {}.".format(msg), file=sys.stderr)
        exit(1)

def format_lark_ex(e, code, fname):
    msg = str(e).split("\n")[0]
    cntx = e.get_context(code).split("\n")
    empty = str(" ").rjust(5)
    fname = fname if fname is not None else ""

    print(f"{fname}:{e.line}:{e.column}: Error: {msg}.\n{str(e.line).rjust(5)} | {cntx[0]}\n{empty} | {cntx[1]}", file=sys.stderr)
    exit(1)

def format_ex(msg, code, fname):
    fname = fname if fname is not None else ""
    print(f"{fname}: Error: {msg}.", file=sys.stderr)
    exit(1)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Mash interpreter")
    initializer = Initializer(argparser)
    try:
        initializer.interpret()
    except mex.FlowControlReturn:
        format_ex("'return' outside of a function.", initializer.code, initializer.opts.mash_file)
    except mex.FlowControlBreak:
        format_ex("'break' outside of a loop.", initializer.code, initializer.opts.mash_file)
    except mex.FlowControlContinue:
        format_ex("'continue' outside of a loop", initializer.code, initializer.opts.mash_file)
    except mex.MashException as e:
        format_ex(str(e), initializer.code, initializer.opts.mash_file)
    except LarkError as e:
        if getattr(e, "get_context", None) is not None:
            format_lark_ex(e, initializer.code, initializer.opts.mash_file)
        else:
            # Chained
            format_ex(e.orig_exc, initializer.code, initializer.opts.mash_file)
    