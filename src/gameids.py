from steam import Steam
import json
import requests
from decouple import config

KEY = config("STEAM_API_KEY")
steam = Steam(KEY)

numList = 50000
last_id_str = ""
baseURL = "https://api.steampowered.com/IStoreService/GetAppList/v1?max_results=" + str(numList) + "&key=" + KEY


gameids = []
while True:
    #request steam
    request = requests.get(baseURL + last_id_str)
    response = request.json()
    response = response['response']
    apps = response['apps']
    for app in apps:
        gameids.append(app['appid'])
    
    #if there are no more ids
    if len(response) == 1:
        break

    #get info for next call
    id = response['last_appid']
    last_id_str = "&last_appid=" + str(id)

#dump data into file
f = open("data/gameids/gameids.json", "w")
json.dump(gameids, f)
f.close()

