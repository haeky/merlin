from sklearn.externals import joblib
import numpy as np
import json

with open('heroes.json', 'r') as f:
    result = json.load(f)['result']

heroes = result['heroes']
NUM_HEROES = heroes[-1]['id']
NUM_FEATURES = NUM_HEROES * 2

hero_ids = set(hero['id'] for hero in heroes)
missing_ids = list(set(range(1, NUM_HEROES + 1)) - hero_ids)

class Merlin:
    def __init__(self):
        self.model = joblib.load('models/lr_model.pkl')

    def to_hero_localized_name(self, hero_id):
        for hero in heroes:
            if hero['id'] == hero_id:
                return hero['localized_name']

    def build_query(self, my_team, enemy_team):
        query = np.zeros(NUM_FEATURES, dtype=np.int8)
        for i in my_team:
            query[i - 1] = 1
        for i in enemy_team:
            query[i + NUM_HEROES - 1] = 1
        return query

    def probability(self, my_team, enemy_team):
        query = self.build_query(my_team, enemy_team)
        radiant_prob = self.model.predict_proba(query)[0][1]

        query = self.build_query(enemy_team, my_team)
        dire_prob = self.model.predict_proba(query)[0][0]
        return (dire_prob + radiant_prob) / 2

    def recommend(self, my_team, enemy_team):
        available_heroes = [(i, my_team + [i]) for i in hero_ids if i not in my_team and i not in enemy_team and i not in missing_ids]

        recommendation = []
        for hero_id, team in available_heroes:
            probability = self.probability(team, enemy_team)
            recommendation.append((probability, self.to_hero_localized_name(hero_id)))

        return sorted(recommendation, reverse=True)[0:5-len(my_team)]

