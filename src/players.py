# http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&steamid=76561198841140464&relationship=friend
import json
from decouple import config
import requests
import time

KEY = config("STEAM_API_KEY")
baseURL = "http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"

set1 = {1, 2, 3}
set2 = {3, 4, 5}

print(set2 - set1)

try:
    playerslist1 = open("data/playerids/discovered_players.json")
    discoveredplayers = json.load(playerslist1)
    playerslist1.close()
except:
    discoveredplayers = [76561198841140464]


try:
    analyzed = open("data/playerids/analyzed_players.json")
    analyzedplayers = json.load(analyzed)
    analyzed.close()
except:
    analyzedplayers = []

i = 0
save_freq = 100
num_needed = 10000
while len(discoveredplayers) != 0:
    if i % save_freq == -1 % save_freq:
        print("dump")
        discovered = open("data/playerids/discovered_players.json", "w")
        json.dump(discoveredplayers, discovered)
        discovered.close()

        analyzed = open("data/playerids/analyzed_players.json", "w")
        json.dump(analyzedplayers, analyzed)
        analyzed.close()
        print(i)
    i += 1
    player = discoveredplayers.pop()
    analyzedplayers.append(player)
    try:
        request = requests.get(baseURL, {'key': str(KEY), 'steamid': player, 'relationship': 'friend'})
        if not request.ok: raise Exception(request.reason)
        friends = request.json()['friendslist']['friends']
    except Exception as E:
        print(E)
        if str(E) != "Unauthorized":
            break
        continue
    for friend in friends:
        steamid = int(friend['steamid'])
        if steamid not in analyzedplayers and steamid not in discoveredplayers:
            discoveredplayers.append(int(steamid))
    if i == num_needed:
        break


discovered = open("data/playerids/discovered_players.json", "w")
json.dump(discoveredplayers, discovered)
discovered.close()

analyzed = open("data/playerids/analyzed_players.json", "w")
json.dump(analyzedplayers, analyzed)
analyzed.close()