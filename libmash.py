"""
Internal implementation for libmash functions
@version: 0.0.1
"""
from copy import copy
import random
import math

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

def reverse_1(l):
    retv = copy(l)
    retv.reverse()
    return retv

def cos_1(x):
    return math.cos(x)

def sin_1(x):
    return math.sin(x)

def tan_1(x):
    return math.tan(x)

def acos_1(x):
    return math.acos(x)

def asin_1(x):
    return math.asin(x)

def atan_1(x):
    return math.atan(x)

def atan_2(y, x):
    return math.atan2(y, x)
