'''
Created on 6 févr. 2015

@author: dvaumoron
'''

import inspect
import functools

def Singleton(cls):
    @functools.wraps(cls)
    def getInstance(*args, **kwargs):
        if getInstance.instance is None:
            getInstance.instance = cls(*args, **kwargs)
        return getInstance.instance
    getInstance.instance = None
    return getInstance

class CacheSetter:
    def __init__(self, ci, key):
        self.ci = ci
        self.key = key
    def set(self, value):
        self.ci.cache[self.key] = value
        return self.ci

class CacheInitializer:
    def __init__(self):
        self.cache = {}
    def call(self, *args, **kwargs):
        return CacheSetter(self, str(args) + str(kwargs))

def memoizeWith(cache):
    def memoize(function):
        @functools.wraps(function)
        def memoized(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                res = cache[key]
            else:
                res = cache[key] = function(*args, **kwargs)
            return res
        memoized.cache = cache
        return memoized
    return memoize

def memoize(function):
    return memoizeWith({})(function)

def buildDecorator(cls, slots=False):
    c = PrintableClass(cls.__name__ + "Decorator")
    if slots:
        c.addSlots("'inner'")
    m = PrintableMethod("__init__", inspect.ArgSpec(["self", "inner"], None, None, None))
    m.addInstruction("self.inner = inner")
    c.addMethod(m)
    for name in dir(cls):
        attr = getattr(cls, name)
        if (inspect.ismethod(attr) or inspect.isfunction(attr)) and name != "__init__":
            argspec = inspect.getargspec(attr)
            m = PrintableMethod(name, argspec)
            instruction = StringBuffer()
            instruction.append("return self.inner.").append(name).append("(")
            recopyArgsWithoutSelf(argspec, instruction)
            instruction.append(")")
            m.addInstruction(instruction)
            c.addMethod(m)
        elif isinstance(attr, property):
            m = PrintableMethod(name, inspect.ArgSpec(["self"], None, None, None))
            m.addDecorator("property")
            instruction = StringBuffer()
            instruction.append("return self.inner.").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
            m = PrintableMethod(name, inspect.ArgSpec(["self", name], None, None, None))
            m.addDecorator(name + ".setter")
            instruction = StringBuffer()
            instruction.append("self.inner.").append(name).append(" = ").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
            m = PrintableMethod(name, inspect.ArgSpec(["self"], None, None, None))
            m.addDecorator(name + ".deleter")
            instruction = StringBuffer()
            instruction.append("del self.inner.").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
    return str(c)

def buildComposite(cls, slots=True):
    c = PrintableClass(cls.__name__ + "Composite")
    if slots:
        c.addSlots("'inners'")
    m = PrintableMethod("__init__", inspect.ArgSpec(["self"], None, None, None))
    m.addInstruction("self.inners = []")
    c.addMethod(m)
    m = PrintableMethod("addInner", inspect.ArgSpec(["self", "inner"], None, None, None))
    m.addInstruction("self.inners.append(inner)")
    c.addMethod(m)
    for name in dir(cls):
        attr = getattr(cls, name)
        if (inspect.ismethod(attr) or inspect.isfunction(attr)) and name != "__init__":
            argspec = inspect.getargspec(attr)
            m = PrintableMethod(name, argspec)
            m.addInstruction("for inner in self.inners:")
            instruction = StringBuffer()
            instruction.append("\tinner.").append(name).append("(")
            recopyArgsWithoutSelf(argspec, instruction)
            instruction.append(")")
            m.addInstruction(instruction)
            c.addMethod(m)
        elif isinstance(attr, property):
            m = PrintableMethod(name, inspect.ArgSpec(["self"], None, None, None))
            m.addDecorator("property")
            instruction = StringBuffer()
            instruction.append("return self.inners[0].").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
            m = PrintableMethod(name, inspect.ArgSpec(["self", name], None, None, None))
            m.addDecorator(name + ".setter")
            m.addInstruction("for inner in self.inners:")
            instruction = StringBuffer()
            instruction.append("\tinner.").append(name).append(" = ").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
            m = PrintableMethod(name, inspect.ArgSpec(["self"], None, None, None))
            m.addDecorator(name + ".deleter")
            m.addInstruction("for inner in self.inners:")
            instruction = StringBuffer()
            instruction.append("\tdel inner.").append(name)
            m.addInstruction(instruction)
            c.addMethod(m)
    return str(c)

def recopyArgsWithoutSelf(argspec, buffer):
    first = True
    for arg in argspec.args:
        if arg == "self":
            continue
        elif first:
            first = False
        else:
            buffer.append(", ")
        buffer.append(arg)
    varargs = argspec.varargs
    if varargs is not None:
        if first:
            first = False
        else:
            buffer.append(", ")
        buffer.append("*").append(varargs)
    keywords = argspec.keywords
    if keywords is not None:
        if not first:
            buffer.append(", ")
        buffer.append("**").append(keywords)

class Observable:
    def __init__(self):
        self.observators = set()
    def registerObservator(self, observator):
        self.observators.add(observator)
    def unregisterObservator(self, observator):
        self.observators.discard(observator)
    def notify(self):
        for observator in self.observators:
            observator.notify(self)

class StringBuffer:
    __slots__ = "buffer"
    def __init__(self):
        self.buffer = []
    def append(self, e):
        if isinstance(e, StringBuffer):
            self.buffer += e.buffer
        else:
            self.buffer.append(str(e))
        return self
    def __str__(self):
        return ''.join(self.buffer)

class PrintableClass:
    __slots__ = ("decorators", "name", "methods", "slots")
    def __init__(self, name):
        self.decorators = []
        self.name = name
        self.slots = None
        self.methods = []
    def addDecorator(self, decorator):
        self.decorators.append(decorator)
    def addSlots(self, slots):
        self.slots = slots
    def addMethod(self, method):
        self.methods.append(method)
    def toStringBuffer(self):
        buffer = StringBuffer()
        if self.decorators:
            for decorator in self.decorators:
                buffer.append("@").append(decorator).append("\n")
        buffer.append("class ").append(self.name).append(":\n")
        if self.slots is not None:
            buffer.append("\t__slots__ = ").append(self.slots).append("\n")
        for method in self.methods:
            buffer.append(method.toStringBuffer())
        return buffer
    def __str__(self):
        return str(self.toStringBuffer())

class PrintableMethod:
    __slots__ = ("decorators", "name", "argspec", "instructions")
    def __init__(self, name, argspec):
        self.decorators = []
        self.name = name
        self.argspec = argspec
        self.instructions = []
    def addDecorator(self, decorator):
        self.decorators.append(decorator)
    def addInstruction(self, instruction):
        self.instructions.append(instruction)
    def toStringBuffer(self):
        buffer = StringBuffer()
        if self.decorators:
            for decorator in self.decorators:
                buffer.append("\t@").append(decorator).append("\n")
        buffer.append("\tdef ").append(self.name).append("(")
        first = True
        args = self.argspec.args
        defaults = self.argspec.defaults
        lenArgs = len(args)
        if defaults is None:
            lenDefaults = 0
        else:
            lenDefaults = len(defaults)
        indexStartDefaults = lenArgs - lenDefaults
        for index, arg in enumerate(args):
            if first:
                first = False
            else:
                buffer.append(", ")
            buffer.append(arg)
            if index >= indexStartDefaults:
                buffer.append("=").append(defaults[index - indexStartDefaults])
        varargs = self.argspec.varargs
        if varargs is not None:
            if first:
                first = False
            else:
                buffer.append(", ")
            buffer.append("*").append(varargs)
        keywords = self.argspec.keywords
        if keywords is not None:
            if not first:
                buffer.append(", ")
            buffer.append("**").append(keywords)
        buffer.append("):\n")
        for instruction in self.instructions:
            buffer.append("\t\t").append(instruction).append("\n")
        return buffer
    def __str__(self):
        return str(self.toStringBuffer())

class CurriedFunction:
    def __init__(self, minargs, function, args, kwargs):
        self.minargs = minargs
        self.function = function
        self.args = args
        self.kwargs = kwargs
    def __call__(self, *args, **kwargs):
        newArgs = self.args + args
        newKwargs = dict(list(self.kwargs.items()) + list(kwargs.items()))
        if len(newArgs) + len(newKwargs) >= self.minargs:
            return self.function(*newArgs, **newKwargs)
        else:
            return CurriedFunction(self.minargs, self.function, newArgs, newKwargs)

def curryN(minargs):
    def curry(function):
        @functools.wraps(function)
        def curried(*args, **kwargs):
            if len(args) + len(kwargs) >= minargs:
                return function(*args, **kwargs)
            else:
                return CurriedFunction(minargs, function, args, kwargs)
        return curried
    return curry

def curry(function):
    return curryN(len(inspect.getargspec(function).args))(function)
