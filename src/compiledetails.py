import json

#reformats some data into better/more usable forms
def changeinfo(info):
    #modify data into lists
    if 'categories' in info.keys():
        new_categories = []
        for category in info['categories']:
            new_categories.append(category['id'])
        info['categories'] = new_categories
  
    if 'genres' in info.keys():
        new_genres = []
        for genre in info['genres']:
            new_genres.append(genre['id'])
        info['genres'] = new_genres

    if 'platforms' in info.keys():
        new_plat = []
        for plat, val in info['platforms'].items():
            if val:
                new_plat.append(plat)
        info['platforms'] = new_plat

    #change to sole value
    if 'metacritic' in info.keys(): info['metacritic'] = info['metacritic']['score'] 
    if 'release_date' in info.keys(): info['release_date'] = info['release_data']['date'][-4:] 
    if 'achievements' in info.keys(): info['achievements'] = info['achievements']['total'] 
    if 'recommendations' in info.keys(): info['recommendations'] = info['recommendations']['total'] 
    if 'price_overview' in info.keys(): info['price_overview'] = info['price_overview']['initial']

    return info


# compile all game data into one file
allgames = {}
allids = []
for i in range(202):
  try:
    #modify games info and store info and id if possible
    gamedata = open("data/gamedata/game_data_" + str(i) + ".json")
    games = json.load(gamedata)
    gamedata.close()
    for id, info in games.items():
      if type(info) is not dict:
        continue
      allgames[id] = changeinfo(info)
      allids.append(id)
  except Exception as E:
    print(E)
    break

#dump game info
alldata = open("data/gamedata/all_gamedata.json", "w")
json.dump(allgames, alldata)
alldata.close()

#dump ids used
allidsdata = open("data/gameids/all_usable_ids.json", "w")
json.dump(allids, allidsdata)
allidsdata.close()