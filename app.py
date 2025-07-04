import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
DB_PATH    = os.path.join(BASE_DIR, 'gameface.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED    = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']           = UPLOAD_DIR

# Donation
app.config['DONATION_NAME'] = 'Eymen Yiğit Karaman'
app.config['DONATION_IBAN'] = 'TR18 0001 5001 5800 7341 5288 14'

db = SQLAlchemy(app)

class Game(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), unique=True, nullable=False)
    story          = db.Column(db.Text)
    best_players   = db.Column(db.Text)
    company        = db.Column(db.String(100))
    image_filename = db.Column(db.String(100), default='default.png')

class Feedback(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED

@app.before_first_request
def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        db.create_all()
        # Demo oyunlar
        for i in range(1, 6):
            db.session.add(Game(
                name=f"Game{i}", 
                story=f"Demo hikâye #{i}", 
                best_players=f"Player{i}A, Player{i}B", 
                company=f"Company {i}"
            ))
        db.session.commit()

@app.route('/')
def index():
    search    = request.args.get('search','').strip()
    game_id   = request.args.get('game_id', type=int)
    base_q    = Game.query.order_by(Game.name)
    games     = base_q.filter(Game.name.ilike(f"%{search}%")).all() if search else base_q.all()
    selected  = Game.query.get(game_id) if game_id else None
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('index.html', games=games, game=selected,
                           feedbacks=feedbacks, search=search)

@app.route('/add_game', methods=['POST'])
def add_game():
    name   = request.form['name'].strip()
    story  = request.form.get('story','').strip()
    bp     = request.form.get('best_players','').strip()
    comp   = request.form.get('company','').strip()
    file   = request.files.get('image_file')
    if not name:
        flash("Oyun adı zorunlu.","error")
        return redirect(url_for('index'))
    if file and not allowed_file(file.filename):
        flash("Geçersiz resim formatı.","error")
        return redirect(url_for('index'))
    if Game.query.filter_by(name=name).first():
        flash("Bu isimde oyun mevcut.","error")
        return redirect(url_for('index'))
    filename = 'default.png'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_DIR, filename))
    game = Game(name=name, story=story, best_players=bp, company=comp, image_filename=filename)
    db.session.add(game); db.session.commit()
    flash("Oyun eklendi.","success")
    return redirect(url_for('index', game_id=game.id))

@app.route('/edit_game/<int:game_id>', methods=['GET','POST'])
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        game.name         = request.form['name'].strip()
        game.story        = request.form.get('story','').strip()
        game.best_players = request.form.get('best_players','').strip()
        game.company      = request.form.get('company','').strip()
        file = request.files.get('image_file')
        if file and allowed_file(file.filename):
            fn = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, fn))
            game.image_filename = fn
        db.session.commit()
        flash("Oyun güncellendi.","success")
        return redirect(url_for('index', game_id=game.id))
    return render_template('edit_game.html', game=game)

@app.route('/delete_game/<int:game_id>')
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game); db.session.commit()
    flash(f"“{game.name}” silindi.","success")
    return redirect(url_for('index'))

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    msg = request.form['message'].strip()
    if msg:
        db.session.add(Feedback(message=msg)); db.session.commit()
        flash("Geri bildirim kaydedildi.","success")
    else:
        flash("Mesaj boş olamaz.","error")
    return redirect(url_for('index'))

@app.route('/gift')
def gift():
    return render_template('gift.html')

@app.errorhandler(500)
def internal_error(e):
    return f"<h3>Sunucu Hatası</h3><pre>{e}</pre>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
