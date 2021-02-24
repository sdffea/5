import random

import numpy


def makefunc():
    isbn = numpy.empty(13, dtype=int)
    isbn[0] = 9
    isbn[1] = 7
    isbn[2] = random.randint(8, 9)
    isbn[3] = random.randint(0, 1)
    for i in range(4, 12):
        isbn[i] = random.randint(0, 9)
    x = 0
    for q in range(13):
        if q % 2 == 0:
            x += isbn[q]
        else:
            x += (3 * isbn[q])
    isbn[12] = 10 - (x % 10)
    b = ""
    for c in range(13):
        b += str(isbn[c])
    return b
