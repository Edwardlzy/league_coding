import requests

# Return the basic information of a summoner.
'''
    "profileIconId": 1667,
    "name": "BeforeUWereBorn",
    "summonerLevel": 30,
    "accountId": 228713314,
    "id": 70471081,
    "revisionDate": 1500155915000
'''
def requestSummonerData(summonerName, APIKey):
    #Here is how I make my URL.  There are many ways to create these.
    URL = "https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #requests.get is a function given to us my our import "requests". It basically goes to the URL we made and gives us back a JSON.
    response = requests.get(URL)
    return response.json()


# Return the AccountId of a summoner.
def getAccountID(summonerName, APIKey):
    URL = "https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()["accountId"]


# Return a list of matches in the following format:
'''
    "lane": "BOTTOM",
    "gameId": 2549333650,
    "champion": 498,
    "platformId": "NA1",
    "timestamp": 1500154170219,
    "queue": 2,
    "role": "DUO_CARRY",
    "season": 9
'''
def getRecentMatches(summonerName, APIKey):
    accountId = getAccountID(summonerName, APIKey)
    URL = "https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/" + str(accountId) + "/recent" + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()["matches"]


# Return the most frequently recently played champion by this summoner.
def mostPlayedChampionRecently(summonerName, APIKey):
    champ_dict = {}

    # Get the recent games.
    raw_data = getRecentMatches(summonerName, APIKey)

    for game in raw_data:
        if game["champion"] not in champ_dict:
            champ_dict[game["champion"]] = 1
        else:
            champ_dict[game["champion"]] += 1

    resultID = [champ for champ in champ_dict if champ_dict[champ] == max(champ_dict.values())]
    return champIDToName(resultID, APIKey)


# Given a list of championIds, return a list of champion names.
def champIDToName(champions, APIKey):
    names = []
    for champID in champions:
        URL = "https://na1.api.riotgames.com/lol/static-data/v3/champions/" + str(champID) + "?api_key=" + APIKey
        names.append(requests.get(URL).json()["name"])
    return names


# Return the champion that appears most frequently in the summoner's recent losing games.
def hardestChampionAgainst(summonerName, APIKey):
    champ_dict = {}
    gameIds = [(match["gameId"], match["champion"]) for match in getRecentMatches(summonerName, APIKey)]

    for game in gameIds:
        URL = "https://na1.api.riotgames.com/lol/match/v3/matches/" + str(game[0]) + "?api_key=" + APIKey
        gameData = requests.get(URL).json()
        counter = 0
        winTeam = 0
        loseTeam = 0

        for team in gameData["teams"]:
            if team["win"] == "Win":
                winTeam = team["teamId"]
            else:
                loseTeam = team["teamId"]

        # Counter meaning: 0->same champ on both sides; 1->win; -1->lose, record.
        for participant in gameData["participants"]:
            # Find all losing games.
            if participant["championId"] == game[1]:
                if participant["teamId"] == loseTeam:
                    counter -= 1
                else:
                    counter += 1

        if counter == -1:
            for participant in gameData["participants"]:
                if participant["teamId"] == winTeam:
                    if participant["championId"] not in champ_dict:
                        champ_dict[participant["championId"]] = 1
                    else:
                        champ_dict[participant["championId"]] += 1

    # for i in champ_dict:
    #     print(i, champ_dict[i])

    resultID = [champ for champ in champ_dict if champ_dict[champ] == max(champ_dict.values())]
    return champIDToName(resultID, APIKey)


# Return the basic information of an ID's ranked games.
def requestRankedData(ID, APIKey):
    URL = "https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/" + ID + "?api_key=" + APIKey
    # print (URL)
    response = requests.get(URL)
    return response.json()
    

def main():
    summonerName = (str)(input('Type your Summoner Name here and DO NOT INCLUDE ANY SPACES: '))
    APIKey = (str)(input('Copy and paste your API Key here: '))

    responseJSON  = requestSummonerData(summonerName, APIKey)
    ID = responseJSON['id']
    ID = str(ID)
    responseJSON2 = requestRankedData(ID, APIKey)
    if responseJSON2 is not None:
        print (responseJSON2[0]['tier'])
        print (responseJSON2[0]['rank'])
        print (responseJSON2[0]['leaguePoints'])
    print("Recently played", mostPlayedChampionRecently(summonerName, APIKey), "the most.")
    print("Hardest against", hardestChampionAgainst(summonerName, APIKey))


if __name__ == "__main__":
    main()

