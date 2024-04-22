from scipy import sparse
import numpy as np
import json
import heapq
from typing import List, Tuple
import joblib
import math

# testi1 = [2, 4, 5]
# col = testi1
# row = [0] * len(col)
# data = [1] * len(col)
# print(sparse.csr_array((data, (row, col))))
# print(sparse.csr_array((data, (row, col))).todense())


# test1 = sparse.csr_array([1, 1])
# test2 = sparse.csr_array([0, 1])
# test3 = sparse.csr_array([0, 5])

# print(test1)
# print()
# print(test2)
# print()
# testm = sparse.vstack([test1, test2])
# test4 = sparse.vstack([testm, test3])
# print(test4)

# print()
# print(testm[0,1])
# print()
# print(testm @ testm.T)
# print()
# print(testm + testm.T)


# #test all 1
# testm = testm + testm.T
# indices = sparse.find(testm)
# row = indices[0]
# col = indices[1]
# data = [1] * len(row)
# print()
# print("final")
# print(sparse.csr_array((data, (row, col))))

# print()
# print(testm)


# print()
# print("test col")
# A = sparse.lil_array((3, 2))
# A[2,] = test3
# print(A.tocsr())

allgamedata = open("data/gamedata/all_gamedata.json")
allgames = json.load(allgamedata)
allgamedata.close()

allidsdata = open("data/gamedata/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()

#parameters and variables
k = 50
num_cores = 3
lowerbound = -99999999999999999

print("k:", k)
#computes distances of two lists
def list_diff(info1, info2, key):
  if key not in info1.keys() or key not in info2.keys():
    return 2.0

  look1 = set(info1[key])
  look2 = set(info2[key])
  if len(look1) == 0 and len(look2) == 0:
    return 0
  cost = len(look1.difference(look2)) + len(look2.difference(look1))
  return cost / (len(look1) + len(look2))

#computes distance of two numbers
def num_diff(info1, info2, key):
  if key not in info1.keys() or key not in info2.keys():
    return 100
  return abs(info1[key] - info2[key])


#calculates distance between 2 games
def calc_dist(gameinfo1, gameinfo2):
  devcost = list_diff(gameinfo1, gameinfo2, 'developers')
  pubcost = list_diff(gameinfo1, gameinfo2, 'publishers')
  genrecost = list_diff(gameinfo1, gameinfo2, 'genres')
  catcost = list_diff(gameinfo1, gameinfo2, 'categories')
  platcost = list_diff(gameinfo1, gameinfo2, 'platforms')

  metacost = num_diff(gameinfo1, gameinfo2, 'metacritic')
  reccost = num_diff(gameinfo1, gameinfo2, 'recommendations')
  datecost = num_diff(gameinfo1, gameinfo2, 'release_date')
  pricecost = num_diff(gameinfo1, gameinfo2, 'price_overview')
  achcost = num_diff(gameinfo1, gameinfo2, 'achievements')

  #totals cost based on weights
  costs = [devcost, pubcost, genrecost, catcost, platcost, metacost, reccost, datecost, pricecost, achcost]
  weights = [5, 8, 35, 15, 0.25, 0.5, 0.0001, 0.15, 0.0005, 0.1]
  dist = 0
  for cost, weight in zip(costs, weights):
    dist += cost * weight
  return int(10 * dist + 1)


#make a row
def calc_row(rownum):
    
    info1 = allgames[str(allids[rownum])]
    #max heap of negative distances
    closest: List[Tuple[float, int]] = [(lowerbound, 0)] * k
    for colnum in range(len(allids)):
        if rownum == colnum:
            continue
        info2 = allgames[str(allids[colnum])]
        dist = calc_dist(info1, info2)
        if dist > closest[0][0]:
            heapq.heapreplace(closest, (-dist, colnum))
    
    #make column and append it to A
    col = [pair[1] for pair in closest if pair[0] != lowerbound]
    col.append(len(allids) - 1)
    row = [0] * len(col)
    data = [1] * len(col)
    data[-1] = 0
    return sparse.csr_array((data, (row, col)))
   
      

rows_per_core = math.ceil(len(allids) / num_cores)
def adjecencyblock(block):
    tempA = sparse.lil_array((0, len(allids)))
    for i in range(block * rows_per_core, min((block + 1) * rows_per_core, len(allids))):
        if i % 1000 == 0:
            print("block:", block, "\ti:", i)
        tempA = sparse.vstack([tempA, calc_row(i)])
    return tempA

A = sparse.vstack(joblib.Parallel(num_cores)(joblib.delayed(adjecencyblock)(i) for i in range(num_cores)))

#do final calculations
print()
print("A")
print(A)
print(A.nnz)
A = A.tocsr()
A = A + A.T
indices = sparse.find(A)
row = indices[0]
col = indices[1]
data = [1] * len(row)
A = sparse.csr_array((data, (row, col)))
sparse.save_npz("data/gamedata/adjacency_" + str(k) + "_parallel.npz", A)

print()
print("saved")
print(A)
print(A.nnz)

