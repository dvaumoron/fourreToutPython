
from __future__ import annotations

import collections
import functools
import heapq
import itertools
import json
import logging
import math
import operator
import random
import types
import codi

logging.basicConfig(level=logging.DEBUG)
debug_printer = codi.logger_to_printer(logging.getLogger(), logging.DEBUG)

class Memoize:
    __slots__ = ("func", "cache")
    def __init__(self, func, cache=None):
        self.func = func
        if cache is None:
            self.cache = {}
        else:
            self.cache = cache
    def __call__(self, *args, **kwArgs):
        key = args + tuple(kwArgs.items())
        try:
            res = self.cache[key]
        except KeyError:
            res = self.cache[key] = self.func(*args, **kwArgs)
        return res
    def __str__(self):
        return f"Memoize({str(self.func)}, {str(self.cache)})"

ci = codi.CacheInit()
ci(0).set(1)

@codi.memoize_with(ci.cache)
@codi.print_call
def fact(n):
    return n * fact(n - 1)

def fact2(n):
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res

def fact3(n):
    return functools.reduce(operator.mul, range(2, n + 1), 1)

@codi.terminal_rec
@codi.print_call
def fact4(n, acc=1):
    if n < 2:
        return acc
    else:
        return fact4(n - 1, n * acc)

ci = codi.CacheInit()
ci(0).set(0)
ci(1).set(1)

@codi.print_call_with(debug_printer)
def fib(n):
    return fib(n - 1) + fib(n - 2)

fib = Memoize(fib, ci.cache)

def fib2(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a

class DoubleAppendDecorator(codi.Decorator):
    __slots__ = ()
    def append(self, value):
        superAppend = super().__getattr__("append")
        superAppend(value)
        superAppend(value)

def _custom_hook(d):
    if "__complex__" in d:
        return complex(d["real"], d["imag"])
    elif "__set__" in d:
        return set(d["values"])
    elif "__tuple__" in d:
        return tuple(d["values"])
    elif "__frozenset__" in d:
        return frozenset(d["values"])
    else:
        return d

decode_json = functools.partial(json.loads, object_hook=_custom_hook)

def _prepare_json(o):
    if isinstance(o, dict):
        return {k: _prepare_json(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_prepare_json(e) for e in o]
    elif isinstance(o, complex):
        return {"__complex__": True, "real": o.real, "imag": o.imag}
    elif isinstance(o, set):
        return {"__set__": True, "values": [_prepare_json(e) for e in o]}
    elif isinstance(o, tuple):
        return {"__tuple__": True, "values": [_prepare_json(e) for e in o]}
    elif isinstance(o, frozenset):
        return {"__frozenset__": True, "values": [_prepare_json(e) for e in o]}
    else:
        return o

json_dumps = json.dumps

def encode_json(o):
    return json_dumps(_prepare_json(o))

ci = codi.CacheInit()
ci(1).set(False)
ci(2).set(True)

@codi.memoize_with(ci.cache)
def prime(n):
    if n % 2 == 0:
        return False
    i = 3
    r = n**0.5
    while i <= r:
        if n % i == 0:
            return False
        i += 2
    return True

def print_primes():
    print([k[0] for k, v in prime.cache.items() if v])

def decompose_prime(n):
    c = collections.Counter()
    while n % 2 == 0:
        n //= 2
        c[2] += 1
    i = 3
    while i <= n**0.5:
        while n % i == 0:
            n //= i
            c[i] += 1
        i += 2
    if n != 1:
        c[n] += 1
    return c

def print_decompose(n):
    l = []
    lAppend = l.append
    for k, v in decompose_prime(n).items():
        if v == 1:
            lAppend(str(k))
        else:
            lAppend(f"{k}**{v}")
    print(n, "=", " * ".join(l))

def multiple(n):
    c = collections.Counter()
    for i in range(2, n+1):
        c |= decompose_prime(i)
    res = 1
    for k, v in c.items():
        res *= k**v
    return res

def _diviseur(n):
    yield 1
    c = decompose_prime(n)
    elements = list(c.elements())
    for i in range(1, len(elements)):
        for t in itertools.combinations(elements, i):
            res = 1
            for j in t:
                res *= j
            yield res
    yield n

def diviseur(n):
    return sorted(set(_diviseur(n)))

ns = types.SimpleNamespace()

class TestField:
    x = codi.Typed(int, codi.Field())
    y = codi.DefaultValue(0, codi.RevealAccess(codi.Field()))
    z = codi.RevealAccess(codi.Typed(int, codi.Field()), debug_printer)
    t = codi.ClassField()
    a = codi.DefaultValue(0, codi.RevealAccess(codi.ClassField()))
    b = codi.Typed(int, codi.ClassField())
    c = codi.RevealAccess(codi.Typed(int, codi.ClassField()))
    def getD(self):
        return self._d
    def setD(self, value):
        self._d = value
    d = codi.RevealAccess(property(getD, setD))
    @codi.ClassProperty
    def e(klass):
        print("Method get e")
        return klass._e
    @e.setter
    def e(klass, value):
        print("Method set e")
        klass._e = value
    @e.deleter
    def e(klass):
        print("Method delete e")
        del klass._e
    @codi.StaticProperty
    def f():
        print("Method get f")
        return _f
    @f.setter
    def f(value):
        global _f
        print("Method set f")
        _f = value
    @f.deleter
    def f():
        global _f
        print("Method delete f")
        del _f
    def __init__(self):
        self.inner = types.SimpleNamespace()
    g = codi.RevealAccess(codi.DelegateField("inner"))
    h = codi.RevealAccess(codi.ProxyField(ns))

class Arbre:
    __slots__ = ("label", "gauche", "droit")
    def __init__(self, label):
        self.label = label
        self.gauche = None
        self.droit = None
    def parcours_en_profondeur(self):
        if self.gauche is not None:
            yield from self.gauche.parcours_en_profondeur()
        yield self.label
        if self.droit is not None:
            yield from self.droit.parcours_en_profondeur()
    def parcours_en_largeur(self):
        d = collections.deque()
        d.append(self)
        while len(d) > 0:
            n = d.popleft()
            yield n.label
            if n.gauche is not None:
                d.append(n.gauche)
            if n.droit is not None:
                d.append(n.droit)

@codi.type_check
def func1(a: int, b: float) -> float:
    return a + b

@codi.type_check
def func2(a: int, b: float) -> float:
    pass

@codi.type_check_class
class CheckedClass:
    def f(self, a: int, b: int) -> int:
        return a + b

@codi.print_call
def tri_fusion(d):
    if len(d) < 2:
        return d
    else:
        d1, d2 = split(d)
        return fusion(tri_fusion(d1), tri_fusion(d2))

def split(d):
    d1 = []
    d1_append = d1.append
    d2 = []
    d2_append = d2.append
    b = True
    for e in d:
        if b:
            b = False
            d1_append(e)
        else:
            b = True
            d2_append(e)
    return d1, d2

@codi.print_call
def fusion(d1, d2):
    d = []
    d_append = d.append
    len_d1 = len(d1)
    len_d2 = len(d2)
    i = 0
    j = 0
    while len_d1 > i or len_d2 > j:
        if len_d2 == j or len_d1 > i and d1[i] < d2[j]:
            d_append(d1[i])
            i += 1
        else:
            d_append(d2[j])
            j += 1
    return d

@codi.print_call
def tri_rapide(l):
    if len(l) < 2:
        return l
    else:
        l1, pivot, l2 = split_rapide(l)
        return fusion_rapide(tri_rapide(l1), pivot, tri_rapide(l2))

def split_rapide(l):
    l1 = []
    l2 = []
    l1_append = l1.append
    l2_append = l2.append
    it = iter(l)
    pivot = next(it)
    for value in it:
        if value < pivot:
            l1_append(value)
        else:
            l2_append(value)
    return l1, pivot, l2

@codi.print_call
def fusion_rapide(l1, pivot, l2):
    l = []
    l.extend(l1)
    l.append(pivot)
    l.extend(l2)
    return l

def tri_bulle(l):
    b = True
    lenl = len(l)
    while b:
        b = False
        print(l)
        lenl -= 1
        for i in range(lenl):
            ip1 = i + 1
            if l[i] > l[ip1]:
                b = True
                l[i], l[ip1] = l[ip1], l[i]

@codi.print_call
def tri_insertion(d):
    if len(d) < 2:
        return d
    else:
        e = d.pop()
        return insertion(e, tri_insertion(d))

@codi.print_call
def insertion(e, d):
    res = collections.deque()
    while len(d) > 0 and e > d[0]:
        res.append(d.popleft())
    res.append(e)
    res.extend(d)
    return res

class Tas:
    __slots__ = ("label", "gauche", "droit")
    def __init__(self, value):
        self.label = value
        self.gauche = None
        self.droit = None
    def add(self, value):
        if value < self.label:
            if self.gauche is None:
                self.gauche = Tas(value)
            else:
                self.gauche.add(value)
        else:
            if self.droit is None:
                self.droit = Tas(value)
            else:
                self.droit.add(value)
    def __iter__(self):
        if self.gauche is not None:
            yield from self.gauche
        yield self.label
        if self.droit is not None:
            yield from self.droit
    def __str__(self):
        return f"Tas({self.gauche}, {self.label}, {self.droit})"

def tri_tas(l):
    if len(l) < 2:
        return l
    it = iter(l)
    t = Tas(next(it))
    print(t)
    for e in it:
        t.add(e)
        print(t)
    return list(t)

def tri_min(l):
    lenl = len(l) - 1
    for i in range(lenl):
        print(l)
        min = lenl
        for j in range(i, lenl):
            if l[j] < l[min]:
                min = j
        l[min], l[i] = l[i], l[min]
    print(l)

def heapsort(l):
    h = []
    for value in l:
        heapq.heappush(h, value)
        print(h)
    res = []
    res_append = res.append
    for i in range(len(h)):
        res_append(heapq.heappop(h))
        print(h)
    return res

def char_range(start, stop, step = 1):
    startI = ord(start)
    stopI = ord(stop) + 1
    for i in range(startI, stopI, step):
        yield chr(i)

class CharSlice:
    def __class_getitem__(cls, key):
        if isinstance(key, slice):
            step = key.step
            if step is None:
                l = char_range(key.start, key.stop)
            else:
                l = char_range(key.start, key.stop, step)
            return "".join(l)
        else:
            raise TypeError("wait char slice")

def gen_product(res):
    while True:
        res *= (yield res)

def fact_gen(n):
    it = gen_product(1)
    print(next(it))
    for i in range(2, n+1):
        print(it.send(i))

def adaptable_range(n):
    current = 0
    increment = 1
    while current < n:
        value = (yield current)
        if value is None:
            current += increment
        else:
            increment = value        

def _siracuse(n):
    yield n
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        yield n

def siracuse(n):
    return list(_siracuse(n))

class IntVisitable(int):
    accept = codi.def_accept("int")

class FloatVisitable(float):
    accept = codi.def_accept("float")

class StringVisitable(str):
    accept = codi.def_accept("string")

@codi.static_class
class PrintVisitor:
    def visit_int(i):
        print("int :" , i)
    def visit_float(f):
        print("float :" , f)
    def visit_string(s):
        print("string :" , s)

@codi.delegate("l", ("append", "extend"))
class DList:
    def __init__(self):
        self.l = []

def binome(n, p):
    if p > n or p < 0:
        return 0
    res = 1
    for i in range(p):
        res = (res * (n - i)) // (i + 1)
    return res

class InfiniteList(list):
    __slots__ = ()
    def __getitem__(self, key):
        if isinstance(key, slice):
            return super().__getitem__(key)
        else:
            l = len(self)
            if l == 0:
                raise IndexError("list index out of range")
            elif l == 1:
                return super().__getitem__(0)
            else:
                return super().__getitem__(key % l)
    def __repr__(self):
        return "InfiniteList({})".format(super().__repr__())

exec(codi.macro_dataclass("Position", ["line", "column"]))

exec(codi.macro_square_matrix(3))

rand_value = functools.partial(random.uniform, -1, 1)

exp = math.exp

exec(codi.macro_sigmoid(3))

exec(codi.macro_perceptron(3))

if __name__ == "__main__":
    print(fact(10))
    print(fact2(5))
    print(fact3(3))
    print(fact4(10))
    print(fact)
    print(fact.cache)
    print(fib(10))
    print(fib2(5))
    print(fib)
    print(fib.cache)

    l = []
    ld = codi.RevealAccessDecorator(DoubleAppendDecorator(l), debug_printer)
    ld.append(1)
    ld.append(2)
    ld.append(3)
    ld.remove(2)
    print(l)

    l1 = [-1]
    l2 = [-2]
    l3 = [-3]
    lcBottom = codi.Composite()
    lcBottom.addItem(l1)
    lcBottom.addItem(l2)
    lcTop = codi.Composite()
    lcTop.addItem(lcBottom)
    lcTop.addItem(l3)

    lcTop.append(0)
    lcTop.append(1)
    lcTop.append(2)
    lcTop.append(3)
    lcTop.remove(0)

    print(l1, l2, l3)

    jsonStr = encode_json([0., {"test":({2+1j, 1+2j}, 1)}])
    print(jsonStr)
    print(decode_json(jsonStr))

    for i in range(3,100,2):
        prime(i)
    print_primes()

    print_decompose(1020)
    print_decompose(1176)
    print_decompose(1178)
    print_decompose(1404)
    print_decompose(1406)
    print_decompose(1984)
    print_decompose(2019)
    print_decompose(2520)
    print_decompose(4536)

    print("multiple(10) =", multiple(10))

    print("diviseur(60) =", diviseur(60))

    t = TestField()
    t2 = TestField()
    t.x = 1
    t.y = 2
    t.z = 3
    t.t = 4
    t.a = 5
    t.b = 6
    t.c = 7
    t.d = 8
    t.e = 9
    t.f = 10
    t.g = 11
    t.h = 12
    print("t.x =", t.x)
    print("t.y =", t.y)
    print("t.z =", t.z)
    print("t.t =", t.t)
    print("t2.t =", t2.t)
    print("TestField.t =", TestField.t)
    print("t.a =", t.a)
    print("t2.a =", t2.a)
    print("TestField.a =", TestField.a)
    print("t.b =", t.b)
    print("t2.b =", t2.b)
    print("TestField.b =", TestField.b)
    print("t.c =", t.c)
    print("t2.c =", t2.c)
    print("TestField.c =", TestField.c)
    print("t.d =", t.d)
    print("t.e =", t.e)
    print("t2.e =", t2.e)
    print("TestField.e =", TestField.e)
    print("TestField._e =", TestField._e)
    print("t.f =", t.f)
    print("t2.f =", t2.f)
    print("TestField.f =", TestField.f)
    print("_f =", _f)
    print("t.g =", t.g)
    print("t.inner =", t.inner)
    print("t2.inner =", t2.inner)
    print("t.h =", t.h)
    print("t2.h =", t2.h)
    print("ns =", ns)
    del t.x
    del t.y
    del t.z
    del t.t
    del t.a
    del t.b
    del t.c
    try:
        del t.d
    except AttributeError as ae:
        print("Catched AttributeError :", ae)
    del t.e
    del t.f
    del t.g
    del t.h
    try:
        t.x = "a"
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        t.z = "a"
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        t.b = "a"
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        t.c = "a"
    except TypeError as te:
        print("Catched TypeError :", te)
    print("t.y =", t.y)
    print("t.a =", t.a)

    a = Arbre("racine")
    ag = Arbre("arbre gauche")
    ag1 = Arbre("arbre gauche 1")
    ag2 = Arbre("arbre gauche 2")
    ad = Arbre("arbre droit")
    ad1 = Arbre("arbre droit 1")
    ad2 = Arbre("arbre droit 2")
    f1 = Arbre("feuille 1")
    f2 = Arbre("feuille 2")
    f3 = Arbre("feuille 3")
    f4 = Arbre("feuille 4")
    f5 = Arbre("feuille 5")
    f6 = Arbre("feuille 6")
    f7 = Arbre("feuille 7")
    f8 = Arbre("feuille 8")
    
    a.gauche = ag
    a.droit = ad
    ag.gauche = ag1
    ag.droit = ag2
    ad.gauche = ad1
    ad.droit = ad2
    ag1.gauche = f1
    ag1.droit = f2
    ag2.gauche = f3
    ag2.droit = f4
    ad1.gauche = f5
    ad1.droit = f6
    ad2.gauche = f7
    ad2.droit = f8

    print(list(a.parcours_en_profondeur()))
    print(list(a.parcours_en_largeur()))

    print(func1(1, 2.))
    try:
        func1(1., 1.)
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        func1(1, 1)
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        func1(a=1., b=1.)
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        func1(1, b=1)
    except TypeError as te:
        print("Catched TypeError :", te)
    try:
        func2(1,2.)
    except TypeError as te:
        print("Catched TypeError :", te)

    cc = CheckedClass()
    print(cc.f(1, 2))
    try:
        cc.f(1, 2.)
    except TypeError as te:
        print("Catched TypeError :", te)

    print(tri_fusion([5, 2, 6, 4, 1, 3]))
    print(tri_rapide([5, 2, 6, 4, 1, 3]))
    print("tri_bulle")
    tri_bulle([5, 2, 6, 4, 1, 3])
    print(tri_insertion(collections.deque([5, 2, 6, 4, 1, 3])))
    print(tri_tas([5, 2, 6, 4, 1, 3]))
    print("tri_min")
    tri_min([5, 2, 6, 4, 1, 3])
    print("heapsort")
    print(heapsort([5, 2, 6, 4, 1, 3]))

    print(list(char_range('A', 'Z')))
    print(list(char_range('B', 'Z', 2)))
    print(CharSlice['A':'z'])
    print(CharSlice['a':'z':2])

    sd = codi.SliceDict({i:i**2 for i in range(5)})
    print(sd[3])
    print(sd[2:2])
    print(sd[1:2])
    print(sd[2:4])
    try:
        sd[2:2:1]
    except TypeError as te:
         print("Catched TypeError :", te)
    sd2 =  codi.SliceDict({"atchoum": 1, "toto": 2, "baby": 3, "zoro": 4})
    print(sd2[:'n'])
    print(sd2['n':])
    print(sd2[:])
    print(sd2['a':'{'])
    print(sd2['b':'t'])
    print(sd2['b':'u'])

    fact_gen(10)

    it = adaptable_range(10)
    for i in it:
        print(i)
        if i == 5:
            it.send(2)

    print(siracuse(9))

    IntVisitable(1).accept(PrintVisitor)
    FloatVisitable(2.5).accept(PrintVisitor)
    StringVisitable("abc").accept(PrintVisitor)

    dl = DList()
    dl.append(1)
    dl.extend((2, 3))
    print(dl.l)

    for i in range(5):
        print([binome(i, j) for j in range(-1, i + 2)])

    il = InfiniteList([1,2,3])
    print(il)
    print(il[-4], il[10])

    p = Position(1,2)
    print(p)
    p.line = 3
    p.column = 4
    print(p)

    m = SquareMatrix3([0, 1, 2, 3, 4, 5, 6, 7, 8])
    print(m)
    id3 = SquareMatrix3.identity()
    print(id3)
    print(m + id3)
    print(m - id3)
    print(3 * id3)
    print(id3 * 5)
    cm = [1, 2, 3]
    cm2 = m @ cm
    print(cm2) 
    m2 = SquareMatrix3.generate(rand_value)
    print(m2)

    print(sigmoid3(cm))

    p3 = Perceptron3(sigmoid3)
    p3.inner.append(id3)
    p3.inner.append(m)
    p3.inner.append(m2)
    print(p3(cm))
