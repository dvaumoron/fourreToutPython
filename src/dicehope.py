
d20 = range(1, 21)

sum_max = 0
sum_min = 0

for a in d20:
    for b in d20:
        if a > b:
            sum_max += a
            sum_min += b
        else:
            sum_max += b
            sum_min += a

print("hope best of 2d20 :", sum_max / 400)
print("hope worst of 2d20 :", sum_min / 400)

d6 = range(1, 7)

s = 0

for a in d6:
    for b in d6:
        for c in d6:
            for d in d6:
                s += a + b + c + d - min(a, b, c, d)

print("hope 3 best of 4d6 :", s / (6**4))

s = 0

for a in d6:
    for b in d6:
        for c in d6:
            for d in d6:
                for e in d6:
                    l = [a, b, c, d ,e]
                    l.sort()
                    s += l[2] + l[3] + l[4]

print("hope 3 best of 5d6 :", s / (6**5))
