import json
from scipy import sparse
import math
import os
import heapq
from typing import List, Tuple

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



# get gamedata and ids to be used
allgamedata = open("data/gamedata/all_gamedata.json")
allgames = json.load(allgamedata)
allgamedata.close()

allidsdata = open("data/gameids/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()

k = 50
lowerbound = -99999999999999999
A = sparse.lil_array((len(allids), len(allids)))
for i in range(len(allids)):
  if i % 100 == 0:
    print("i:", i)
  info1 = allgames[str(allids[i])]
  #max heap of negative distances
  closest: List[Tuple[float, int]] = [(lowerbound, 0)] * k
  for j in range(len(allids)):
    if i == j:
      continue
    info2 = allgames[str(allids[j])]
    dist = calc_dist(info1, info2)
    if dist > closest[0][0]:
      heapq.heapreplace(closest, (-dist, j))
  col = [pair[1] for pair in closest if pair[0] != lowerbound]
  col.append(len(allids) - 1)
  row = [0] * len(col)
  data = [1] * len(col)
  data[-1] = 0
  entry = sparse.csr_array((data, (row, col)))
  A[i,] = entry


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
sparse.save_npz("data/graphdata/adjacency.npz", A)

print()
print("saved")
print(A.nnz)