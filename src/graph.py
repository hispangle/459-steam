# use lanczos alg for eigen
from scipy import sparse 
import json

test1 = sparse.csr_array([1, 0])
test2 = sparse.csr_array([0, 0])

print(test1)
print()
print(test2)
print()
testm = sparse.vstack([test1, test2])
print(testm)

print()
print(testm[0,1])
print()
print(testm @ testm.T)
print()
print(testm + testm.T)



allidsdata = open("data/gameids/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()

for i in range(len(allids)):
    iblock = int(i / 1000)
    adji = []
    for j in range(len(allids)):
        if i == j:
            continue
        jblock = int(j / 1000)



