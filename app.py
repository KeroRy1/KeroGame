from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameface.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# MODELLER
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    story = db.Column(db.Text)
    best_players = db.Column(db.Text)
    company = db.Column(db.String(100))
    image_filename = db.Column(db.String(100))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

# Yardımcı fonksiyon
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        db.create_all()
        if Game.query.count() == 0:
            demo_games = [
                Game(name="Minecraft", story="Minecraft, bloklardan oluşan bir dünyada hayatta kalma oyunudur.",
                     best_players="Dream, Technoblade", company="Mojang", image_filename="minecraft.jpg"),
                Game(name="Valorant", story="Valorant, ajanlarla oynanan taktiksel FPS oyunudur.",
                     best_players="TenZ, ScreaM", company="Riot Games", image_filename="valorant.jpg"),
                Game(name="Rocket League", story="Arabalarla futbol oynanan rekabetçi bir oyundur.",
                     best_players="Turbopolsa, GarrettG", company="Psyonix", image_filename="rocketleague.jpg")
            ]
            db.session.bulk_save_objects(demo_games)
            db.session.commit()

@app.route('/')
def index():
    game_id = request.args.get('game_id', type=int)
    games = Game.query.order_by(Game.name).all()
    game = Game.query.get(game_id) if game_id else None
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('index.html', games=games, game=game, feedbacks=feedbacks)

@app.route('/add_game', methods=['POST'])
def add_game():
    name = request.form.get('name', '').strip()
    story = request.form.get('story', '').strip()
    best_players = request.form.get('best_players', '').strip()
    company = request.form.get('company', '').strip()
    file = request.files.get('image_file')

    if not name or not file or not allowed_file(file.filename):
        flash("Lütfen geçerli bilgiler girin ve resim seçin.", "error")
        return redirect(url_for('index'))

    if Game.query.filter_by(name=name).first():
        flash("Bu isimde bir oyun zaten var.", "error")
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    game = Game(name=name, story=story, best_players=best_players, company=company, image_filename=filename)
    db.session.add(game)
    db.session.commit()
    flash("Oyun eklendi.", "success")
    return redirect(url_for('index'))

@app.route('/edit_game', methods=['POST'])
def edit_game():
    old_name = request.form.get('old_name', '').strip()
    game = Game.query.filter_by(name=old_name).first()
    if not game:
        flash("Oyun bulunamadı.", "error")
        return redirect(url_for('index'))

    game.name = request.form.get('name', game.name).strip()
    game.story = request.form.get('story', game.story).strip()
    game.best_players = request.form.get('best_players', game.best_players).strip()
    game.company = request.form.get('company', game.company).strip()
    db.session.commit()
    flash("Oyun güncellendi.", "success")
    return redirect(url_for('index', game_id=game.id))

@app.route('/delete_game', methods=['POST'])
def delete_game():
    name = request.form.get('name', '').strip()
    game = Game.query.filter_by(name=name).first()
    if not game:
        flash("Silinecek oyun bulunamadı.", "error")
        return redirect(url_for('index'))

    db.session.delete(game)
    db.session.commit()
    flash("Oyun silindi.", "success")
    return redirect(url_for('index'))

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    message = request.form.get('message', '').strip()
    if not message:
        flash("Geri bildirim boş olamaz.", "error")
        return redirect(url_for('index'))

    feedback = Feedback(message=message)
    db.session.add(feedback)
    db.session.commit()
    flash("Teşekkürler!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_database()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
