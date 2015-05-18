
from collections import deque

vals = [1, 4, 2, 67, 8, 3, 4, 7, 4]

def mergesort(vals):
    if len(vals) < 2:
        return vals
    mid = int(len(vals)/2)
    left = deque(mergesort(vals[:mid]))
    right = deque(mergesort(vals[mid:]))

    out = []
    while left or right:
        if left and right:
            print(left)
            print(right)
            if left[0] < right[0]:
                out.append(left.popleft())
            else:
                out.append(right.popleft())
        elif left:
            out.append(left.popleft())
        elif right:
            out.append(right.popleft())
    return out

print(mergesort(vals))
