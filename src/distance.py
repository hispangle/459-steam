import json
import math

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
def num_diff(info1, info2, key):
  if key not in info1.keys() or key not in info2.keys() or info1[key] == info2[key]:
    return 0
  return 1 - min(info1[key], info2[key]) / max(info1[key], info2[key])


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
  weights = [0.5, 0.5, 5, 1, 2, 0.5, 0.25, 0.1, 2.5, 0.1]
  dist = 0
  for cost, weight in zip(costs, weights):
    dist += cost * weight

  return int(100 * dist + 1)



# get gamedata and ids to be used
dists = {}
allgamedata = open("data/gamedata/all_gamedata.json")
allgames = json.load(allgamedata)
allgamedata.close()

allidsdata = open("data/gameids/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()

print(len(allids))
# calculate distances by block
num_per_block = 1000
numblocks = math.ceil(len(allids) / num_per_block)

#get last block calculated
try:
    lastblockdata = open("data/graphdata/dists/lastblock.json")
    lastblock = json.load(lastblockdata)
    lastblockdata.close()
except:
    lastblock = [0, 0]
lasti = lastblock[0]
lastj = lastblock[1]


for i in range(lasti, numblocks):
    #get blocks
    fail = False
    jlow = lastj if i == lasti else i
    for j in range(jlow, numblocks):
        print(str(i) + ", " + str(j))
        block1 = num_per_block * i
        block2 = num_per_block * j
        blockdists = []

        #calculate distances between selected blocks
        for index1 in range(block1, min(block1 + num_per_block, len(allids))):
            #get game info
            game1 = allids[index1]

            #node in block i not found
            if str(game1) not in allgames.keys(): 
                fail = True
                break

            info1 = allgames[str(game1)]

            
            for index2 in range(block2, min(block2 + num_per_block, len(allids))):
                #no need to calculate distance between self
                if index1 == index2:
                    continue

                #get game info
                game2 = allids[index2]

                #node in block j failed
                if str(game2) not in allgames.keys(): 
                    fail = True
                    break

                info2 = allgames[str(game2)]
                blockdists.append(calc_dist(info1, info2))
            
            #break out of bad block
            if fail:
               break
        
        #bad block
        if fail:
           break

        #dump distances to block file
        blockfile = open("data/graphdata/dists/dist_" + str(i) + "_" + str(j) + ".json", "w")
        json.dump(blockdists, blockfile)
        blockfile.close()

        lastblockdata = open("data/graphdata/dists/lastblock.json", "w")
        json.dump([i, j], lastblockdata)
        lastblockdata.close()

