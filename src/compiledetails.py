import json
import time
import math
import requests
from currency_converter import CurrencyConverter

BASE_DETAILS = "https://store.steampowered.com/api/appdetails"
filters = "supported_languages,developers,price_overview,metacritic,categories,controller_support,genres,recommendations,achievements,release_date,platforms,publishers"
c = CurrencyConverter()

#reformats some data into better/more usable forms
def changedata(data: dict) -> dict:
    #modify data into lists
    if 'categories' in data.keys():
        new_categories = []
        for category in data['categories']:
            new_categories.append(category['id'])
        data['categories'] = new_categories
  
    if 'genres' in data.keys():
        new_genres = []
        for genre in data['genres']:
            new_genres.append(genre['id'])
        data['genres'] = new_genres

    if 'platforms' in data.keys():
        new_plat = []
        for plat, val in data['platforms'].items():
            if val:
                new_plat.append(plat)
        data['platforms'] = new_plat

    #change to sole value
    if 'metacritic' in data.keys(): data['metacritic'] = data['metacritic']['score'] 
    if 'release_date' in data.keys(): data['release_date'] = data['release_date']['date'][-4:] 
    if 'achievements' in data.keys(): data['achievements'] = data['achievements']['total'] 
    if 'recommendations' in data.keys(): data['recommendations'] = data['recommendations']['total']
    if 'price_overview' in data.keys():
        if data['price_overview']['currency'] in c.currencies: 
            data['price_overview'] = c.convert(data['price_overview']['initial'], data['price_overview']['currency'], new_currency="USD") 
        else: 
            del data['price_overview']

    return data

try:
    last_index = open("data/gamedata/last_index.json")
    index = json.load(last_index)
    last_index.close()
except:
    index = 0

gameidsdata = open("data/gameids/gameids.json")
gameids = json.load(gameidsdata)
gameidsdata.close()

latest = index * 1000
for i in range(latest, len(gameids)):
    if i % 1000 == 0:
        gamesinfo = []
        print(index)
    id = gameids[i]
    try:
        request = requests.get(BASE_DETAILS, {"appids": str(id), "filters": filters})
        if not request.ok: raise Exception(request.reason)
        gamedata = request.json()[str(id)]['data']
        if type(gamedata) is not dict: raise Exception("data not dict")
        gamesinfo.append(changedata(gamedata))
    except Exception as E:
        print(E)
    
    if i % 1000 == -1 % 1000:
        data = open("data/gamedata/chunks/gamedata_" + str(index) + ".json", "w")
        json.dump(gamesinfo, data)
        data.close()

        last_index = open("data/gamedata/last_index.json", "w")
        latest = json.dump(index, last_index)
        last_index.close()
        index += 1
    time.sleep(1.5)

data = open("data/gamedata/chunks/gamedata_" + str(index) + ".json", "w")
json.dump(gamesinfo, data)
data.close()


allgames = {}
allids = []
for i in range(math.ceil(len(gameids) / 1000)):
    gamesdata = open("data/gamedata/chunks/gamedata_" + str(index) + ".json")
    games = json.load(gamesdata)
    gamesdata.close()
    allgames.update(games)
    for id in games.keys():
        allids.append(id)

allgamedata = open("data/gamedata/allgamedata.json", "w")
json.dump(allgames, allgamedata)
allgamedata.close()

allidsdata = open("data/gamedata/allidsdata.json", "w")
json.dump(allids, allidsdata)
allidsdata.close()