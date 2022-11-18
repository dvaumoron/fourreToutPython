
import abc
import secrets

class AbstractKey(abc.ABC):
    __slots__ = ("keys", "current")
    def __init__(self):
        self.keys = []
        self.current = 0
    @property
    def key(self):
        key = self.keys[self.current]
        self.current += 1
        if self.current >= len(self.keys):
            self.current = 0
        return key
    def computeFile(self, src_path, dest_path):
        with open(src_path, mode="rb") as src, open(dest_path, mode="wb") as dest:
            for line in src:
                for i in line:
                    dest.write(self.compute(i))
    @classmethod
    @abc.abstractmethod
    def gen(klass, size):
        pass
    @abc.abstractmethod
    def inv(self):
        pass
    @abc.abstractmethod
    def write(self, path):
        pass
    @classmethod
    @abc.abstractmethod
    def read(klass, path):
        pass
    @abc.abstractmethod
    def compute(self, i):
        return i.to_bytes(1, "big")

class SubstitutionKey(AbstractKey):
    __slots__ = ()
    @classmethod
    def gen(klass, size):
        res = klass()
        sr = secrets.SystemRandom()
        for i in range(size):
            l = list(range(256))
            sr.shuffle(l)
            res.keys.append(l)
        return res
    def inv(self):
        res = type(self)()
        for key in self.keys:
            l = [None] * 256
            for i, j in enumerate(key):
                l[j] = i
            res.keys.append(l)
        return res
    def write(self, path):
        with open(path, mode="wb") as f:
            for key in self.keys:
                f.write(bytes(key))
    @classmethod
    def read(klass, path):
        res = klass()
        with open(path, mode="rb") as f:
            l = [i for line in f for i in line]
        lenl = len(l)
        if lenl % 256 != 0:
            raise ValueError("invalid key length")
        for i in range(lenl // 256):
            res.keys.append(l[i*256:(i+1)*256])
        lr = list(range(256))
        for key in res.keys:
            if sorted(key) != lr:
                raise ValueError("invalid substitution key")
        return res
    def compute(self, i):
        return super().compute(self.key[i])

class IntKey(AbstractKey):
    __slots__ = ()
    @classmethod
    def gen(klass, size):
        res = klass()
        for i in range(size * 256):
            res.keys.append(secrets.randbelow(256))
        return res
    def write(self, path):
        with open(path, mode="wb") as f:
            for key in self.keys:
                f.write(key.to_bytes(1, "big"))
    @classmethod
    def read(klass, path):
        res = klass()
        with open(path, mode="rb") as f:
            res.keys.extend(i for line in f for i in line)
        return res

class XOrKey(IntKey):
    __slots__ = ()
    def inv(self):
        return self
    def compute(self, i):
        return super().compute(self.key ^ i)

class AddModuloKey(IntKey):
    __slots__ = ()
    def inv(self):
        res = type(self)()
        for key in self.keys:
            res.keys.append(256 - key)
        return res
    def compute(self, i):
        return super().compute((self.key + i) % 256)

if __name__ == "__main__":
    import argparse

    Keys = {"XOr": XOrKey, "Substitution": SubstitutionKey,
            "AddModulo": AddModuloKey}

    def encode(args):
        key = Keys[args.Key].read(args.key)
        if args.decode:
            key = key.inv()
        key.computeFile(args.src, args.dest)

    def gen(args):
        key = Keys[args.Key].gen(args.size)
        key.write(args.dest)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.9")
    parser.add_argument("-a", "--algorithm", dest="Key", choices=Keys,
                        default="XOr",
                        help="encryption algorithm (default: XOr)")
    subparsers = parser.add_subparsers(help="valid subcommands")

    parser_encode = subparsers.add_parser("encode", help="encode a file")
    parser_encode.add_argument("key", help="key file")
    parser_encode.add_argument("src", help="source file")
    parser_encode.add_argument("dest", help="destination file")
    parser_encode.set_defaults(function=encode, decode=False)

    parser_decode = subparsers.add_parser("decode", help="decode a file")
    parser_decode.add_argument("key", help="key file")
    parser_decode.add_argument("src", help="source file")
    parser_decode.add_argument("dest", help="destination file")
    parser_decode.set_defaults(function=encode, decode=True)

    parser_gen = subparsers.add_parser("genKey", help="generate a key")
    parser_gen.add_argument("dest", help="destination key file")
    parser_gen.add_argument("-s", "--size", type=int, default=1,
                            help="key size (default: 1)")
    parser_gen.set_defaults(function=gen)

    args = parser.parse_args()
    try:
        args.function(args)
    except AttributeError:
        parser.print_usage()
