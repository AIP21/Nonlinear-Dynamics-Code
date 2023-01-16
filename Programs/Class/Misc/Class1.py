def C(n):
    if n % 2 == 0:
        return n / 2
    else:
        return 3 * n + 1


def tripLength(n):
    steps = 0
    while n != 1:
        steps += 1
        n = C(n)

    return steps


def maxLengthBelow(M):
    maxLength = -1
    
    for n in range(1, M):
        val = tripLength(n)
        
        if maxLength < val:
            maxLength = val

    return maxLength


print(maxLengthBelow(0))

# print(C(12))