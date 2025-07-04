from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

games = [
    {"id": 1, "name": "Valorant", "story": "Ajanların savaşı", "top_players": ["TenZ", "ScreaM"], "company": "Riot Games"},
    {"id": 2, "name": "League of Legends", "story": "Runeterra evreni", "top_players": ["Faker", "Caps"], "company": "Riot Games"}
]

@app.route('/')
def index():
    return render_template('index.html', games=games)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = next((g for g in games if g["id"] == game_id), None)
    return render_template('edit_game.html', game=game, games=games)

@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_text = request.form.get('feedback')
    print(f"Gelen geri bildirim: {feedback_text}")
    return redirect(url_for('index'))

@app.route('/gift', methods=['GET', 'POST'])
def gift():
    if request.method == 'POST':
        name = request.form.get('Eymen Yiğit Karaman')
        iban = request.form.get('TR18 0001 5001 5800 7341 5288 14')
        print(f"Hediye Gönderildi: {name} - IBAN: {iban}")
        return redirect(url_for('index'))
    return render_template('gift.html', games=games)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
