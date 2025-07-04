import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'gameface.db')

app = Flask(__name__)
app.config['SECRET_KEY']               = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI']  = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Hediye Gönder Sayfası için ayarlanabilir bilgiler
app.config['DONATION_NAME'] = 'Eymen Yiğit Karaman'
app.config['DONATION_IBAN'] = 'TR18 0001 5001 5800 7341 5288 14'

db = SQLAlchemy(app)

class Game(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), unique=True, nullable=False)
    story        = db.Column(db.Text, nullable=True)
    best_players = db.Column(db.Text, nullable=True)
    company      = db.Column(db.String(100), nullable=True)

def init_db():
    if not os.path.exists(DB_PATH):
        db.create_all()
        # Demo oyun verisi
        for i in range(1, 11):
            db.session.add(Game(
                name=f"Game {i}",
                story=f"Bu, Game {i} için örnek hikâye.",
                best_players=f"Player{i}A, Player{i}B",
                company=f"Company {i}"
            ))
        db.session.commit()

with app.app_context():
    init_db()

@app.route('/')
def index():
    search   = request.args.get('search', '').strip()
    gid      = request.args.get('game_id', type=int)
    base_q   = Game.query.order_by(Game.name)
    games    = base_q.filter(Game.name.ilike(f"%{search}%")).all() if search else base_q.all()
    selected = Game.query.get(gid) if gid else None
    return render_template('index.html',
                           games=games,
                           game=selected,
                           search=search)

@app.route('/gift')
def gift():
    # IBAN & İsim app.config üzerinden çekiliyor
    return render_template('gift.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
