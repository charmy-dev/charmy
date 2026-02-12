def c(x):
    if isinstance(x, float):
        if 0 < x <= 1.0:
            x = x * 255
    return x


r, g, b, a = 255, 1.0, 0.5, 0.5
print(c(r), c(g), c(b), c(a))


"""r, g, b, a = 255, 1.0, 0.5, 0.5

for index, clin in enumerate([r, g, b, a]):
    if isinstance(clin, float):
        if 0 < clin <= 1.0:
            clin = clin * 255

print(r, g, b, a)"""
