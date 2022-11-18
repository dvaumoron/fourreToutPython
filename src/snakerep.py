
import snake
import traceback

parse = snake.parse
print_exc = traceback.print_exc

class REP(snake.Interpreteur):
    def __init__(self, src_dir):
        super().__init__(src_dir)
        self.local_env = snake.EnvironementLocal(self.b)
        parse("(def_macro quit () (quote (:= continue_rep False)))").eval(self.local_env)
    def main(self):
        self.local_env["continue_rep"] = True      

        while self.local_env["continue_rep"]:
            phrase = read_input()
            try:
                res = parse(phrase).eval(self.local_env)
                self.local_env["_"] = res
                if res is not None:
                    print(repr(res))
            except Exception:
                print_exc()

def read_input():
    line = input(">>> ")
    buffer = []
    indentation = count_indentation(line)
    multiple = False
    while indentation > 0:
        multiple = True
        buffer.append(line)
        line = input("... ")
        indentation += count_indentation(line)
    if multiple:
        buffer.append(line)
        return "\n".join(buffer)
    else:
        return line

def count_indentation(line):
    res = 0
    it = iter(line)
    disable = False
    for c in it:
        if disable:
            if c == "\\":
                next(it)
            elif c == "\"":
                disable = False
        else:
            if c == "(":
                res += 1
            elif c == ")":
                res -= 1
            elif c == "\"":
                disable = True
            elif c == "#":
                break
    return res

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.2")
    parser.add_argument("dir", help="source directory")
    ns = parser.parse_args()

    rep = REP(ns.dir)
    rep.main()
