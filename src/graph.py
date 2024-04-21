from scipy import sparse
import numpy as np
import json
import heapq
from typing import List, Tuple
import joblib
import math

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

allgamedata = open("data/gamedata/all_gamedata.json")
allgames = json.load(allgamedata)
allgamedata.close()

allidsdata = open("data/gameids/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()

#parameters and variables
k = 50
lowerbound = -99999999999999999
A = sparse.lil_array((len(allids), len(allids)))
num_per_block = 1000
numblocks = math.ceil(len(allids) / num_per_block)


#computes distances of two lists
def list_diff(info1, info2, key):
  if key not in info1.keys() or key not in info2.keys():
    return 1.0

  if len(info1[key]) == 0 and len(info2[key]) == 0:
    return 0
  
  cost = 0
  for key1 in info1[key]:
    if key1 not in info2[key]:
      cost += 1
  for key2 in info2[key]:
    if key2 not in info1[key]:
      cost += 1
  return cost / (len(info1[key]) + len(info2[key]))

#computes distance of two numbers
def num_diff(info1, info2, key, div = False):
  if key not in info1.keys() or key not in info2.keys():
    return 1 if div else 10
  if info1[key] == info2[key]:
    return 0
  return 1 - min(info1[key], info2[key]) / max(info1[key], info2[key]) if div else abs(info1[key] - info2[key])


#calculates distance between 2 games
def calc_dist(gameinfo1, gameinfo2):
  devcost = list_diff(gameinfo1, gameinfo2, 'developers')
  pubcost = list_diff(gameinfo1, gameinfo2, 'publishers')
  genrecost = list_diff(gameinfo1, gameinfo2, 'genres')
  catcost = list_diff(gameinfo1, gameinfo2, 'categories')
  platcost = list_diff(gameinfo1, gameinfo2, 'platforms')

  metacost = num_diff(gameinfo1, gameinfo2, 'metacritic')
  reccost = num_diff(gameinfo1, gameinfo2, 'recommendations', True)
  datecost = num_diff(gameinfo1, gameinfo2, 'release_date')
  pricecost = num_diff(gameinfo1, gameinfo2, 'price_overview')
  achcost = num_diff(gameinfo1, gameinfo2, 'achievements', True)

  #totals cost based on weights
  costs = [devcost, pubcost, genrecost, catcost, platcost, metacost, reccost, datecost, pricecost, achcost]
  weights = [5, 5, 50, 10, 0.5, 0.05, 0.75, 0.20, 0.0025, 0.3]
  dist = 0
  for cost, weight in zip(costs, weights):
    dist += cost * weight
  return int(10 * dist + 1)


#make a row
def calc_row(rownum):
    
    info1 = allgames[str(allids[rownum])]
    #max heap of negative distances
    closest: List[Tuple[float, int]] = [(lowerbound, 0)] * k
    dists = {}
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
    entry = sparse.csr_array((data, (row, col)))
    A[rownum,] = entry
   
      
num_cores = 6
rows_per_core = math.ceil(len(allids) / num_cores)
def adjecencyblock(block):
    for i in range(block * rows_per_core, min((block + 1) * rows_per_core, len(allids))):
        if i % 100 == 0:
            print("block:", block, "\ti:", i)
        calc_row(i)

joblib.Parallel(num_cores)(joblib.delayed(adjecencyblock)(i) for i in range(num_cores))

#do final calculations
print()
print("A")
print(A.nnz)
A = A.tocsr()
A = A + A.T
indices = sparse.find(A)
row = indices[0]
col = indices[1]
data = [1] * len(row)
A = sparse.csr_array((data, (row, col)))
sparse.save_npz("data/graphdata/adjacency_parallel.npz", A)

print()
print("saved")
print(A.nnz)

