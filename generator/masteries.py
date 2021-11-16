from typing import Dict, List, Tuple
import requests
import csv
import time
import json
import argparse

API_KEY = ''
BASE_URL = ''

def getNames(file : str) -> List[str]:

    names = []
    with open('names.txt', 'r') as file:
        names = [line.strip() for line in file]
    return names

def makeGET(url : str, arg : str) -> Dict:

    request = f'{BASE_URL}/{url}/{arg}?api_key={API_KEY}'
    resp = requests.get(request)

    if (resp.status_code == 200):

        return resp.json()

    else:
        raise requests.HTTPError(resp.content, request)

def getMasteries(name : str) -> Dict[int, Tuple[int, int]]:

    try:

        summoner_data = makeGET('lol/summoner/v4/summoners/by-name', name)
        id = summoner_data['id']
        time.sleep(0.5)
        masteries_data = makeGET('lol/champion-mastery/v4/champion-masteries/by-summoner', id)
        output = {int(entry["championId"]) : [entry["championPoints"], entry["championLevel"]] for entry in masteries_data}
        return output

    except requests.HTTPError as e:

        print(f'Error getting info for {name}.')
        print(f'url={e.args[1]}')
        print(e.args[0])

def getChampionNames() -> List[Tuple[int, str]]:

    with open('champion.json', 'r', encoding="utf8") as json_file:

        champions = json.load(json_file)
        data = [(int(champion["key"]), champion["name"]) for _, champion in champions["data"].items()]
        return data

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Generate masteries for some people")
    parser.add_argument('region', type=str,
                    help='The region to gather the data from.')
    parser.add_argument('key', type=str,
                    help='The Riot API key to use.')

    args = parser.parse_args()

    REGION = args.region
    API_KEY = args.key

    BASE_URL = f'https://{REGION}.api.riotgames.com'

    names_with_scores = {}
    championNames = getChampionNames()

    names = getNames('names.txt')
    for i, name in enumerate(names):
        result = getMasteries(name)
        names_with_scores[name] = result
        print(f'Got {name}. {i}/{len(names)} remaining.')
        time.sleep(1)

    with open('output.csv', 'w', newline='') as csv_file:

        writer = csv.writer(csv_file)
        writer.writerow(("Champion Name", "Name", "Score", "Mastery Rank", "Average Score"))

        for i, (id, name) in enumerate(championNames, 1):

            results = {}
            average = 0
            num = 0
            for username, scores in names_with_scores.items():
                if id in scores:
                    results[username] = scores[id][0]
                    average += scores[id][0]
                    num += 1

            average /= num
            average = round(average)

            if results:
                highest = max(results, key=results.get)
                writer.writerow((name, highest, results[highest], names_with_scores[highest][id][1], average))
            else:
                writer.writerow((name, "-", "-", "-", "-"))

            print(f'Done {name}. {i}/{len(championNames)} remaining.')