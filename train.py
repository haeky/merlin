from pymongo import MongoClient
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from progressbar import *
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
NUM_MATCHES = matches.count()

X = np.zeros((NUM_MATCHES, NUM_FEATURES), dtype=np.int8)
Y = np.zeros(NUM_MATCHES, dtype=np.int8)

widgets = ['Progress: ', Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
pbar = ProgressBar(widgets=widgets, maxval=NUM_MATCHES)
pbar.start()

for i, match in enumerate(matches.find()):
    Y[i] = 1 if match['radiant_win'] else 0
    pbar.update(i)
    for player in match['players']:
        player_index = player['player_slot']
        hero_index = player['hero_id'] + NUM_HEROES if player_index >= 128 else player['hero_id']
        X[i, hero_index - 1] = 1

pbar.finish()

indices = np.random.permutation(NUM_MATCHES)
test_indices = indices[0:NUM_MATCHES/4]
train_indices = indices[NUM_MATCHES/4:NUM_MATCHES]

data_x_test = X[test_indices]
data_y_test = Y[test_indices]

data_x_train = X[train_indices]
data_y_train = Y[train_indices]

model = LogisticRegression().fit(data_x_train, data_y_train)
print "Variance: %s" % model.score(data_x_test, data_y_test)

joblib.dump(model, 'merlin.pkl', compress=9)

