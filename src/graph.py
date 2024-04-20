# use lanczos alg for eigen
# augment dists by int(dist/2 * min(1, log(f) / h) + dist/2)
# f is numfriends
# h is number of friends who own the game
# expensive and probably unfeasable
# friend graph?
# order propagated labels based on # friends own?
# label propagation on friend graph?

from scipy import sparse
import numpy as np
import json

testi1 = [2, 4, 5]
col = testi1
row = [0] * len(col)
data = [1] * len(col)
print(sparse.csr_array((data, (row, col))))
print(sparse.csr_array((data, (row, col))).todense())


test1 = sparse.csr_array([1, 1])
test2 = sparse.csr_array([0, 1])
test3 = sparse.csr_array([0, 5])

print(test1)
print()
print(test2)
print()
testm = sparse.vstack([test1, test2])
test4 = sparse.vstack([testm, test3])
print(test4)

print()
print(testm[0,1])
print()
print(testm @ testm.T)
print()
print(testm + testm.T)


#test all 1
testm = testm + testm.T
indices = sparse.find(testm)
row = indices[0]
col = indices[1]
data = [1] * len(row)
print()
print("final")
print(sparse.csr_array((data, (row, col))))

# print()
# print(testm)


# print()
# print("test col")
# A = sparse.lil_array((3, 2))
# A[2,] = test3
# print(A.tocsr())
# allidsdata = open("data/gameids/all_usable_ids.json")
# allids = json.load(allidsdata)
# allidsdata.close()

# for i in range(len(allids)):
#     iblock = int(i / 1000)
#     for j in range(len(allids)):
#         jblock = int(j / 1000)
#         #len - i - 1 is length of list of node


