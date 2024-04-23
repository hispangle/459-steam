from scipy import sparse
import json
import random
from bayes_opt import BayesianOptimization
import heapq
from typing import List, Tuple
import math

#Training params
split = 1
numwanted = 25
numplayers = 100

#ML params
k = 50 #(k determined by graph)
print("k:", k)

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
info = open("data/playerdata/player_free_info.json")
playerinfo = json.load(info)
info.close() 

items = list(playerinfo.items())[:numplayers]
random.shuffle(items)
#the last 3 games are latest
#otherwise ordered by id
def propagation(T = 6, numrec = numwanted, playerID = None, khat = k):
    if int(khat) == 0:
        khat = 10
    if int(khat) == 1:
        khat = 25
    if int(khat) == 2:
        khat = 50
    if int(khat) == 3:
        khat = 100

    #calculate P
    parallel = ""
    parallel = "_parallel"
    A = sparse.load_npz("data/gamedata/adjacency_" + str(khat) + parallel + ".npz")
    A = A.tocsr()
    D_INV= sparse.dia_array(([1/float(x) if x != 0 else 0 for x in A.sum(axis = 1)], [0]), A.shape)
    P = D_INV @ A

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
    neg = 0
    for player, games in items:
        #get player data
        if len(games) < 4:
            neg += 1
            continue
        
        if playerID:
            player = playerID
            games = playerinfo[playerID]
        #change player data into id index and split
        games = [allids.index(str(game)) for game in games if str(game) in allids]
        shuffled = games
        random.shuffle(shuffled)
        train = shuffled[:int(split * len(shuffled))]
        test = shuffled[int(split * len(shuffled)):]

        #label
        true = 0
        labels = label(train)
        rec: List[Tuple[float, int]] = [(lowerbound, -1)] * int(numrec)
        for j in range(len(allids)):
            if j not in train and labels[j, 0] > rec[0][0]:
                heapq.heapreplace(rec, (labels[j, 0], j))


        for score, game in rec:
            #print("score:", score, "\tgame:", allids[game])
            if game in test:
                true += 1
        
        help = 0
        helpers = [id for _, id in rec]
        #print("test")
        for game in test:
            score = labels[game, 0]
            #print("score:", score, "\tgame:", allids[game])
            if game in helpers:
                help += 1
        #get metrics and recomendations 
        
        acc = math.exp(help / (len(test) + 0.0000000000001))
        recs[player] = [allids[x[1]] for x in rec if x[1] > -1]

        #get loss
        loss += acc

        if playerID:
            print("loss:", loss)
            print("recs:", recs)
            break
    
    return loss / (numplayers - neg)

# bounds = {'khat':(0, 3.99999)}
# optimizer = BayesianOptimization(
#     f = propagation,
#     pbounds = bounds
# )

# optimizer.maximize(init_points=10, n_iter=40)
# print(optimizer.max)

propagation(playerID='76561198841140464', T=6)
