# P2

Ce programme permet de parcourir la librairie en ligne "book to scrape" et d'en récupérer toutes les informations demandées pour chaque livre.
Ces informations seront enregistrées en format CSV pour chaque catégorie de livres et leur couvertures seront égalemment téléchargées.

Tout d'abord, allez dans le terminal;
- sous Windows, en tapant et entrant "cmd" dans la barre de recherche
- sous Mac, en tapant et sélectionnant "terminal" dans une recherche "spotlight"

Allez ensuite dans le répertoire du projet que vous avez téléchargé en tapant son chemin:
cd /Users/"vous"/Downloads/P2

Pour vérifier que vous êtes au bon endroit dans la console entrez:
- Unix: `pwd`
- Windows: `cd`

Créez un environnement :
- Unix: `python -m venv P2.env`
- Windows: `py -m venv P2.env`

Activez l'environnement :
- Unix: `source P2.env/bin/activate`
- Windows: `P2.env\Scripts\activate`


Et installez les paquets requis avec la commande :
`pip install -r requirments.txt`

Vous pouvez maintenant lancer le programme en tapant:
- Unix: `python P2.py`
- Windows: `py P2.py`


Dès que vous aurez terminé, quittez l'environnement en entrant `deactivate`
