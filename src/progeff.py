
import bisect
import collections
import heapq
import codi

class UnionFind:
    __slots__ = ("up",)
    def __init__(self, n):
        self.up = list(range(n))
    def find(self, x):
        up_x = self.up[x]
        if up_x == x:
            return x
        else:
            up_x = self.up[x] = self.find(up_x)
            return up_x
    def union(self, x, y):
        repr_x = self.find(x)
        repr_y = self.find(y)
        if repr_x == repr_y:
            return False
        else:
            self.up[repr_y] = repr_x
            return True

@codi.print_call
def anagrams(words):
    words = list(set(words)) # remove duplicate
    d = collections.defaultdict(list)
    join = "".join
    for word in words:
        d[join(sorted(word))].append(word)
    return [seq for seq in d.values() if len(seq) > 1]

@codi.print_call
def power_string(word):
    return len(word) // (word + word).find(word, 1)

PRIME = 72057594037927931
DOMAIN = 128

def matches(s, t, i):
    for j, tj in enumerate(t):
        if s[i + j] != tj:
            return False
    return True

@codi.print_call
def rabin_karp_matching(s, t):
    len_s = len(s)
    len_t = len(t)
    if len_s < len_t:
        return -1
    len_s_t = len_s - len_t
    last_pos = pow(DOMAIN, len_t - 1, PRIME)
    hash_s = 0
    hash_t = 0
    for i, ti in enumerate(t):
        hash_s = (DOMAIN * hash_s + ord(s[i])) % PRIME
        hash_t = (DOMAIN * hash_t + ord(ti)) % PRIME
    for i in range(len_s_t + 1):
        if hash_s == hash_t and matches(s, t, i):
            return i
        if i < len_s_t:
            # roll_hash
            hash_s -= ord(s[i]) * last_pos
            hash_s = (DOMAIN * hash_s + ord(s[i + len_t])) % PRIME
    return -1

def copy_append(seq, elem):
    seq2 = seq[:]
    seq2.append(elem)
    return seq2

@codi.print_call
def levenshtein(x, y):
    n = len(x)
    m = len(y)
    A = [[None] * (m + 1) for i in range(n + 1)]
    A[0][0] = (0, 0, [])
    for i, xi in enumerate(x):
        ip1 = i + 1
        A[ip1][0] = (ip1, -1, copy_append(A[i][0][2], f"suppression de {xi}"))
    for j, yj in enumerate(y):
        jp1 = j + 1
        A[0][jp1] = (jp1, -1, copy_append(A[0][j][2], f"ajout de {yj}"))
    for i, xi in enumerate(x):
        ip1 = i + 1
        for j, yj in enumerate(y):
            jp1 = j + 1
            case_suppress = A[i][jp1]
            suppress = copy_append(case_suppress[2], f"suppression de {xi}")
            case_ajout = A[ip1][j]
            ajout = copy_append(case_ajout[2], f"ajout de {yj}")
            case_shift = A[i][j]
            if xi == yj:
                cout_shift = 0
                op = f"decalage sur {xi}"
            else:
                cout_shift = 1
                op = f"substitution de {xi} par {yj}"
            shift = copy_append(case_shift[2], op)
            A[ip1][jp1] = min((case_suppress[0] + 1, -len(suppress), suppress),
                              (case_ajout[0] + 1, -len(ajout), ajout),
                              (case_shift[0] + cout_shift, -len(shift), shift))
    Anm = A[n][m]
    return Anm[0], Anm[2]

@codi.print_call
def longest_common_subsequence(x, y):
    n = len(x)
    m = len(y)
    A = [[[] for j in range(m + 1)] for i in range(n + 1)]
    for i, xi in enumerate(x):
        ip1 = i + 1
        for j, yj in enumerate(y):
            jp1 = j + 1
            if xi == yj:
                A[ip1][jp1] = copy_append(A[i][j], xi)
            else:
                A[ip1][jp1] = max(A[ip1][j], A[i][jp1], key=len)
    return A[n][m]

@codi.print_call
def longest_increasing_subsequence(x):
    p = [None] * len(x)
    h = [None]
    b = [float("-inf")]
    h_append = h.append
    b_append = b.append
    bisect_left = bisect.bisect_left
    for i, xi in enumerate(x):
        top = b[-1]
        if xi > top:
            p[i] = h[-1]
            h_append(i)
            b_append(xi)
        elif xi < top:
            k = bisect_left(b, xi)
            h[k] = i
            b[k] = xi
            p[i] = h[k - 1]
    q = h[-1]
    s = []
    s_append = s.append
    while q is not None:
        s_append(x[q])
        q = p[q]
    return s[::-1]

@codi.print_call
def topological_order_dfs(graph):
    n = len(graph)
    order = []
    order_append = order.append
    times_seen = [-1] * n
    for start in range(n):
        if times_seen[start] == -1:
            times_seen[start] = 0
            to_visit = [start]
            to_visit_pop = to_visit.pop
            to_visit_append = to_visit.append
            while to_visit:
                node = to_visit[-1]
                children = graph[node]
                if times_seen[node] == len(children):
                    to_visit_pop()
                    order_append(node)
                else:
                    child = children[times_seen[node]]
                    times_seen[node] += 1
                    if times_seen[child] == -1:
                        times_seen[child] = 0
                        to_visit_append(child)
    return order[::-1]

@codi.print_call
def topological_order(graph):
    indegs = [0] * len(graph)
    for graph_node in graph:
        for neighbor in graph_node:
            indegs[neighbor] += 1
    stack = [node for node, indeg in enumerate(indegs) if indeg == 0]
    stack_pop = stack.pop
    stack_append = stack.append
    order = []
    order_append = order.append
    while stack:
        node = stack_pop()
        order_append(node)
        for neighbor in graph[node]:
            indegs[neighbor] -= 1
            if indegs[neighbor] == 0:
                stack_append(neighbor)
    return order

def kosaraju_dfs(graph, nodes, order_append, sccp_append):
    times_seen = [-1] * len(graph)
    for start in nodes:
        if times_seen[start] == -1:
            to_visit = [start]
            to_visit_pop = to_visit.pop
            to_visit_append = to_visit.append
            times_seen[start] = 0
            comp = [start]
            comp_append = comp.append
            sccp_append(comp)
            while to_visit:
                node = to_visit[-1]
                children = graph[node]
                if times_seen[node] == len(children):
                    to_visit_pop()
                    order_append(node)
                else:
                    child = children[times_seen[node]]
                    times_seen[node] += 1
                    if times_seen[child] == -1:
                        times_seen[child] = 0
                        to_visit_append(child)
                        comp_append(child)

def reverse(graph):
    rev_graph = [[] for node in graph]
    for node, graph_node in enumerate(graph):
        for neighbor in graph_node:
            rev_graph[neighbor].append(node)
    return rev_graph

def false_append(x):
    pass

@codi.print_call
def kosaraju(graph):
    order = []
    kosaraju_dfs(graph, range(len(graph)), order.append, false_append)
    sccp = []
    kosaraju_dfs(reverse(graph), order[::-1], false_append, sccp.append)
    return sccp[::-1]

@codi.print_call
def dinic(graph, capacity, source, target):
    Q = collections.deque()
    Q_appendleft = Q.appendleft
    Q_pop = Q.pop
    total = 0
    n = len(graph)
    flow = [[0] * n for u in range(n)]
    max_source = sum(capacity[source][v] for v in graph[source])
    while True:
        Q_appendleft(source)
        lev = [None] * n
        lev[source] = 0
        while Q:
            u = Q_pop()
            for v in graph[u]:
                if lev[v] is None and capacity[u][v] > flow[u][v]:
                    lev[v] = lev[u] + 1
                    Q_appendleft(v)
        if lev[target] is None:
            return flow, total
        limit = max_source - total
        total += _dinic_step(graph, capacity, lev, flow, source, target, limit)

def _dinic_step(graph, capacity, lev, flow, u, target, limit):
    if limit <= 0:
        return 0
    if u == target:
        return limit
    val = 0
    for v in graph[u]:
        residuel = capacity[u][v] - flow[u][v]
        if lev[v] == lev[u] + 1 and residuel > 0:
            z = min(limit, residuel)
            aug = _dinic_step(graph, capacity, lev, flow, v, target, z)
            flow[u][v] += aug
            flow[v][u] -= aug
            val += aug
            limit -= aug
    if val == 0:
        lev[u] = None
    return val

def create_huffman(phrase):
    c = collections.Counter(phrase)
    h = []
    heappush = heapq.heappush
    i = 0
    for k, v in c.items():
        heappush(h, (v, i, k))
        i += 1
    heappop = heapq.heappop
    while len(h) > 1:
        a = heappop(h)
        b = heappop(h)
        heappush(h, (a[0] + b[0], i, [a[2], b[2]]))
        i += 1
    code = {}
    tree = h[0][2]
    extract_huffman(code, tree)
    return code, tree

def extract_huffman(code, tree, prefix=""):
    if isinstance(tree, list):
        l, r = tree
        extract_huffman(code, l, prefix + "0")
        extract_huffman(code, r, prefix + "1")
    else:
        code[tree] = prefix

def encode_huffman(huff, phrase):
    code = huff[0]
    buffer = []
    buffer_append = buffer.append
    for c in phrase:
        buffer_append(code[c])
    return "".join(buffer)

def decode_huffman(huff, phrase):
    tree = huff[1]
    buffer = []
    buffer_append = buffer.append
    current = tree
    for c in phrase:
        if c == "0":
            current = current[0]
        else:
            current = current[1]
        if isinstance(current, str):
            buffer_append(current)
            current = tree
    return "".join(buffer)

@codi.print_call
def kruskal(graph, weight):
    edges = []
    edges_append = edges.append
    for u, (graph_u, weight_u)in enumerate(zip(graph, weight)):
        for v in graph_u:
            edges_append((weight_u[v], u , v))
    edges.sort()
    n = len(graph)
    diff = UnionFind(n).union
    prec = [None] * n
    for w, u, v in edges:
        if diff(u, v):
            prec[v] = u
    return prec

def pgcd(a, b):
    if b == 0:
        return a
    else:
        return pgcd(b, a % b)

def bezout(a, b):
    if b == 0:
        return (1, 0)
    else:
        u, v = bezout(b, a % b)
        return (v, u - (a // b) * v)

@codi.print_call
def fast_pow(a, b):
    p2 = 1
    ap2 = a
    res = 1
    while b > 0:
        if p2 & b > 0:
            b -= p2
            res *= ap2
        p2 *= 2
        ap2 = ap2 * ap2
    return res

def eratosthene(n):
    prime = [True] * n
    res = [2]
    res_append = res.append
    for i in range(3, n, 2):
        if prime[i]:
            res_append(i)
            for j in range(2 * i, n, i):
                prime[j] = False
    return res

priority = {";": 0, "(": 1, ")": 2, "+": 3, "-": 3, "*": 4, "/": 4}

def arithm_parse(line):
    vals = []
    ops = []
    vals_append = vals.append
    vals_pop = vals.pop
    ops_append = ops.append
    ops_pop = ops.pop
    for tok in line + [";"]:
        if tok in priority:
            if tok != "(":
                pTok = priority[tok]
                while ops and priority[ops[-1]] >= pTok:
                    right = vals_pop()
                    left = vals_pop()
                    vals_append((left, ops_pop(), right))
            if tok == ")":
                ops_pop()
            else:
                ops_append(tok)
        elif tok.isdigit():
            vals_append(int(tok))
        else:
            vals_append(tok)
    return vals_pop()

def arithm_eval(env, expr):
    if isinstance(expr, tuple):
        left, op, right = expr
        left = arithm_eval(env, left)
        right = arithm_eval(env, right)
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left // right
    elif isinstance(expr, int):
        return expr
    else:
        return env[expr]

def all_subsets(n, card):
    if card == 0:
        yield 0
    else:
        cardM1 =  card - 1
        for i in range(cardM1, n):
            i2 = 1 << i
            for e in all_subsets(i, cardM1):
                yield e | i2

def arithm_expr_target(x, target):
    n = len(x)
    m = 1 << n
    expr = [None] * m
    i = 1
    for e in x:
        expr[i] = {e: (str(e), 0)}
        i <<= 1
    done = set()
    for card in range(2, n + 1):
        for S in all_subsets(n, card):
            exprS = expr[S] = {}
            for L in range(1, S):
                if L & S == L:
                    R = S ^ L
                    if (R, L) not in done:
                        done.add((L, R))
                        exprRItems = expr[R].items()
                        for vL, rL in expr[L].items():
                            eL = rL[0]
                            cL = rL[1]
                            for vR, rR in exprRItems:
                                eR = rR[0]
                                opCost = cL + rR[1] + 1
                                if vL not in exprS:
                                    exprS[vL] = rL
                                if vR not in exprS:
                                    exprS[vR] = rR
                                vLnot0 = vL != 0
                                vRnot0 = vR != 0
                                if vLnot0 and vRnot0:
                                    add_or_replace(exprS, vL + vR, opCost, eL, "+", eR)
                                    if vL > vR:
                                        add_or_replace(exprS, vL - vR, opCost, eL, "-", eR)
                                    elif vR > vL:
                                        add_or_replace(exprS, vR - vL, opCost, eR, "-", eL)
                                vLnot1 = vL != 1
                                vRnot1 = vR != 1
                                if vLnot1 and vRnot1:
                                    add_or_replace(exprS, vL * vR, opCost, eL, "*", eR)
                                if vRnot0 and vRnot1 and vL % vR == 0:
                                    add_or_replace(exprS, vL // vR, opCost, eL, "/", eR)    
                                if vLnot0 and vLnot1 and vR % vL == 0:
                                    add_or_replace(exprS, vR // vL, opCost, eR, "/", eL)
    del done
    exprTout = expr[m - 1]
    del expr
    signs = (-1, 1)
    for dist in range(target + 1):
        for sign in signs:
            val = target + sign * dist
            if val in exprTout:
                return f"{exprTout[val][0]} = {val}"
    return "no solution found"

EXPR_FORMAT = "({} {} {})".format

def add_or_replace(exprS, newValue, opCost, eL, op, eR):
    if newValue in exprS:
        opCost2 = exprS[newValue][1]
        if opCost < opCost2:
            exprS[newValue] = EXPR_FORMAT(eL, op, eR), opCost
    else:
        exprS[newValue] = EXPR_FORMAT(eL, op, eR), opCost

if __name__ == "__main__":
    phrase = ("le chien marche vers sa niche et trouve une limace de "
              "chine nue pleine de malice qui lui fait du charme")
    print(anagrams(phrase.split()))

    print()

    print(power_string("abcd"))
    print(power_string("aaaa"))
    print(power_string("abaabaaba"))

    print()

    print(rabin_karp_matching("lalopalalali", "lala"))

    print()

    print(levenshtein("AUDI", "LADA"))
    print(levenshtein("abracadabra", "alakazam"))

    print()

    print(longest_common_subsequence("abcdae", "aedbea"))

    print()

    print(longest_increasing_subsequence([9,3,1,4,1,5,9,2,6,5,4,5,3,9,7,9]))

    print()

    print(topological_order_dfs([[1, 4], [], [0], [], [1, 3]]))
    print(topological_order([[1, 4], [], [0], [], [1, 3]]))

    print()

    print(kosaraju([[4], [0], [1,3], [2], [1], [1, 4, 6], [2,5], [3, 6]]))

    print()

    print(dinic([[1, 2], [0, 2, 3, 4], [0, 1, 4], [1, 4, 5], [1, 2, 3, 5], [3, 4]],
                [[0, 10, 10, 0, 0, 0],
                 [10, 0, 2, 4, 8, 0],
                 [10, 2, 0, 0, 9, 0],
                 [0, 4, 0, 0, 5, 10],
                 [0, 8, 9, 5, 0, 10],
                 [0, 0, 0, 10, 10, 0]],
                0, 5))

    print()

    huff = create_huffman(phrase)
    phrase2 = encode_huffman(huff, phrase)
    print(phrase2)
    print(decode_huffman(huff, phrase2))

    print()

    print(kruskal([[1,2], [0,2], [0,1]], [[0, 2, 2], [3, 0, 1], [1, 3, 0]]))

    print()

    print("pgcd(13, 8) =", pgcd(13, 8))
    print("bezout(13, 8) =", bezout(13, 8))

    print()

    print(fast_pow(2, 13))

    print()

    print("primes =", eratosthene(100))

    print()

    env = {"x": 2}
    print("env =", env)
    print("4 + (1 + x) * 3 =",
          arithm_eval(env, arithm_parse("4 + ( 1 + x ) * 3".split())))

    print()

    print(arithm_expr_target([4, 100, 6, 75, 8, 7], 573))
