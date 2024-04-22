from scipy import sparse
import json
import random
from bayes_opt import BayesianOptimization
import heapq
from typing import List, Tuple

#Training params
split = 1
numwanted = 50
numplayers = 1000

#ML params
cutoff = 0.25
k = 100 #(k determined by graph)

lowerbound = -99999999999999999


#calculate P
parallel = ""
parallel = "_parallel"
A = sparse.load_npz("data/gamedata/adjacency_" + str(k) + parallel + ".npz")
A = A.tocsr()
D_INV= sparse.dia_array(([1/float(x) if x != 0 else 0 for x in A.sum(axis = 1)], [0]), A.shape)
P = D_INV @ A

#get all ids
allidsdata = open("data/gamedata/all_usable_ids.json")
allids = json.load(allidsdata)
allidsdata.close()


#get labelled nodes
info = open("data/playerdata/player_info.json")
playerinfo = json.load(info)
info.close() 

items = list(playerinfo.items())[:numplayers]
random.shuffle(items)
#the last 3 games are latest
#otherwise ordered by id
def propagation(T, numrec = numwanted, playerID = None):
    #define label propagation
    def label(ids):
        row = ids
        row.append(len(allids) - 1)
        col = [0] * len(ids)
        data = [1] * len(ids)
        data[-1] = 0
        y0 = sparse.csc_array((data, (row, col)))
        y = y0.todense()
        for _ in range(int(T)):
            y = P @ y
            for i in ids:
                y[i, 0] = 1
        return y


    recs = {}
    loss = 0
    for player, games in items:
        #get player data
        if player == '76561198841140464' or len(games) < 4:
            continue
        
        if playerID:
            player = playerID
            games = playerinfo[playerID]
        #change player data into id index and split
        games = [allids.index(str(game)) for game in games if str(game) in allids]
        latest = games[-3:]
        shuffled = games[:-3]
        random.shuffle(shuffled)
        train = shuffled[:int(split * len(shuffled))]
        test = shuffled[int(split * len(shuffled)):]
        test.extend(latest)

        #label
        true = 0
        labels = label(train)
        rec: List[Tuple[float, int]] = [(lowerbound, -1)] * int(numrec)
        for j in range(len(allids)):
            if j not in train and labels[j, 0] > rec[0][0]:
                heapq.heapreplace(rec, (labels[j, 0], j))


        for game in rec:
            if game in train:
                true += 1
        
        #get metrics and recomendations 
        acc = true / float(len(test))
        recs[player] = [allids[x[1]] for x in rec if x[1] > -1]

        #get loss
        loss += acc

        if playerID:
            print("loss:", loss)
            print("recs:", recs)
            break
    return loss

bounds = {'T': (5, 25), 'numrec': (50, 150)}
optimizer = BayesianOptimization(
    f = propagation,
    pbounds = bounds
)

optimizer.maximize()
print(optimizer.max)

propagation(playerID='76561198841140464', T=8)

#augment rec list with friends/recent games?