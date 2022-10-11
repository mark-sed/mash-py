"""
Internal implementation for libmash functions
@version: 0.0.1
"""
from copy import copy
import random

import mash_types as types

def bitand_2(a, b):
    return a & b

def bitor_2(a, b):
    return a | b

def bitxor_2(a, b):
    return a ^ b

def bitnot_1(a):
    return ~a

def lshift_2(a, count):
    return a << count

def rshift_2(a, count):
    return a >> count

def zip_2(l1, l2):
    return [types.List([a, b]) for a, b in zip(l1, l2)]

def shuffle_1(l):
    retv = copy(l)
    random.shuffle(retv)
    return retv