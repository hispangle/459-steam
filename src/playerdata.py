from decouple import config
import requests
import json

KEY = config("STEAM_API_KEY")
baseURL = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"
#myID = 76561198841140464
#req = requests.get(baseURL, {"key": str(KEY), "steamid": myID, "include_appinfo": "true", "include_played_free_games": "true"})


#get discovered players
try:
    playerslist1 = open("data/playerdata/discovered_players.json")
    discoveredplayers = json.load(playerslist1)
    playerslist1.close()
except:
    discoveredplayers = []

#get analyzed players
try:
    analyzed = open("data/playerdata/analyzed_players.json")
    analyzedplayers = json.load(analyzed)
    analyzed.close()
except:
    analyzedplayers = []

#get players who have info already
try:
    indexed = open("data/playerdata/indexed_recent_players.json")
    indexedplayers = json.load(indexed)
    indexed.close()
except:
    indexedplayers = []

#get player info
try:
    info = open("data/playerdata/player_recent_info.json")
    playerinfo = json.load(info)
    info.close() 
except:
    playerinfo = {}
indexedplayers = []
players = list(set(analyzedplayers).union(set(discoveredplayers)).difference(set(indexedplayers)))
saveinterval = 1000
for i in range(len(players)):
    if i % saveinterval == 0:
        print("i:", i)
    
    id = players[i]
    req = requests.get(baseURL, {"key": str(KEY), "steamid": id, "count": 20})
    if req.ok:
        if 'games' in req.json()['response']:
            playerinfo[id] = [game['appid'] for game in req.json()['response']['games']]
        indexedplayers.append(id)
    
    if i % saveinterval == 0:
        info = open("data/playerdata/player_recent_info.json", "w")
        json.dump(playerinfo, info)
        info.close()

        indexed = open("data/playerdata/indexed__recent_players.json", "w")
        json.dump(indexedplayers, indexed)
        indexed.close()

