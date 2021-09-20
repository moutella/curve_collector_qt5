from numpy import linalg as num_linalg
from scipy import linalg as sci_linalg

A = [
    [4, 3, 0],
    [3, 4, -1],
    [0, -1, 4]
]
b = [24, 30, -4]
result = num_linalg.solve(A, b)
print(result)

result = sci_linalg.solve(A, b)
print(result)
