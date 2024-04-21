from scipy import sparse
import json
import random
from bayes_opt import BayesianOptimization

#Training params
split = 0.8
numwanted = 30
numplayers = 1000

#ML params
cutoff = 0.25
k = 100 #(k determined by graph)


totalplayers = 100000

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
def propagation(cutoff, acc_vs_rec_penalty, T = 30):
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

        #change player data into id index and split
        games = [allids.index(str(game)) for game in games if str(game) in allids]
        latest = games[-3:]
        shuffled = games[:-3]
        random.shuffle(shuffled)
        train = shuffled[:int(split * len(shuffled))]
        test = shuffled[int(split * len(shuffled)):]
        test.extend(latest)

        #label
        rec = []
        true = 0
        labels = label(train)
        for j in range(len(allids)):
            if labels[j, 0] > cutoff and j not in train:
                rec.append(j)
            if labels[j, 0] > cutoff and j in test:
                true += 1

        #get metrics and recomendations 
        acc = true / float(len(test))
        recs[player] = [allids[x] for x in rec]
        numrecs = len(rec)
        recpenalty = min(numwanted - numrecs, 0) / float(numwanted) + numwanted/float(numrecs + 0.1)

        #get loss
        loss += acc * acc_vs_rec_penalty + recpenalty
    return loss

bounds = {'cutoff': (0, 1), 'acc_vs_rec_penalty': (0.1, 10)}
optimizer = BayesianOptimization(
    f = propagation,
    pbounds = bounds
)

optimizer.maximize()
print(optimizer.max)
