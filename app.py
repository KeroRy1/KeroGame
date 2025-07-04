from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

games = [
    {"id": 1, "name": "Valorant", "story": "Ajanların savaşı", "top_players": ["TenZ", "ScreaM"], "company": "Riot Games"},
    {"id": 2, "name": "League of Legends", "story": "Runeterra evreni", "top_players": ["Faker", "Caps"], "company": "Riot Games"}
]

feedbacks = []

@app.route('/')
def index():
    return render_template('index.html', games=games, feedbacks=feedbacks)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = next((g for g in games if g["id"] == game_id), None)
    if not game:
        return "Oyun bulunamadı", 404
    return render_template('edit_game.html', game=game, games=games, feedbacks=feedbacks)
    
@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        new_id = max([g["id"] for g in games]) + 1 if games else 1
        games.append({
            "id": new_id,
            "name": request.form["name"],
            "story": request.form["story"],
            "top_players": request.form["top_players"].split(","),
            "company": request.form["company"]
        })
        return redirect(url_for('index'))
    return render_template('add_game.html', games=games, feedbacks=feedbacks)

@app.route('/edit/<int:game_id>', methods=['POST'])
def edit_game(game_id):
    for game in games:
        if game["id"] == game_id:
            game["name"] = request.form["name"]
            game["story"] = request.form["story"]
            game["top_players"] = request.form["top_players"].split(",")
            game["company"] = request.form["company"]
            break
    return redirect(url_for('index'))

@app.route('/delete/<int:game_id>', methods=['GET', 'POST'])
def delete_game(game_id):
    global games
    game = next((g for g in games if g["id"] == game_id), None)
    if request.method == 'POST':
        games = [g for g in games if g["id"] != game_id]
        return redirect(url_for('index'))
    return render_template('delete_game.html', game=game, games=games, feedbacks=feedbacks)

@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_text = request.form.get('feedback')
    if feedback_text:
        feedbacks.append(feedback_text)
    return redirect(url_for('index'))

@app.route('/gift')
def gift():
    return render_template('gift.html', games=games, feedbacks=feedbacks)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
