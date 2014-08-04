from pymongo import MongoClient
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import time
import json
import numpy as np

client = MongoClient()
db = client.merlin
matches = db.matches

with open('heroes.json', 'r') as f:
    result = json.load(f)['result']

heroes = result['heroes']
NUM_HEROES = heroes[-1]['id']
NUM_FEATURES = NUM_HEROES * 2
NUM_MATCHES = 100000

class Train:
    def build_data(self):
        X = np.zeros((NUM_MATCHES, NUM_FEATURES), dtype=np.int8)
        Y = np.zeros(NUM_MATCHES, dtype=np.int8)

        for i, match in enumerate(matches.find().limit(NUM_MATCHES)):
            Y[i] = 1 if match['radiant_win'] else 0

            for player in match['players']:
                player_index = player['player_slot']
                hero_index = player['hero_id'] + NUM_HEROES if player_index >= 128 else player['hero_id']
                X[i, hero_index - 1] = 1

        indices = np.random.permutation(NUM_MATCHES)

        data_x = X[indices]
        data_y = Y[indices]

        return data_x, data_y

    def build_lr_model(self, data_x_train, data_y_train, export=False):
        model = LogisticRegression().fit(data_x_train, data_y_train)
        if export:
            joblib.dump(model, 'models/lr_model.pkl', compress=9)
        return model

    def build_knn_model(self, data_x_train, data_y_train, k, export=False):
        model = KNeighborsClassifier(n_neighbors=k, weights='distance').fit(data_x_train, data_y_train)
        if export:
            joblib.dump(model, 'models/knn_model.pkl', compress=9)
        return model

if __name__ == '__main__':
    x, y = Train().build_data()
    Train().build_lr_model(x, y, True)
    Train().build_knn_model(x, y, True)
