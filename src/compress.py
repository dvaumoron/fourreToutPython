
import json
import progeff

bin_to_hex = {"0000": "0", "0001": "1", "0010": "2", "0011": "3",
              "0100": "4", "0101": "5", "0110": "6", "0111": "7",
              "1000": "8", "1001": "9", "1010": "a", "1011": "b",
              "1100": "c", "1101": "d", "1110": "e", "1111": "f"}

hex_to_bin = {"0": "0000", "1": "0001", "2": "0010", "3": "0011",
              "4": "0100", "5": "0101", "6": "0110", "7": "0111",
              "8": "1000", "9": "1001", "a": "1010", "b": "1011",
              "c": "1100", "d": "1101", "e": "1110", "f": "1111"}

def convert_bin_to_hex(phrase):
    n = len(phrase)
    skip = n % 8
    if skip != 0:
        skip = 8 - skip
        phrase += "0" * skip
        n += skip
    buffer = []
    append = buffer.append
    for i in range(0, n, 4):
        append(bin_to_hex[phrase[i:i + 4]])
    return skip, "".join(buffer)

def convert_hex_to_bin(skip, phrase):
    buffer = []
    append = buffer.append
    for c in phrase:
        append(hex_to_bin[c])
    res = "".join(buffer)
    if skip == 0:
        return res
    else:
        return res[:-skip]

def read_txt_file(path):
    buffer = []
    append = buffer.append
    with open(path) as f:
        for line in f:
            append(line)
    return "".join(buffer)

def read_byte_file(path):
    buffer = bytearray()
    with open(path, "rb") as f:
        for line in f:
            buffer += line
    return buffer

def encode(key_path, src_path, dest_path):
    txt = read_txt_file(src_path)
    key = progeff.create_huffman(txt)
    with open(key_path, "w") as f:
        json.dump(key[1], f, ensure_ascii=False, separators=(",", ":"))
    txt_bin = progeff.encode_huffman(key, txt)
    del txt
    skip, txt_hex = convert_bin_to_hex(txt_bin)
    skip_b = skip.to_bytes(1, "big")
    txt_bytes = bytes.fromhex(txt_hex)
    del txt_hex
    with open(dest_path, "wb") as f:
        f.write(skip_b)
        f.write(txt_bytes)

def decode(key_path, src_path, dest_path):
    txt_bytes = read_byte_file(src_path)
    skip = txt_bytes[0]
    txt_hex = txt_bytes[1:].hex()
    del txt_bytes
    txt_bin = convert_hex_to_bin(skip, txt_hex)
    del txt_hex
    with open(key_path, "r") as f:
        key = (None, json.load(f))
    txt = progeff.decode_huffman(key, txt_bin)
    del txt_bin
    del key
    with open(dest_path, "w") as f:
        f.write(txt)

if __name__ == "__main__":
    import argparse

    actions = {"encode": encode, "decode": decode}

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.3")
    parser.add_argument("action", choices=actions)
    parser.add_argument("key", help="key file")
    parser.add_argument("src", help="source file")
    parser.add_argument("dest", help="destination file")
    args = parser.parse_args()

    actions[args.action](args.key, args.src, args.dest)
