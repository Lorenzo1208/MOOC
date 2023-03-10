# Charger le modèle
from pycaret.classification import *
model = load_model('ada_model copy')

# Générer un graphique de caractéristiques
interpret_model(model, plot='feature')
#