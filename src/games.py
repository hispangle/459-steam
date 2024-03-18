from steam import Steam
import json
import time
import requests
from decouple import config

KEY = config("STEAM_API_KEY")
steam = Steam(KEY)

filters = "fullgame,developers,demos,price_overview,metacritic,categories,controller_support,genres,recommendations,achievements"

ids = []
id = 0
failedids = []
try:
    for i in range(201):
        detailed_games = {}
        f = open("data/gameids_" + str(i) + ".json")
        games = json.load(f)
        for j, game in enumerate(games):
            if j % 100 == 1:
                print(j)
            id = game['appid']
            ids.append(id)
            times = 0
            while times < 2:
                data = steam.apps.get_app_details(id, filters = filters)
                if data:
                    break
                else:
                    print(id)
                    times += 1
                    time.sleep(60.1)
            if data is None:
                failedids.append(id)
                continue
            data = data[str(id)]
            if data['success']:
                detailed_games[id] = data['data']
        w = open("data/game_data_" + str(i) + ".json", "w")
        json.dump(detailed_games, w)
        time.sleep(120)
except Exception as E:
    print(E)
    print(id)

ids_file = open("data/allids.json", "w")
json.dump(ids, ids_file)

ids_file = open("data/failedids.json", "w")
json.dump(failedids, ids_file)

print(len(ids))






BASE_DETAILS = "https://store.steampowered.com/api/appdetails"

