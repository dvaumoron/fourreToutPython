
from __future__ import annotations

import collections
import contextvars
import functools
import inspect
import typing

MISSING = object()

def memoize_with(cache):
    "Decorator to cache function result."

    def memoize(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwArgs):
            key = args + tuple(kwArgs.items())
            try:
                res = cache[key]
            except KeyError:
                res = cache[key] = wrapped(*args, **kwArgs)
            return res
        wrapper.cache = cache
        return wrapper
    return memoize

def memoize(wrapped):
    "Decorator to cache function result."

    return memoize_with({})(wrapped)

class _CacheSetter:
    __slots__ = ("_cache", "_key")
    def __init__(self, cache, key):
        self._cache = cache
        self._key = key
    def set(self, value):
        self._cache[self._key] = value

class CacheInit:
    __slots__ = ("cache",)
    def __init__(self, cache=None):
            self.cache = {} if cache is None else cache
    def __call__(self, *args, **kwArgs):
        return _CacheSetter(self.cache, args + tuple(kwArgs.items()))

def print_call_with(printer):
    def print_call(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwArgs):
            l = [repr(e) for e in args]
            l2 = [f"{k}={v!r}" for k, v in kwArgs.items()]
            printer(wrapped.__name__, "(", ",".join(l+l2), ")", sep="")
            return wrapped(*args, **kwArgs)
        return wrapper
    return print_call

print_call = print_call_with(print)

def logger_to_printer(logger, level):
    if logger.isEnabledFor(level):
        def printer(*args, **kwArgs):
            try:
                sep = kwArgs["sep"]
            except KeyError:
                sep = " "
            logger.log(level, sep.join(str(e) for e in args))
    else:
        def printer(*args, **kwArgs):
            pass
    return printer

def apply_all_class(f):
    "Transform a function decorator in a class decorator wich apply to all callable of the class."

    def apply(c):
        for k, v in c.__dict__.items():
            if callable(v):
                setattr(c, k, f(v))
        return c
    apply.__doc__ = f"Class decorator which apply {f.__name__} to all callable of the class."
    return apply

static_class = apply_all_class(staticmethod)

def def_accept(name):
    "Generate an accept(visitor) method."

    exec(f"""\
def accept(self, visitor):
    return visitor.visit_{name}(self)
""")
    return locals()["accept"]

def visitable(klass):
    "Class decorator to add an accept(visitor) method."

    name = klass.__name__
    accept = def_accept(name)
    accept.__qualname__ = f"{name}.accept"
    klass.accept = accept
    return klass 

def def_delegate(inner_name, method_name):
    "Generate a method that delegate to inner_name attribute of self."

    exec(f"""\
def {method_name}(self, *args, **kwargs):
        return self.{inner_name}.{method_name}(*args, **kwargs)
""")
    return locals()[method_name]

def def_class_delegate(class_name, inner_name, method_name):
    "As def_delegate but set the __qualname__ attribute."

    delegate = def_delegate(inner_name, method_name)
    delegate.__qualname__ = f"{class_name}.{method_name}"
    return delegate

def delegate(inner_name, method_names):
    "Class decorator to add one or more delegate method."

    if isinstance(method_names, str):
        def inner_delegate(klass):
            setattr(klass, method_names, def_class_delegate(klass.__name__, inner_name, method_names))
            return klass
    else:
        def inner_delegate(klass):
            class_name = klass.__name__
            for method_name in method_names:
                setattr(klass, method_name, def_class_delegate(class_name, inner_name, method_name))
            return klass
    return inner_delegate

def Singleton(cls):
    @functools.wraps(cls)
    def getInstance(*args, **kwargs):
        if getInstance.instance is None:
            getInstance.instance = cls(*args, **kwargs)
        return getInstance.instance
    getInstance.instance = None
    return getInstance

class Decorator:
    __slots__ = ("_inner",)
    def __init__(self, inner):
        self._inner = inner
    def __getattr__(self, name):
        return getattr(self._inner, name)

class RevealAccessDecorator(Decorator):
    __slots__ = ("_printer")
    def __init__(self, inner, printer=print):
        super().__init__(inner)
        self._printer = printer
    def __getattr__(self, name):
        self._printer("get :", name)
        return super().__getattr__(name)

class Composite:
    __slots__ = ("_items",)
    def __init__(self):
        self._items = []
    def addItem(self, item):
        self._items.append(item)
    def __getattr__(self, name):
        def method(*args, **kwargs):
            return tuple(getattr(item, name)(*args, **kwargs) for item in
                         self._items)
        return method

class Field:
    __slots__ = ("name",)
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
    def __delete__(self, instance):
        del instance.__dict__[self.name]
    def __set_name__(self, owner, name):
        self.name = name

class ClassField:
    __slots__ = ("value",)
    def __get__(self, instance, owner=None):
        return self.value
    def __set__(self, instance, value):
        self.value = value
    def __delete__(self, instance):
        del self.value

class DelegateField:
    __slots__ = ("innerName", "name")
    def __init__(self, innerName):
        self.innerName = innerName
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            inner = getattr(instance, self.innerName)
            return getattr(inner, self.name)
    def __set__(self, instance, value):
        inner = getattr(instance, self.innerName)
        setattr(inner, self.name, value)
    def __delete__(self, instance):
        inner = getattr(instance, self.innerName)
        delattr(inner, self.name)
    def __set_name__(self, owner, name):
        self.name = name

class ProxyField:
    __slots__ = ("inner", "name")
    def __init__(self, inner):
        self.inner = inner
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return getattr(self.inner, self.name)
    def __set__(self, instance, value):
        setattr(self.inner, self.name, value)
    def __delete__(self, instance):
        delattr(self.inner, self.name)
    def __set_name__(self, owner, name):
        self.name = name

class DescriptorDecorator:
    __slots__ = ("inner", "name")
    def __init__(self, inner):
        self.inner = inner
    def __get__(self, instance, owner=None):
        return self.inner.__get__(instance, owner)
    def __set__(self, instance, value):
        self.inner.__set__(instance, value)
    def __delete__(self, instance):
        self.inner.__delete__(instance)
    def __set_name__(self, owner, name):
        self.name = name
        try:
            self.inner.__set_name__(owner, name)
        except AttributeError:
            pass

class Typed(DescriptorDecorator):
    __slots__ = ("fieldType",)
    def __init__(self, fieldType, inner):
        super().__init__(inner)
        self.fieldType = fieldType
    def __set__(self, instance, value):
        if not isinstance(value, self.fieldType):
            raise TypeError(f"expecting {self.fieldType.__name__} in {self.name}")
        super().__set__(instance, value)

class RevealAccess(DescriptorDecorator):
    __slots__ = ("_printer",)
    def __init__(self, inner, printer=print):
        super().__init__(inner)
        self._printer = printer
    def __get__(self, instance, owner=None):
        self._printer("Retrieving var", self.name)
        return super().__get__(instance, owner)
    def __set__(self, instance, value):
        self._printer("Updating var", self.name)
        super().__set__(instance, value)
    def __delete__(self, instance):
        self._printer("Deleting var", self.name)
        super().__delete__(instance)

class DefaultValue(DescriptorDecorator):
    __slots__ = ("default",)
    def __init__(self, default, inner):
        super().__init__(inner)
        self.default = default
    def __get__(self, instance, owner=None):
        try:
            return super().__get__(instance, owner)
        except AttributeError:
            self.__set__(instance, self.default)
            return self.default
        except KeyError:
            self.__set__(instance, self.default)
            return self.default

class ClassProperty(property):
    def __get__(self, instance, owner=None):
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        if owner is None and instance is not None:
            owner = type(instance)
        return self.fget(owner)
    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(type(instance), value)
    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(type(instance))

class StaticProperty(property):
    def __get__(self, instance, owner=None):
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget()
    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(value)
    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel()

def type_check(wrapped):
    "Decorator to check type of argument and return value of a function."

    @functools.wraps(wrapped)
    def wrapper(*args, **kwArgs):
        annotations = typing.get_type_hints(wrapped)
        it_param = iter(inspect.signature(wrapped).parameters.values())
        for arg in args:
            name = next(it_param).name
            try:
                t = annotations[name]
                if not isinstance(arg, t):
                    raise TypeError(f"{wrapped.__name__} : {name} must be {t.__name__}")
            except KeyError:
                pass
        for k, v in kwArgs.items():
            try:
                t = annotations[k]
                if not isinstance(v, t):
                    raise TypeError(f"{wrapped.__name__} : {k} must be {t.__name__}")
            except KeyError:
                pass
        res = wrapped(*args, **kwArgs)
        try:
            t = annotations["return"]
            if not isinstance(res, t):
                raise TypeError(f"{wrapped.__name__} must return {t.__name__}")
        except KeyError:
                pass
        return res
    return wrapper

type_check_class = apply_all_class(type_check)

class SliceDict(dict):
    __slots__ = ()
    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise TypeError("step not allowed")
            start = key.start
            stop = key.stop
            res = type(self)()
            if start is None:
                if stop is None:
                    res.update(self)
                else:
                    for k, v in self.items():
                        if k < stop:
                            res[k] = v
            elif stop is None:
                for k, v in self.items():
                    if start <= k:
                        res[k] = v
            else:
                for k, v in self.items():
                    if start <= k < stop:
                        res[k] = v
            return res
        else:
            return super().__getitem__(key)
    def __repr__(self):
        return "SliceDict({0})".format(super().__repr__())

class Observable:
    def __init__(self):
        self.observators = []
    def add_observator(self, observator):
        self.observators.append(observator)
    def notify(self, event):
        for observator in self.observators:
            observator.notify(event)

def generate(f):
    while True:
        yield f()

def compute(value, f):
    while True:
        yield value
        value = f(value)

def macro_dataclass(name, params):
    slots_buffer = []
    init_args_buffer = ["self"]
    init_body_buffer = []
    to_tuple_body_buffer = []
    to_dict_body_buffer = []
    repr_body_buffer = []
    first = True

    for param in params:
        param_str = f"'{param}'"
        get_param = f"self.{param}"
        slots_buffer.append(param_str)
        init_args_buffer.append(param)
        init_body_buffer.append(f"{get_param} = {param}")
        to_tuple_body_buffer.append(get_param)
        to_dict_body_buffer.append(f"{param_str}: {get_param}")
        if first:
            first = False
            repr_body_buffer.append(f"'{name}({param}='")
        else:
            repr_body_buffer.append(f"', {param}='")
        repr_body_buffer.append(f"repr({get_param})")

    repr_body_buffer.append("')'")

    lit_join = ", ".join
    line_join = "\n        ".join

    return f"""\
class {name}:
    __slots__ = ({lit_join(slots_buffer)},)
    def __init__({lit_join(init_args_buffer)}):
        {line_join(init_body_buffer)}
    def to_tuple(self):
        return ({lit_join(to_tuple_body_buffer)},)
    def to_dict(self):
        return {{{lit_join(to_dict_body_buffer)}}}
    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, {name}):
            return self.to_tuple() == other.to_tuple()
        else:
            return NotImplemented
    def __lt__(self, other):
        if isinstance(other, {name}):
            return self.to_tuple() < other.to_tuple()
        else:
            return NotImplemented
    def __repr__(self):
        return ''.join(({lit_join(repr_body_buffer)},))
"""

def macro_square_matrix(size):
    name = f"SquareMatrix{size}"
    line_name = f"MatrixLine{size}"

    str_body_buffer = ["'[['"]
    id_list_buffer = []
    generate_list_buffer = []
    add_list_buffer = []
    sub_list_buffer = []
    mul_list_buffer = []
    matmul_list_buffer = []

    f_call = "f()"

    range_size = range(size)
    for i in range_size:
        if i != 0:
            str_body_buffer.append("'],\\n ['")
        offset = i * size
        matmul_sublist_buffer = []
        for j in range_size:
            indice = j + offset
            if j != 0:
                str_body_buffer.append("', '")
            str_body_buffer.append(f"str(self_inner[{indice}])")
            id_list_buffer.append("1" if i == j else "0")
            generate_list_buffer.append(f_call)
            add_list_buffer.append(f"self_inner[{indice}] + other_inner[{indice}]")
            sub_list_buffer.append(f"self_inner[{indice}] - other_inner[{indice}]")
            mul_list_buffer.append(f"other * self_inner[{indice}]")
            matmul_sublist_buffer.append(f"self_inner[{indice}] * other[{j}]")
        matmul_list_buffer.append(" + ".join(matmul_sublist_buffer))

    str_body_buffer.append("']]'")

    lit_join = ", ".join

    return f"""\
class {line_name}:
    __slots__ = ('inner', 'offset')
    def __init__(self, inner, line):
        self.inner = inner
        self.offset = line * {size}
    def __getitem__(self, column):
        return self.inner[column + self.offset]
    def __setitem__(self, column, value):
        self.inner[column + self.offset] = value
class {name}:
    __slots__ = ('inner',)
    def __init__(self, inner):
        self.inner = inner
    def __getitem__(self, line):
        return {line_name}(self.inner, line)
    def __repr__(self):
        return '{name}({{}})'.format(self.inner)
    def __str__(self):
        self_inner = self.inner
        return ''.join(({lit_join(str_body_buffer)},))
    @classmethod
    def identity(klass):
        return klass([{lit_join(id_list_buffer)}])
    @classmethod
    def generate(klass, f):
        return klass([{lit_join(generate_list_buffer)}])
    def __add__(self, other):
        if isinstance(other, {name}):
            self_inner = self.inner
            other_inner = other.inner
            return type(self)([{lit_join(add_list_buffer)}])
        return NotImplemented
    def __sub__(self, other):
        if isinstance(other, {name}):
            self_inner = self.inner
            other_inner = other.inner
            return type(self)([{lit_join(sub_list_buffer)}])
        return NotImplemented
    def __mul__(self, other):
        self_inner = self.inner
        return type(self)([{lit_join(mul_list_buffer)}])
    __rmul__ = __mul__
    def __matmul__(self, other):
        self_inner = self.inner
        return [{lit_join(matmul_list_buffer)}]
"""

def macro_sigmoid(size):
    buffer = []
    append = buffer.append

    for i in range(size):
        append(f"1 / (1 + exp(-column[{i}]))")

    lit_join = ", ".join

    return f"""\
def sigmoid{size}(column):
    return [{lit_join(buffer)}]
"""

def macro_perceptron(depth):
    buffer = []
    append = buffer.append
    apply_sigmoid = "column = sigmoid(column)"

    for i in range(depth):
        append(f"column = self_inner[{i}] @ column")
        append(apply_sigmoid)

    line_join = "\n        ".join

    return f"""\
class Perceptron{depth}:
    __slots__ = ('inner', 'sigmoid',)
    def __init__(self, sigmoid):
        self.inner = []
        self.sigmoid = sigmoid
    def __call__(self, column):
        self_inner = self.inner
        sigmoid = self.sigmoid
        {line_join(buffer)}
        return column
"""

_RecursiveCall = collections.namedtuple("RecursiveCall", ("args", "kwargs"))

def terminal_rec(wrapped):
    "Decorator to optimize terminal recursive function."

    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        if wrapper.recursive_call.get():
            return _RecursiveCall(args, kwargs)
        try:
            wrapper.recursive_call.set(True)
            while True:
                res = wrapped(*args, **kwargs)
                if isinstance(res, _RecursiveCall):
                    args, kwargs = res
                else:
                    return res
        finally:
            wrapper.recursive_call.set(False)
    wrapper.recursive_call = contextvars.ContextVar(f"{wrapped.__name__}.recursive_call", default=False)
    return wrapper

class BiDict:
    __slots__ = ("d", "rd")
    def __init__(self, d=None, rd=None):
        if d is None:
            self.d = {}
            self.rd = {}
            if rd is not None:
                self.rev().update(rd)
        elif rd is None:
            self.d = {}
            self.rd = {}
            self.update(d)
        else:
            self.d = d
            self.rd = rd
    def rev(self):
        return BiDict(self.rd, self.d)
    def __len__(self):
        return len(self.d)
    def __getitem__(self, key):
        return self.d[key]
    def __setitem__(self, key, value):
        old_value = self.d.get(key, MISSING)
        if old_value is MISSING:
            if value in self.rd:
                raise ValueError(f"value {value!r} already associated")
            else:
                self.d[key] = value
                self.rd[value] = key
        elif old_value != value:
            if value in self.rd:
                raise ValueError(f"value {value!r} already associated")
            else:
                self.d[key] = value
                del self.rd[old_value]
                self.rd[value] = key
    def __delitem__(self, key):
        old_value = self.d.get(key)
        del self.d[key]
        del self.rd[old_value]
    def __contains__(self, key):
        return key in self.d
    def __iter__(self):
        return iter(self.d)
    def clear(self):
        self.d.clear()
        self.rd.clear()
    def copy(self):
        return BiDict(self.d.copy(), self.rd.copy())
    def get(self, key, default=None):
        return self.d.get(key, default)
    def items(self):
        return self.d.items()
    def keys(self):
        return self.d.keys()
    def update(self, other=None, **kwargs):
        if other is not None:
            if isinstance(other, dict):
                other = other.items()
            for k, v in other:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v
    def values(self):
        return self.rd.keys()
    def __repr__(self):
        return f"BiDict({self.d})"

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
