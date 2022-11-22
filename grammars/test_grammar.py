from lark import Lark
from sys import stdin

grammar = None
with open("mash.lark", "r") as gfile:
    grammar = gfile.read()

print(grammar)

mash_parser = Lark(grammar, start="start", parser='lalr')

print("")
txt = stdin.read()
print("")
print(mash_parser.parse(txt).pretty())