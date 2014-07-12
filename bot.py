from dota2py import api
from pymongo import MongoClient
import pdb
import json
import logging

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO, filename='botpy.log', format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

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
        logger.degug("Invalid data : status-%s" % data['status'])
        return False

    if data['total_results'] == 0:
        logger.debug("Cannot find any matches in data")
        return False

    return True

def filter_match_detail(match_detail):
    match_detail_filtered = { 'match_id' : match_detail['match_id'], 'radiant_win' : match_detail['radiant_win'] }
    match_detail_filtered['players'] = []

    for i, player in enumerate(match_detail['players']):
        player_detail = { 'player_slot' : player['player_slot'], 'hero_id': player['hero_id'] }
        match_detail_filtered['players'].append(player_detail)

    return match_detail_filtered

if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client.merlin
    count = 0;

    data = api.get_match_history(skill=3, min_players=10)['result']
    if data_valid(data):
        for match in data['matches']:
            match_detail = api.get_match_details(match['match_id'])['result']
            if match_valid(match_detail):
                db.matches.insert(filter_match_detail(match_detail))
                count += 1

    logger.info("Added %s new matches" % count);
    logger.info("Currently at %s matches in the database" % db.matches.count())
