import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# 📁 Kalıcı veritabanı konumu (static/data)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'static', 'data', 'gameface.db')

# ⚙️ Flask ayarları
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 🔧 Veritabanı başlangıcı
db = SQLAlchemy(app)

# 🎮 MODELLER
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

# 🔐 Yardımcılar
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_app():
    os.makedirs(os.path.join(BASE_DIR, 'static', 'images'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'data'), exist_ok=True)
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            demo = [
                Game(name="Minecraft", story="Blok dünyasında hayatta kal!", best_players="Dream, Techno", company="Mojang", image_filename="minecraft.jpg"),
                Game(name="Valorant", story="Taktiksel ajan savaşı.", best_players="TenZ, ScreaM", company="Riot Games", image_filename="valorant.jpg")
            ]
            db.session.bulk_save_objects(demo)
            db.session.commit()

# 🔓 Sayfalar
@app.route('/')
def index():
    game_id = request.args.get('game_id', type=int)
    games = Game.query.order_by(Game.name).all()
    game = Game.query.get(game_id) if game_id else None
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('index.html', games=games, game=game, feedbacks=feedbacks)

# 🛠️ İşlemler
@app.route('/add_game', methods=['POST'])
def add_game():
    try:
        name = request.form.get('name', '').strip()
        story = request.form.get('story', '').strip()
        best_players = request.form.get('best_players', '').strip()
        company = request.form.get('company', '').strip()
        file = request.files.get('image_file')

        if not name or not file or not allowed_file(file.filename):
            flash("Geçerli bilgi ve resim girilmeli.", "error")
            return redirect(url_for('index'))

        if Game.query.filter_by(name=name).first():
            flash("Bu isimde bir oyun zaten var.", "error")
            return redirect(url_for('index'))

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_game = Game(name=name, story=story, best_players=best_players, company=company, image_filename=filename)
        db.session.add(new_game)
        db.session.commit()
        flash("Oyun başarıyla eklendi!", "success")
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    msg = request.form.get('message', '').strip()
    if msg:
        db.session.add(Feedback(message=msg))
        db.session.commit()
        flash("Geri bildirim alındı!", "success")
    else:
        flash("Geri bildirim boş olamaz.", "error")
    return redirect(url_for('index'))

# 🛡️ Genel hata yakalama
@app.errorhandler(Exception)
def handle_all_errors(error):
    return f"<h3>Beklenmedik hata oluştu: {str(error)}</h3>", 500

# 🚀 Başlat
if __name__ == '__main__':
    init_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)