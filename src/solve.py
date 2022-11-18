
import progeff

def prepare(expr):
    return expr[:expr.find("=")].replace("(", " ( ").replace(")", " ) ")

def print_eval(expr):
    if isinstance(expr, tuple):
        left, op, right = expr
        left = print_eval(left)
        right = print_eval(right)
        if op == "+":
            res = left + right
            print(left, "+", right, "=", res)
            return res
        if op == "-":
            res = left - right
            print(left, "-", right, "=", res)
            return res
        if op == "*":
            res = left * right
            print(left, "*", right, "=", res)
            return res
        if op == "/":
            res = left // right
            print(left, "/", right, "=", res)
            return res
    else:
        return expr

if __name__ == "__main__":
    import argparse
    import datetime

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.7")
    parser.add_argument("chiffre", type=int, nargs="+")
    parser.add_argument("-c", "--compact", action="store_true")
    parser.add_argument("-t", "--time", action="store_true")

    args = parser.parse_args()

    chiffre = args.chiffre

    start = datetime.datetime.now()

    expr = progeff.arithm_expr_target(chiffre[:-1], chiffre[-1])

    end = datetime.datetime.now()

    if args.compact:
        print(expr)
    else:
        expr = prepare(expr).split()

        expr = progeff.arithm_parse(expr)

        print_eval(expr)

    if args.time:
        print()
        print("temps de calcul :", end - start)
