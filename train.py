from pymongo import MongoClient
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from progressbar import *
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
NUM_MATCHES = matches.count()

def build_data():
    X = np.zeros((NUM_MATCHES, NUM_FEATURES), dtype=np.int8)
    Y = np.zeros(NUM_MATCHES, dtype=np.int8)

    widgets = ['Progress: ', Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA()]
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

    return data_x_train, data_y_train, data_x_test, data_y_test

def build_lr_model(data_x_train, data_y_train, data_x_test, data_y_test):
    start_time = time.time()
    model = LogisticRegression().fit(data_x_train, data_y_train)
    joblib.dump(model, 'models/lr_model.pkl', compress=9)
    print "LogisticRegression - Elapsed time : %.3f seconds - Variance: %s" % (time.time() - start_time, model.score(data_x_test, data_y_test))

def build_knn_model(data_x_train, data_y_train, data_x_test, data_y_test):
    start_time = time.time()
    model = KNeighborsClassifier().fit(data_x_train, data_y_train)
    joblib.dump(model, 'models/knn_model.pkl', compress=9)
    print "KNeighborsClassifier - Elapsed time : %.3f seconds - Variance: %s" % (time.time() - start_time, model.score(data_x_test, data_y_test))

def build_svm_model(data_x_train, data_y_train, data_x_test, data_y_test):
    start_time = time.time()
    model = SVC(kernel='linear').fit(data_x_train, data_y_train)
    joblib.dump(model, 'models/svc_model.pkl', compress=9)
    print "SupportVectorClassification - Elapsed time : %.3f seconds - Variance: %s" % (time.time() - start_time, model.score(data_x_test, data_y_test))

if __name__ == '__main__':
    data = build_data()
    build_lr_model(*data)
    build_knn_model(*data)
    build_svm_model(*data)
