from steam import Steam
import json
import requests
from decouple import config

KEY = config("STEAM_API_KEY")
steam = Steam(KEY)

#all_games = open('C:\\Users\\hispa\\Documents\\459-steam\\data\\all_games.json', encoding='utf8')
#data = json.load(all_games)
#game_list = data['applist']['apps']

#for i, game in enumerate(game_list):
#    break
#    if i % 10 == 0:
#        print(i)
#    id = game['appid']
#    try:
#        steam.apps.get_app_details(id)
#    except:
#        print("bad: " + str(i))
#        break


numList = 500
last_id_str = ""
baseURL = "https://api.steampowered.com/IStoreService/GetAppList/v1?max_results=" + str(numList) + "&key=" + KEY

i = 0
more = True
while more:
    request = requests.get(baseURL + last_id_str)
    response = request.json()
    response = response['response']
    apps = response['apps']

    f = open("data/gameids/gameids_" + str(i) + ".json", "w")
    json.dump(apps, f)
    f.close()

    print(i)
    if len(response) == 1:
        break


    i += 1
    more = response['have_more_results']
    id = response['last_appid']
    last_id_str = "&last_appid=" + str(id)


