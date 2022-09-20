#!/usr/bin/python3
"""
Mash interpreter
"""
__author__ = "Marek Sedlacek"
__date__ = "September 2022"
__version__ = "0.0.1"
__email__ = "mr.mareksedlacek@gmail.com"

import shlex
import argparse
import interpreter
import sys

def print_version():
    """
    Prints Mash version
    """
    print("Mash {}".format(__version__))

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
        # --version
        if self.opts.print_version:
            print_version()
            exit(0)
        self.code = self.opts.code
        # If no code was passed on the command line then open stdin
        if self.code is None:
            if self.opts.mash_file is None:
                # Stdin
                self.code = sys.stdin.readlines()
            else:
                # File passed in
                with open(self.opts.mash_file, 'r', encoding='utf-8') as mash_file:
                    self.code = mash_file.readlines()
        else:
            # Parse new lines even in the argument
            self.code = self.code.split('\n')
        print(self.code)

    def add_arguments(self, argparser):
        """
        Adds arguments to the argparser
        """
        argparser.add_argument('--version', action='store_true', dest='print_version',
                                help='Prints interpreter version to the output.')
        argparser.add_argument('-e', dest='code', default=None,
                                help='Mash code.')
        argparser.add_argument('mash_file', default=None, nargs='?',
                                help='File with Mash code.')

    def error(self, msg):
        """
        Prints error to the stderr and fails
        """
        print("Error: {}.".format(msg), file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Mash interpreter")
    initializer = Initializer(argparser)
    