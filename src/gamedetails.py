import json
import time
import requests
from decouple import config

BASE_DETAILS = "https://store.steampowered.com/api/appdetails"
filters = "supported_languages,developers,price_overview,metacritic,categories,controller_support,genres,recommendations,achievements"

last_id = open("data/gameids/last_index.json")
latest = json.load(last_id)
last_id.close()


for i in range(latest + 1, 201):
    print(i)
    failedids = []
    detailed_games = {}
    f = open("data/gameids/gameids_" + str(i) + ".json")
    games = json.load(f)    
    for j, game in enumerate(games):
        if j % 10 == 1:
            time.sleep(1)
            print(j)

        id = game['appid']
        request = requests.get(BASE_DETAILS, {"appids": str(id), "filters": filters})
        if request.ok and request.json()[str(id)]['success']:
            detailed_games[id] = request.json()[str(id)]['data']
        else:
            print(request.reason)
            failedids.append(id)
        time.sleep(2)
        

    w = open("data/gamedata/game_data_" + str(i) + ".json", "w")
    json.dump(detailed_games, w)
    w.close()
    
    last = open("data/gameids/last_index.json", "w")
    json.dump(i, last)
    last.close()
    
    failed = open("data/gameids/failed_ids_" + str(i) + ".json", "w")
    json.dump(failedids, failed)
    failed.close()
        

