from dota2py import api
from pymongo import MongoClient
import pdb
import json

class GameModes:
    UNKNOWN, ALL_PICK, CAPTAINS_MODE, RANDOM_DRAFT, SINGLE_DRAFT, ALL_RANDOM, DEATH, DIRETIDE, REVERSE, GREEVILING, TUTORIAL, MID_ONLY, LEAST_PLAYED, NEW_PLAYER, COMPENDIUM, CUSTOM, CAPTAINS_DRAFT, BALANCED_DRAFT, ABILITY_DRAFT = range(19)

def match_valid(match_detail):
    for player in match_detail['players']:
        if player['leaver_status'] != 0:
            return False

    if match_detail['game_mode'] not in [GameModes.ALL_PICK, GameModes.SINGLE_DRAFT, GameModes.RANDOM_DRAFT, GameModes.CAPTAINS_MODE, GameModes.CAPTAINS_DRAFT]:
        return False

    return True

def data_valid(match):
    if data['status'] != 1:
        print "Error - Status : %s" % data['status']
        return False

    if data['total_results'] == 0:
        print "Error - No values"
        return False

    return True

if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client.merlin
    count = 0;

    data = api.get_match_history(skill=3, min_players=10)['result']
    if data_valid(data):
        for match in data['matches']:
            match_detail = api.get_match_details(match['match_id'])['result']
            if match_valid(match_detail):
                db.matches.insert(match)
                count += 1




