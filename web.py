from flask import *
from sklearn.externals import joblib
from merlin import Merlin
import json
app = Flask(__name__)

@app.route("/")
def index():
    heroes = Merlin().get_heroes_localized_name()
    return render_template('index.html', data=json.dumps(heroes))

@app.route("/recommend", methods=['POST'])
def recommend():
    dire_team = Merlin().from_heroes_localized_name_to_ids(json.loads(request.form['dire_team']))
    radiant_team = Merlin().from_heroes_localized_name_to_ids(json.loads(request.form['radiant_team']))

    if request.form['model_name'] == 'lr':
        model = joblib.load('models/lr_model.pkl')
    else:
        model = joblib.load('models/knn_model.pkl')

    heroes = [hero[1] for hero in Merlin().recommend(model, dire_team, radiant_team)]
    return render_template('recommend.html', heroes=heroes)

if __name__ == "__main__":
    app.run(debug=True)
