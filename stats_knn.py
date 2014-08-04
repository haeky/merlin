from pymongo import MongoClient
from progressbar import *
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np
import json
from train import Train
from merlin import Merlin

client = MongoClient()
db = client.merlin
matches = db.matches

with open('heroes.json', 'r') as f:
    result = json.load(f)['result']

heroes = result['heroes']
NUM_HEROES = heroes[-1]['id']
NUM_FEATURES = NUM_HEROES * 2
NUM_MATCHES = 100000
NUM_POINTS = 20

class Stats:
    def find_k(self):
        with plt.xkcd():
            widgets = ['Progress: ', Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=6)
            pbar.start()

            x, y = Train().build_data()

            x_axis = range(5, 30, 5)
            y_axis = []
            for i, k in enumerate(x_axis):
                pbar.update(i)

                x_train = x[NUM_MATCHES/10:]
                y_train = y[NUM_MATCHES/10:]
                x_test = x[:NUM_MATCHES/10]
                y_test = y[:NUM_MATCHES/10]

                model = Train().build_knn_model(x_train, y_train, k)
                accuracy = self.evaluate(model, x_test, y_test)
                y_axis.append(accuracy)

            plt.plot(x_axis, y_axis)
            plt.ylabel('Precision')
            plt.xlabel('K')
            plt.title('Validation croisee')
            plt.savefig("k_cross_validation.png")

    def build_stats(self):
        with plt.xkcd():
            y_axis_lr = []

            INTERVAL = NUM_MATCHES / NUM_POINTS
            x_axis = range(INTERVAL, NUM_MATCHES, INTERVAL)

            widgets = ['Progress: ', Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=(NUM_MATCHES/INTERVAL))
            pbar.start()

            x, y = Train().build_data()

            for i, size in enumerate(x_axis):
                pbar.update(i)

                x_train = x[size/10:]
                y_train = y[size/10:]
                x_test = x[:size/10]
                y_test = y[:size/10]

                model = Train().build_knn_model(x_train, y_train, 15)
                accuracy = self.evaluate(model, x_test, y_test)
                y_axis_lr.append(accuracy)

            plt.plot(x_axis, y_axis_lr)
            plt.ylabel('Precision')
            plt.xlabel('Grandeur')
            plt.title('K plus proche voisin')
            plt.savefig("knn_accuracy.png")

    def evaluate(self, model, x_data, y_data):
        n = 0.0

        for index, heroes in enumerate(x_data):
            radiant_team = [i for i, x in enumerate(heroes[:NUM_HEROES-1]) if x == 1]
            dire_team = [i for i, x in enumerate(heroes[NUM_HEROES-1:]) if x == 1]
            probability = Merlin().probability(model, radiant_team, dire_team)
            prediction = 1 if probability > 0.5 else 0

            if prediction == y_data[index]:
                n += 1

        return n / len(x_data)

if __name__ == '__main__':
    Stats().build_stats()

