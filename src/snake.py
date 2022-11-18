
import builtins
import enum
import importlib
import itertools
import operator
import pathlib
import types

class Etat:
    __slots__ = ("name", "not_poubelle", "lexeme_type", "transitions",
                 "defaut_transition")
    def __init__(self, name, not_poubelle, lexeme_type):
        self.name = name
        self.not_poubelle = not_poubelle
        self.lexeme_type = lexeme_type
        self.transitions = {}
        self.defaut_transition = None
    def add_transition(self, c, e):
        self.transitions[c] = e
    def add_transitions(self, s, e):
        for c in s:
            self.transitions[c] = e
    def next(self, c):
        return self.transitions.get(c, self.defaut_transition)
    def __repr__(self):
        return f"Etat('{self.name}')"

@enum.unique
class Type(enum.Enum):
    BLANK = 0
    NEW_LINE = 1
    IDENTIFIER = 2
    NONE_KEYWORD = 3
    TRUE_KEYWORD = 4
    FALSE_KEYWORD = 5
    INTEGER_LITERAL = 6
    FLOAT_LITERAL = 7
    STRING_LITERAL = 8
    START_DELIMITER = 9
    END_DELIMITER = 10

class LexemeIterator:
    __slots__ = ("start", "phrase")
    def __init__(self, start, phrase):
        self.start = start
        self.phrase = phrase
    def __iter__(self):
        return self
    def __next__(self):
        current = self.start
        i = 0
        res_index = None
        res_type = None
        length = len(self.phrase)
        if length == 0:
            raise StopIteration()
        while current.not_poubelle and i < length:
            current = current.next(self.phrase[i])
            i += 1
            if current.not_poubelle and current.lexeme_type is not None:
                res_index = i
                res_type = current.lexeme_type
        if res_index is None:
            index = self.phrase.find('\n')
            if index == -1:
                token = self.phrase
            else:
                token = self.phrase[:index]
            raise Exception("token non reconnu : " + token)
        else:
            res = self.phrase[:res_index]
            self.phrase = self.phrase[res_index:]
            return res_type, res

def add_keyword(keyword, lexeme_type, poubelle, prec, identifier, digits,
                alphas, operateurs):
    for i, c in enumerate(keyword):
        etat = Etat(f"{keyword}_keyword{i}", True, Type.IDENTIFIER)
        etat.defaut_transition = poubelle
        prec.add_transition(c, etat)

        etat.add_transitions(digits, identifier)
        etat.add_transitions(alphas, identifier)
        etat.add_transitions(operateurs, identifier)
        prec = etat
    etat.lexeme_type = lexeme_type

def create_analyseur():
    poubelle = Etat("poubelle", False, None)

    start = Etat("start", True, None)
    start.defaut_transition = poubelle

    blank = Etat("blank", True, Type.BLANK)
    blank.defaut_transition = poubelle
    blanks = " \t"
    start.add_transitions(blanks, blank)

    blank.add_transitions(blanks, blank)

    new_line = Etat("new_line", True, Type.NEW_LINE)
    new_line.defaut_transition = poubelle
    new_line_char = "\n"
    start.add_transition(new_line_char, new_line)

    number = Etat("number", True, Type.INTEGER_LITERAL)
    number.defaut_transition = poubelle
    digits = "0123456789"
    start.add_transitions(digits, number)

    number.add_transitions(digits, number)

    number2 = Etat("number2", True, Type.FLOAT_LITERAL)
    number2.defaut_transition = poubelle
    number.add_transition(".", number2);

    number2.add_transitions(digits, number2)

    identifier = Etat("identifier", True, Type.IDENTIFIER)
    identifier.defaut_transition = poubelle
    alphas = "_aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ"
    operateurs = "+-*/.,:;!=<^>%@$~?&|[]{}"
    start.add_transitions(alphas, identifier)
    start.add_transitions(operateurs, identifier)

    identifier.add_transitions(alphas, identifier)
    identifier.add_transitions(operateurs, identifier)
    identifier.add_transitions(digits, identifier)

    delimiteur = Etat("delimiteur", True, Type.START_DELIMITER)
    delimiteur.defaut_transition = poubelle
    start.add_transition("(", delimiteur)

    delimiteur2 = Etat("delimiteur2", True, Type.END_DELIMITER)
    delimiteur2.defaut_transition = poubelle
    start.add_transition(")", delimiteur2)

    string = Etat("string", True, None)
    string.defaut_transition = string
    quote_char = "\""
    start.add_transition(quote_char, string)

    string.add_transition(new_line_char, poubelle)

    string2 = Etat("string2", True, Type.STRING_LITERAL)
    string2.defaut_transition = poubelle
    string.add_transition(quote_char, string2)

    string3 = Etat("string3", True, None)
    string3.defaut_transition = string
    string.add_transition("\\", string3)

    string3.add_transition(new_line_char, poubelle)

    number3 = Etat("number3", True, Type.IDENTIFIER)
    number3.defaut_transition = poubelle
    start.add_transitions("+-", number3)
    number3.add_transitions(digits, number)
    number3.add_transitions(alphas, identifier)
    number3.add_transitions(operateurs, identifier)

    comment = Etat("comment", True, Type.BLANK)
    comment.defaut_transition = comment
    comment.add_transition(new_line_char, poubelle)
    start.add_transition("#", comment)

    add_keyword("None", Type.NONE_KEYWORD, poubelle, start, identifier,
                digits, alphas, operateurs)

    add_keyword("True", Type.TRUE_KEYWORD, poubelle, start, identifier,
                digits, alphas, operateurs)

    add_keyword("False", Type.FALSE_KEYWORD, poubelle, start, identifier,
                digits, alphas, operateurs)

    return start

AL = create_analyseur()

class NodeValue:
    __slots__ = ("value",)
    def __init__(self, value):
        self.value = value
    def eval(self, env):
        return self.value
    def compile(self, env, append, indent):
        append(repr(self.value))
    def __repr__(self):
        return f"NodeValue({self.value!r})"

class NodeIdentifier:
    __slots__ = ("identifier",)
    def __init__(self, identifier):
        self.identifier = identifier
    def eval(self, env):
        return env[self.identifier]
    def compile(self, env, append, indent):
        append(self.identifier)
    def __repr__(self):
        return f"NodeIdentifier({self.identifier!r})"

MARKER = object()

class NodeList(list):
    __slots__ = ()
    def eval(self, env):
        itnodes = iter(self)
        o = next(itnodes).eval(env)
        if isinstance(o, Macro):
            return o(env, itnodes)
        else:
            t = tuple(n.eval(env) for n in itnodes)
            return o(*t)
    def compile(self, env, append, indent):
        itnodes = iter(self)
        node0 = next(itnodes)
        try:
            o = node0.eval(env)
            if isinstance(o, Macro):
                o.compile(env, itnodes, append, indent)
                return
        except KeyError:
            pass

        node0.compile(env, append, indent)
        append("(")
        n = next(itnodes, MARKER)
        if n is not MARKER:
            n.compile(env, append, indent)
            for n in itnodes:
                append(", ")
                n.compile(env, append, indent)
        append(")")
    def __repr__(self):
        return "NodeList({})".format(super().__repr__())

NONE_VALUE = NodeValue(None)
TRUE_VALUE = NodeValue(True)
FALSE_VALUE = NodeValue(False)

def parse_lexeme(lexemes):
    node0 = NodeList()
    node0.append(BLOC_VALUE)
    nodes = [node0]
    index = 0
    for lexeme_type, value in lexemes:
        node_index = nodes[index]
        if lexeme_type is Type.START_DELIMITER:
            nl = NodeList()
            node_index.append(nl)
            nodes.append(nl)
            index += 1
        elif lexeme_type is Type.END_DELIMITER:
            del nodes[index]
            index -= 1
        elif lexeme_type is Type.IDENTIFIER:
            node_index.append(NodeIdentifier(value))
        elif lexeme_type is Type.NONE_KEYWORD:
            node_index.append(NONE_VALUE)
        elif lexeme_type is Type.TRUE_KEYWORD:
            node_index.append(TRUE_VALUE)
        elif lexeme_type is Type.FALSE_KEYWORD:
            node_index.append(FALSE_VALUE)
        elif lexeme_type is Type.INTEGER_LITERAL:
            node_index.append(NodeValue(int(value)))
        elif lexeme_type is Type.FLOAT_LITERAL:
            node_index.append(NodeValue(float(value)))
        elif lexeme_type is Type.STRING_LITERAL:
            node_index.append(NodeValue(extractString(value)))

    if index != 0:
        raise Exception("erreur de parenthèse")
    return node0

def extractString(value):
    newValue = []
    length = len(value) - 1
    index = 1
    while index < length:
        c = value[index]
        if c == "\\":
            index += 1
            c2 = value[index]
            if c2 == "n":
                newValue.append("\n")
            elif c2 == "t":
                newValue.append("\t")
            elif c2 == "b":
                newValue.append("\b")
            elif c2 == "f":
                newValue.append("\f")
            elif c2 == "r":
                newValue.append("\r")
            elif c2 == "\\":
                newValue.append("\\")
            elif c2 == "'":
                newValue.append("'")
            elif c2 == "\"":
                newValue.append("\"")
            else:
                newValue.append(c)
                newValue.append(c2)
        else:
            newValue.append(c)
        index += 1

    return "".join(newValue)

class EnvironementLocal:
    __slots__ = ("local", "parent")
    def __init__(self, parent):
        self.local = {}
        self.parent = parent
    def __getitem__(self, k):
        res = self.local.get(k, MARKER)
        if res is MARKER:
            res = self.parent[k]
        return res
    __getattr__ = __getitem__
    def __setitem__(self, k ,v):
        self.local[k] = v
        return v
    def __delitem__(self, k):
        del self.local[k]
    def __dir__(self):
        return list(self.local.keys())
    def __repr__(self):
        return repr(self.local)

class BreakException(Exception):
    def __init__(self, is_break):
        super().__init__()
        self.is_break = is_break

class Macro: # cette classe sert juste de marqueur
    __slots__ = ()

def exec_macro(env, node):
    if isinstance(node, NodeList):
        itnodes = iter(node)
        res = NodeList()
        node0 = next(itnodes, MARKER)
        if node0 is not MARKER:
            try:
                o = node0.eval(env)
                if isinstance(o, AbstractUserMacro):
                    return exec_macro(env, o.body_eval(itnodes))
            except KeyError:
                pass
            res.append(exec_macro(env, node0))
            for n in itnodes:
                res.append(exec_macro(env, n))
        return res
    return node

class AbstractCallable:
    __slots__ = ("__name__", "env", "declared_args", "body", "__dict__")
    def __init__(self, name, env, declared_args, body):
        self.__name__ = name
        self.env = env
        self.declared_args = declared_args
        self.body = exec_macro(env, body)
    def body_eval(self, itargs):
        local = EnvironementLocal(self.env)
        self.update_local(local, itargs)
        return self.body.eval(local)

class AbstractUserFonction(AbstractCallable):
    __slots__ = ()
    def __call__(self, *args):
        return self.body_eval(iter(args))
    def __get__(self, obj, objtype=None): # transformation en méthode
        if obj is None:
            return self
        return types.MethodType(self, obj)
    def __repr__(self):
        return f"<fonction {self.__name__}>"

def convert_name(declared_args):
    return [node.identifier for node in declared_args]

class ClassicCallable:
    __slots__ = ()
    def update_local(self, local, itargs):
        for name in self.declared_args:
            local[name] = next(itargs)

class VarArgsCallable:
    __slots__ = ()
    def update_local(self, local, itargs):
        local[self.declared_args] = tuple(itargs)

class UserFonction(AbstractUserFonction, ClassicCallable):
    __slots__ = ()

class UserVarArgsFonction(AbstractUserFonction, VarArgsCallable):
    __slots__ = ()

class AbstractUserMacro(AbstractCallable, Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return self.body_eval(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        self.body_eval(itnodes).compile(env, append, indent)
    def __repr__(self):
        return f"<macro {self.__name__}>"

class UserMacro(AbstractUserMacro, ClassicCallable):
    __slots__ = ()

class UserVarArgsMacro(AbstractUserMacro, VarArgsCallable):
    __slots__ = ()

def get_name(env, node):
    if isinstance(node, NodeIdentifier):
        name = node.identifier
    else:
        name = node.eval(env)
        if name is None:
            raise Exception("None n'est pas un nom")
    return name

def apply_op(op, env, it):
    res = 0
    v = next(it, MARKER)
    if v is not MARKER:
        res = v.eval(env)
        for v in it:
            res = op(res, v.eval(env))
    return res

def compile_op(op, zero, env, itnodes, append, indent):
    node0 = next(itnodes, MARKER)
    if node0 is MARKER:
        append(zero)
    else:
        append("(")
        node0.compile(env, append, indent)
        for n in itnodes:
            append(op)
            n.compile(env, append, indent)
        append(")")

class MacroAdd(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.add, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" + ", "0", env, itnodes, append, indent)

class MacroAnd(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = True
        for node in itnodes:
            if not node.eval(env):
                res = False
                break
        return res
    def compile(self, env, itnodes, append, indent):
        compile_op(" and ", "True", env, itnodes, append, indent)

class MacroBitwiseAnd(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 & o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" & ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroBitwiseOr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 | o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" & ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroBitwiseXOr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 ^ o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" ^ ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroBloc(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = None
        for node in itnodes:
            res = node.eval(env)
        return res
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes, MARKER)
        if node0 is MARKER:
            append("pass")
        else:
            node0.compile(env, append, indent)
            for node in itnodes:
                append("\n")
                indent.append_indent(append)
                node.compile(env, append, indent)
            

BLOC_VALUE = NodeValue(MacroBloc())

class MacroBreak(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        raise BreakException(True)
    def compile(self, env, itnodes, append, indent):
        append("break")

class MacroCall(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        f = next(itnodes).eval(env)
        l = next(itnodes).eval(env)
        node2 = next(itnodes, MARKER)
        if node2 is MARKER:
            return f(*l)
        else:
            d = node2.eval(env)
            return f(*l, **d)
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append("(*")
        next(itnodes).compile(env, append, indent)
        node2 = next(itnodes, MARKER)
        if node2 is not MARKER:
            append(", **")
            node2.compile(env, append, indent)
        append(")")

class MacroCallMethod(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o = next(itnodes).eval(env)
        name = get_name(env, next(itnodes))
        t = tuple(n.eval(env) for n in itnodes)
        return getattr(o, name)(*t)
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        if isinstance(node1, NodeIdentifier):
            node0.compile(env, append, indent)
            append(".")
            node1.compile(env, append, indent)
            append("(")
            node2 = next(itnodes, MARKER)
            if node2 is not MARKER:
                node2.compile(env, append, indent)
                for n in itnodes:
                    append(", ")
                    n.compile(env, append, indent)
            append(")")
        else:
            append("getattr(")
            node0.compile(env, append, indent)
            append(", ")
            node1.compile(env, append, indent)
            append(")(")
            node2 = next(itnodes, MARKER)
            if node2 is not MARKER:
                node2.compile(env, append, indent)
                for n in itnodes:
                    append(", ")
                    n.compile(env, append, indent)
            append(")")

class MacroCase(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = None
        node_test = next(itnodes, MARKER)
        while node_test is not MARKER:
            node_body = next(itnodes)
            if node_test.eval(env):
                res = node_body.eval(env)
                break
            node_test = next(itnodes, MARKER)
        return res
    def compile(self, env, itnodes, append, indent):
        node_test = next(itnodes, MARKER)
        if node_test is MARKER:
            append("pass")
        else:
            node_body = next(itnodes)
            append("if ")
            node_test.compile(env, append, indent)
            append(":\n")
            indent.increment()
            indent.append_indent(append)
            node_body.compile(env, append, indent)
            indent.decrement()
            node_test = next(itnodes, MARKER)
            while node_test is not MARKER:
                node_body = next(itnodes)
                append("\n")
                indent.append_indent(append)
                append("elif ")
                node_test.compile(env, append, indent)
                append(":\n")
                indent.increment()
                indent.append_indent(append)
                node_body.compile(env, append, indent)
                indent.decrement()
                node_test = next(itnodes, MARKER)

def decorate(env, nodes, value):
    for i in range(len(nodes) - 4, -1, -1):
        value = nodes[i].eval(env)(value)
    return value

def decorate_comp(env, nodes, append, indent):
    for i in range(len(nodes) - 3):
        append("@")
        nodes[i].compile(env, append, indent)
        append("\n")
        indent.append_indent(append)

class MacroClass(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        nodes = list(itnodes)
        name = nodes[-3].identifier
        bases = tuple(node.eval(env) for node in nodes[-2])
        local = EnvironementLocal(env)
        nodes[-1].eval(local)
        def exec_body(ns):
            ns.update(local.local)
        res = types.new_class(name, bases, exec_body=exec_body)
        res = decorate(env, nodes, res)
        env[name] = res
        return res
    def compile(self, env, itnodes, append, indent):
        nodes = list(itnodes)
        decorate_comp(env, nodes, append, indent)
        append("class ")
        nodes[-3].compile(env, append, indent)
        parent = nodes[-2]
        if parent:
            append("(")
            it = iter(parent)
            next(it).compile(env, append, indent)
            for n in it:
                append(", ")
                n.compile(env, append, indent)
            append(")")
        append(":\n")
        indent.increment()
        indent.append_indent(append)
        nodes[-1].compile(env, append, indent)
        indent.decrement()

class MacroConcat(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return "".join(str(n.eval(env)) for n in itnodes)
    def compile(self, env, itnodes, append, indent):
        append("''.join((")
        node0 = next(itnodes, MARKER)
        if node0 is not MARKER:
            append("str(")
            node0.compile(env, append, indent)
            for n in itnodes:
                append("), str(")
                n.compile(env, append, indent)
            append("),")
        append("))")

class MacroContains(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        seq = next(itnodes).eval(env)
        obj = next(itnodes).eval(env)
        return obj in seq
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        node1.compile(env, append, indent)
        append(" in ")
        node0.compile(env, append, indent)

class MacroContinue(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        raise BreakException(False)
    def compile(self, env, itnodes, append, indent):
        append("continue")

def add_return(node):
    if isinstance(node, NodeList):
        node0 = node[0]
        if isinstance(node0, NodeIdentifier):
            name = node0.identifier
            if name == "bloc":
                node[-1] = add_return(node[-1])
                return node
            elif name == "case":
                for i in range(2, len(node), 2):
                    node[i] = add_return(node[i])
                return node
            elif name == "if":
                node[2] = add_return(node[2])
                node[3] = add_return(node[3])
                return node
            elif name == "raise":
                return node
            elif name == "try":
                node[1] = add_return(node[1])
                for el in node[2]:
                    el[2] = add_return(el[2])
                return node
            elif name == "with":
                node[2] = add_return(node[2])
                return node
    return NodeList([RETURN_VALUE, node])

class MacroDef(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        nodes = list(itnodes)
        name = nodes[-3].identifier
        args_node = nodes[-2]
        body = nodes[-1]
        if isinstance(args_node, NodeList):
            value = UserFonction(name, env, convert_name(args_node), body)
        else:
            value = UserVarArgsFonction(name, env, args_node.identifier, body)
        value = decorate(env, nodes, value)
        env[name] = value
        return value
    def compile(self, env, itnodes, append, indent):
        nodes = list(itnodes)
        decorate_comp(env, nodes, append, indent)
        append("def ")
        nodes[-3].compile(env, append, indent)
        append("(")
        args_node = nodes[-2]
        if isinstance(args_node, NodeList):
            if args_node:
                it = iter(args_node)
                next(it).compile(env, append, indent)
                for n in it:
                    append(", ")
                    n.compile(env, append, indent)
        else:
            append("*")
            args_node.compile(env, append, indent)
        append("):\n")
        indent.increment()
        indent.append_indent(append)
        add_return(nodes[-1]).compile(env, append, indent)
        indent.decrement()

class MacroDefMacro(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        name = next(itnodes).identifier
        args_node = next(itnodes)
        body = next(itnodes)
        if isinstance(args_node, NodeList):
            value = UserMacro(name, env, convert_name(args_node), body)
        else:
            value = UserVarArgsMacro(name, env, args_node.identifier, body)
        env[name] = value
        return value
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append(" = None")

class MacroDel(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        name = next(itnodes).identifier
        del env[name]
    def compile(self, env, itnodes, append, indent):
        append("del ")
        next(itnodes).compile(env, append, indent)

class MacroDelAttr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o = next(itnodes).eval(env)
        name = get_name(env, next(itnodes))
        delattr(o, name)
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        if isinstance(node1, NodeIdentifier):
            append("del ")
            node0.compile(env, append, indent)
            append(".")
            node1.compile(env, append, indent)
        else:
            append("delattr(")
            node0.compile(env, append, indent)
            append(", ")
            node1.compile(env, append, indent)
            append(")")

class MacroDelItem(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        del o1[o2]
    def compile(self, env, itnodes, append, indent):
        append("del ")
        next(itnodes).compile(env, append, indent)
        append("[")
        next(itnodes).compile(env, append, indent)
        append("]")

class MacroDictComp(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        nl = next(itnodes)
        node_key = nl[0]
        node_value = nl[1]
        name = next(itnodes).identifier
        res = {}
        local = EnvironementLocal(env)
        for o in next(itnodes).eval(env):
            local[name] = o
            res[node_key.eval(local)] = node_value.eval(local)
        return res
    def compile(self, env, itnodes, append, indent):
        append("{")
        nl = next(itnodes)
        nl[0].compile(env, append, indent)
        append(": ")
        nl[1].compile(env, append, indent)
        append(" for ")
        next(itnodes).compile(env, append, indent)
        append(" in ")
        next(itnodes).compile(env, append, indent)
        append("}")

class MacroDictLit(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return {nl[0].eval(env):nl[1].eval(env) for nl in itnodes}
    def compile(self, env, itnodes, append, indent):
        append("{")
        nl = next(itnodes, MARKER)
        if nl is not MARKER:
            nl[0].compile(env, append, indent)
            append(": ")
            nl[1].compile(env, append, indent)
            for nl in itnodes:
                append(", ")
                nl[0].compile(env, append, indent)
                append(": ")
                nl[1].compile(env, append, indent)
        append("}")

class MacroDivide(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.truediv, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" / ", "1", env, itnodes, append, indent)

def apply_comp(comp, env, it):
    res = True
    v1 = next(it, MARKER)
    if v1 is not MARKER:
        v1 = v1.eval(env)
        v2 = next(it, MARKER)
        while res and v2 is not MARKER:
            v2 = v2.eval(env)
            res = comp(v1, v2)
            v1 = v2
            v2 = next(it, MARKER)
    return res

def compile_comp(op, env, itnodes, append, indent):
    node0 = next(itnodes, MARKER)
    if node0 is MARKER:
        append("True")
    else:
        node1 = next(itnodes, MARKER)
        if node1 is MARKER:
            append("True")
        else:
            append("(")
            node0.compile(env, append, indent)
            append(op)
            node1.compile(env, append, indent)
            for n in itnodes:
                append(op)
                n.compile(env, append, indent)
            append(")")

class MacroEquals(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.eq, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" == ", env, itnodes, append, indent)

class MacroFloorDivide(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.floordiv, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" // ", "1", env, itnodes, append, indent)

class MacroFor(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = None
        nl = next(itnodes)
        name = nl[0].identifier
        node_body = next(itnodes)
        for o in nl[1].eval(env):
            env[name] = o
            try:
                res = node_body.eval(env)
            except BreakException as be:
                if be.is_break:
                    break
        del env[name]
        return res
    def compile(self, env, itnodes, append, indent):
        append("for ")
        nl = next(itnodes)
        nl[0].compile(env, append, indent)
        append(" in ")
        nl[1].compile(env, append, indent)
        append(":\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()

class MacroGE(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.ge, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" >= ", env, itnodes, append, indent)

def gen(node_exp, name, local, itval):
    for o in itval:
        local[name] = o
        yield node_exp.eval(local)

class MacroGen(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        node_exp = next(itnodes)
        name = next(itnodes).identifier
        local = EnvironementLocal(env)
        return gen(node_exp, name, local, next(itnodes).eval(env))
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" for ")
        next(itnodes).compile(env, append, indent)
        append(" in ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroGetAttr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o = next(itnodes).eval(env)
        name = get_name(env, next(itnodes))
        return getattr(o, name)
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        if isinstance(node1, NodeIdentifier):
            node0.compile(env, append, indent)
            append(".")
            node1.compile(env, append, indent)
        else:
            append("getattr(")
            node0.compile(env, append, indent)
            append(", ")
            node1.compile(env, append, indent)
            append(")")

class MacroGetEnv(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return env
    def compile(self, env, itnodes, append, indent):
        append("locals()")

class MacroGetItem(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1[o2]
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append("[")
        next(itnodes).compile(env, append, indent)
        append("]")

class MacroGT(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.gt, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" > ", env, itnodes, append, indent)

class MacroIf(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        if next(itnodes).eval(env):
            node = next(itnodes)
        else:
            next(itnodes)
            node = next(itnodes)
        return node.eval(env)
    def compile(self, env, itnodes, append, indent):
        append("if ")
        next(itnodes).compile(env, append, indent)
        append(":\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()
        append("\n")
        indent.append_indent(append)
        append("else:\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()

class MacroIfT(MacroIf):
    __slots__ = ()
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        append("(")
        node1.compile(env, append, indent)
        append(" if ")
        node0.compile(env, append, indent)
        append(" else ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroImportPy(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        module_name = next(itnodes).identifier
        res = importlib.import_module(module_name)
        name = next(itnodes, MARKER)
        if name is MARKER:
            env[module_name] = res
        else:
            env[name.identifier] = res
        return res
    def compile(self, env, itnodes, append, indent):
        append("import ")
        next(itnodes).compile(env, append, indent)
        name = next(itnodes, MARKER)
        if name is not MARKER:
            append(" as ")
            name.compile(env, append, indent)

class MacroImportSn(MacroImportPy):
    __slots__ = ()
    def __call__(self, env, itnodes):
        module_name = next(itnodes).identifier
        res = env["__interpreteur__"].eval_module(module_name)
        name = next(itnodes, MARKER)
        if name is MARKER:
            env[module_name] = res
        else:
            env[name.identifier] = res
        return res

class MacroIs(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.is_, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" is ", env, itnodes, append, indent)

class MacroIsNot(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 is not o2
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append(" is not ")
        next(itnodes).compile(env, append, indent)

class MacroLambda(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        function_args = next(itnodes)
        body = next(itnodes)
        if isinstance(function_args, NodeList):
            return UserFonction("lambda", env, convert_name(function_args), body)
        else:
            return UserVarArgsFonction("lambda", env, function_args.identifier, body)
    def compile(self, env, itnodes, append, indent):
        append("lambda ")
        args_node = next(itnodes)
        if isinstance(args_node, NodeList):
            if args_node:
                itargs = iter(args_node)
                next(itargs).compile(env, append, indent)
                for n in itargs:
                    append(", ")
                    n.compile(env, append, indent)
        else:
            append("*")
            args_node.compile(env, append, indent)
        append(": ")
        next(itnodes).compile(env, append, indent)

class MacroLE(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.le, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" <= ", env, itnodes, append, indent)

class MacroListComp(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        node_exp = next(itnodes)
        name = next(itnodes).identifier
        local = EnvironementLocal(env)
        res = []
        for o in next(itnodes).eval(env):
            local[name] = o
            res.append(node_exp.eval(local))
        return res
    def compile(self, env, itnodes, append, indent):
        append("[")
        next(itnodes).compile(env, append, indent)
        append(" for ")
        next(itnodes).compile(env, append, indent)
        append(" in ")
        next(itnodes).compile(env, append, indent)
        append("]")

class MacroListLit(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return [n.eval(env) for n in itnodes]
    def compile(self, env, itnodes, append, indent):
        append("[")
        node0 = next(itnodes, MARKER)
        if node0 is not MARKER:
            node0.compile(env, append, indent)
            for n in itnodes:
                append(", ")
                n.compile(env, append, indent)
        append("]")

class MacroLShift(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 << o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" << ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroLT(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_comp(operator.lt, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_comp(" < ", env, itnodes, append, indent)

class MacroMatMul(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.matmul, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" @ ", "1", env, itnodes, append, indent)

class MacroMinus(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.sub, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" - ", "0", env, itnodes, append, indent)

class MacroMod(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 % o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" % ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroMultiply(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return apply_op(operator.mul, env, itnodes)
    def compile(self, env, itnodes, append, indent):
        compile_op(" * ", "1", env, itnodes, append, indent)

class MacroNE(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 != o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" != ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroNeg(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return - next(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        append("(- ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroNot(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return not next(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        append("(not ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroOr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = False
        for node in itnodes:
            if node.eval(env):
                res = True
                break
        return res
    def compile(self, env, itnodes, append, indent):
        compile_op(" or ", "False", env, itnodes, append, indent)

class MacroPos(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return + next(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        append("(+ ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroPrintSep(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        itargs = (n.eval(env) for n in itnodes)
        sep = next(itargs, MARKER)
        if sep is MARKER:
            print()
        else:
            t = tuple(itargs)
            print(*t, sep=sep)
    def compile(self, env, itnodes, append, indent):
        append("print(")
        node0 = next(itnodes, MARKER)
        if node0 is not MARKER:
            node1 = next(itnodes, MARKER)
            if node1 is not MARKER:
                node1.compile(env, append, indent)
                for n in itnodes:
                    append(", ")
                    n.compile(env, append, indent)
                append(", sep=")
                node0.compile(env, append, indent)
        append(")")

def exec_unquote(env, node):
    if isinstance(node, NodeList):
        size = len(node)
        res = NodeList()
        if size > 0:
            node0 = node[0]
            if isinstance(node0, NodeIdentifier):
                if "unquote" == node0.identifier:
                    return node[1].eval(env)
            res.append(exec_unquote(env, node0))
            for i in range(1, size):
                res.append(exec_unquote(env, node[i]))
        return res
    return node

class MacroQuote(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return exec_unquote(env, next(itnodes))
    def compile(self, env, itnodes, append, indent):
        pass

class MacroRaise(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        raise next(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        append("raise ")
        next(itnodes).compile(env, append, indent)

class MacroReturn(Macro):
    __slots__ = ()
    def compile(self, env, itnodes, append, indent):
        append("return ")
        next(itnodes).compile(env, append, indent)

RETURN_VALUE = NodeValue(MacroReturn())

class MacroRShift(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        return o1 >> o2
    def compile(self, env, itnodes, append, indent):
        append("(")
        next(itnodes).compile(env, append, indent)
        append(" >> ")
        next(itnodes).compile(env, append, indent)
        append(")")

class MacroSet(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        name = next(itnodes).identifier
        value = next(itnodes).eval(env)
        env[name] = value
        return value
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append(" = ")
        next(itnodes).compile(env, append, indent)

class MacroSetAttr(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o = next(itnodes).eval(env)
        name = get_name(env, next(itnodes))
        value = next(itnodes).eval(env)
        setattr(o, name, value)
        return value
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes)
        node1 = next(itnodes)
        if isinstance(node1, NodeIdentifier):
            node0.compile(env, append, indent)
            append(".")
            node1.compile(env, append, indent)
            append(" = ")
            next(itnodes).compile(env, append, indent)
        else:
            append("setattr(")
            node0.compile(env, append, indent)
            append(", ")
            node1.compile(env, append, indent)
            append(", ")
            next(itnodes).compile(env, append, indent)
            append(")")

class MacroSetComp(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        node_exp = next(itnodes)
        name = next(itnodes).identifier
        local = EnvironementLocal(env)
        res = set()
        for o in next(itnodes).eval(env):
            local[name] = o
            res.add(node_exp.eval(local))
        return res
    def compile(self, env, itnodes, append, indent):
        append("{")
        next(itnodes).compile(env, append, indent)
        append(" for ")
        next(itnodes).compile(env, append, indent)
        append(" in ")
        next(itnodes).compile(env, append, indent)
        append("}")

class MacroSetItem(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        o1 = next(itnodes).eval(env)
        o2 = next(itnodes).eval(env)
        o3 = next(itnodes).eval(env)
        o1[o2] = o3
        return o3
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)
        append("[")
        next(itnodes).compile(env, append, indent)
        append("] = ")
        next(itnodes).compile(env, append, indent)

class MacroSetLit(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return {n.eval(env) for n in itnodes}
    def compile(self, env, itnodes, append, indent):
        node0 = next(itnodes, MARKER)
        if node0 is MARKER:
            append("set()")
        else:
            append("{")
            node0.compile(env, append, indent)
            for n in itnodes:
                append(", ")
                n.compile(env, append, indent)
            append("}")

class MacroSetMultiple(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        i = 0
        nl = next(itnodes)
        size = len(nl)
        for value in next(itnodes).eval(env):
            if i < size:
                env[nl[i].identifier] = value
                i += 1
            else:
                break
    def compile(self, env, itnodes, append, indent):
        itname = iter(next(itnodes))
        next(itname).compile(env, append, indent)
        for name in itname:
            append(", ")
            name.compile(env, append, indent)
        append(" = ")
        next(itnodes).compile(env, append, indent)

class MacroTry(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        try:
            return next(itnodes).eval(env)
        except Exception as ex:
            for el in next(itnodes):
                if isinstance(ex, el[0].eval(env)):
                    name = el[1].identifier
                    env[name] = ex
                    res = el[2].eval(env)
                    del env[name]
                    return res
            raise ex
        finally:
            node2 = next(itnodes, MARKER)
            if node2 is not MARKER:
                node2.eval(env)
    def compile(self, env, itnodes, append, indent):
        append("try:\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()
        for el in next(itnodes):
            append("\n")
            indent.append_indent(append)
            append("except ")
            el[0].compile(env, append, indent)
            append(" as ")
            el[1].compile(env, append, indent)
            append(":\n")
            indent.increment()
            indent.append_indent(append)
            el[2].compile(env, append, indent)
            indent.decrement()
        node2 = next(itnodes, MARKER)
        if node2 is not MARKER:
            append("\n")
            indent.append_indent(append)
            append("finally:\n")
            indent.increment()
            indent.append_indent(append)
            node2.compile(env, append, indent)
            indent.decrement()

class MacroTupleLit(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return tuple(n.eval(env) for n in itnodes)
    def compile(self, env, itnodes, append, indent):
        append("(")
        for n in itnodes:    
            n.compile(env, append, indent)
            append(", ")
        append(")")

class MacroUnquote(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        return next(itnodes).eval(env)
    def compile(self, env, itnodes, append, indent):
        next(itnodes).compile(env, append, indent)

class MacroWhile(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        res = None
        node_test = next(itnodes)
        node_body = next(itnodes)
        while node_test.eval(env):
            try:
                res = node_body.eval(env)
            except BreakException as be:
                if be.is_break:
                    break
        return res
    def compile(self, env, itnodes, append, indent):
        append("while ")
        next(itnodes).compile(env, append, indent)
        append(":\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()

class MacroWith(Macro):
    __slots__ = ()
    def __call__(self, env, itnodes):
        nl = next(itnodes)
        name = nl[0].identifier
        with nl[1].eval(env) as o:
            env[name] = o
            res = next(itnodes).eval(env)
            del env[name]
            return res
    def compile(self, env, itnodes, append, indent):
        nl = next(itnodes)
        append("with ")
        nl[1].compile(env, append, indent)
        append(" as ")
        nl[0].compile(env, append, indent)
        append(":\n")
        indent.increment()
        indent.append_indent(append)
        next(itnodes).compile(env, append, indent)
        indent.decrement()

def node_list_lit(*args):
    return NodeList(args)

def create_builtins():
    b = {}

    for name in dir(builtins):
        if not name.startswith("_"):
            b[name] = getattr(builtins, name)

    b["__name__"] = "__builtins__"
    b["."] = MacroCallMethod()
    b[":="] = MacroSet()
    b["=="] = MacroEquals()
    b["!="] = MacroNE()
    b["?"] = MacroIfT()
    b["<"] = MacroLT()
    b["<="] = MacroLE()
    b[">"] = MacroGT()
    b[">="] = MacroGE()
    b["+"] = MacroAdd()
    b["-"] = MacroMinus()
    b["*"] = MacroMultiply()
    b["@"] = MacroMatMul()
    b["/"] = MacroDivide()
    b["//"] = MacroFloorDivide()
    b["%"] = MacroMod()
    b["<<"] = MacroLShift()
    b[">>"] = MacroRShift()
    b["&"] = MacroBitwiseAnd()
    b["|"] = MacroBitwiseOr()
    b["^"] = MacroBitwiseXOr()
    b["[]"] = MacroGetItem()
    b["[]="] = MacroSetItem()
    b["and"] = MacroAnd()
    b["bloc"] = BLOC_VALUE.value
    b["break"] = MacroBreak()
    b["call"] = MacroCall()
    b["case"] = MacroCase()
    b["class"] = MacroClass()
    b["concat"] = MacroConcat()
    b["contains"] = MacroContains()
    b["continue"] = MacroContinue()
    b["def"] = MacroDef()
    b["def_macro"] = MacroDefMacro()
    b["del"] = MacroDel()
    b["del[]"] = MacroDelItem()
    b["delattr"] = MacroDelAttr()
    b["dict_comp"] = MacroDictComp()
    b["dict_lit"] = MacroDictLit()
    b["for"] = MacroFor()
    b["gen"] = MacroGen()
    b["getattr"] = MacroGetAttr()
    b["getenv"] = MacroGetEnv()
    b["if"] = MacroIf()
    b["importpy"] = MacroImportPy()
    b["importsn"] = MacroImportSn()
    b["is"] = MacroIs()
    b["is_not"] = MacroIsNot()
    b["lambda"] = MacroLambda()
    b["list_comp"] = MacroListComp()
    b["list_lit"] = MacroListLit()
    b["neg"] = MacroNeg()
    b["node_list_lit"] = node_list_lit
    b["NodeIdentifier"] = NodeIdentifier
    b["NodeList"] = NodeList
    b["NodeValue"] = NodeValue
    b["not"] = MacroNot()
    b["or"] = MacroOr()
    b["pos"] = MacroPos()
    b["print_sep"] = MacroPrintSep()
    b["quote"] = MacroQuote()
    b["raise"] = MacroRaise()
    b["set_comp"] = MacroSetComp()
    b["set_lit"] = MacroSetLit()
    b["setattr"] = MacroSetAttr()
    b["setm"] = MacroSetMultiple()
    b["try"] = MacroTry()
    b["tuple_lit"] = MacroTupleLit()
    b["unquote"] = MacroUnquote()
    b["while"] = MacroWhile()
    b["with"] = MacroWith()

    parse("(def_macro ++ (e) (quote (:= (unquote e) (+ (unquote e) 1))))").eval(b)
    parse("(def_macro -- (e) (quote (:= (unquote e) (- (unquote e) 1))))").eval(b)

    return b

def parse(phrase):
    return parse_lexeme(LexemeIterator(AL, phrase))

def read_file(path):
    with open(path) as f:
        return f.read()

class Interpreteur:
    def __init__(self, src_dir):
        self.b = create_builtins()
        self.b["__interpreteur__"] = self
        self.module_cache = {}
        self.src_dir = src_dir
    def eval_module(self, module_name, args=None, comp=False):
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        else:
            file_path = module_name.replace(".", "/")
            path = pathlib.Path(self.src_dir, file_path + ".sn")
            file_env = EnvironementLocal(self.b)
            if args is None:
                file_env["__name__"] = module_name
            else:
                file_env["__name__"] = "__main__"
                file_env["args"] = args
            self.module_cache[module_name] = file_env
            st = parse(read_file(path))
            st.eval(file_env)

            if comp:
                buffer = []
                indent = Indenter()
                st.compile(file_env, buffer.append, indent)
                dest_path = pathlib.Path(self.src_dir, file_path + ".py")
                write_file(dest_path, buffer)

            return file_env

def write_file(path, buffer):
    with open(path, "w") as f:
        write = f.write
        for s in buffer:
            write(s)

class Indenter:
    def __init__(self):
        self.level = 0
    def append_indent(self, append):
        for i in range(self.level):
            append("    ")
    def increment(self):
        self.level += 1
    def decrement(self):
        self.level -= 1

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.9")
    parser.add_argument("dir", help="source directory")
    parser.add_argument("module", help="module name")
    parser.add_argument("args", nargs="*", help="optional argument")
    parser.add_argument("-c", "--compile", action="store_true",
                        help="compile file")
    ns = parser.parse_args()

    i = Interpreteur(ns.dir)
    i.eval_module(ns.module, ns.args, ns.compile)
