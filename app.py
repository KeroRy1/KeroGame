import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
DB_DIR     = os.path.join(BASE_DIR, 'static', 'data')
DB_PATH    = os.path.join(DB_DIR, 'gameface.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED    = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']           = UPLOAD_DIR

# Statik IBAN & İsim
app.config['DONATION_IBAN'] = os.environ.get('DONATION_IBAN',
    'TR76 1234 5678 9012 3456 7890 12')
app.config['DONATION_NAME'] = os.environ.get('DONATION_NAME',
    'Kerem Yılmaz')

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

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED

def init_app():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            demos = []
            for i in range(1, 101):
                demos.append(Game(
                    name=f"Game {i}",
                    story=f"Rastgele oluşturulmuş hikâye #{i}.",
                    best_players=f"Player{i}A, Player{i}B",
                    company=f"Company {i}"
                ))
            db.session.bulk_save_objects(demos)
            db.session.commit()

@app.route('/')
def index():
    search   = request.args.get('search','').strip()
    game_id  = request.args.get('game_id', type=int)
    base_q   = Game.query.order_by(Game.name)
    games    = base_q.filter(Game.name.ilike(f'%{search}%')).all() if search else base_q.all()
    game     = Game.query.get(game_id) if game_id else None
    feedbacks= Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('index.html',
        games=games, game=game, feedbacks=feedbacks, search=search
    )

@app.route('/add_game', methods=['POST'])
def add_game():
    name   = request.form['name'].strip()
    story  = request.form.get('story','').strip()
    bp     = request.form.get('best_players','').strip()
    comp   = request.form.get('company','').strip()
    file   = request.files.get('image_file')
    if not name or (file and not allowed_file(file.filename)):
        flash("Geçerli isim ve resim girilmeli.","error")
        return redirect(url_for('index'))
    if Game.query.filter_by(name=name).first():
        flash("Bu isimde oyun zaten var.","error")
        return redirect(url_for('index'))
    filename = 'default.png'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_DIR, filename))
    new = Game(name=name, story=story,
               best_players=bp, company=comp,
               image_filename=filename)
    db.session.add(new)
    db.session.commit()
    flash("Oyun eklendi.","success")
    return redirect(url_for('index', game_id=new.id))

@app.route('/edit_game/<int:game_id>', methods=['GET','POST'])
def edit_game(game_id):
    g = Game.query.get_or_404(game_id)
    if request.method=='POST':
        g.name         = request.form['name'].strip()
        g.story        = request.form.get('story','').strip()
        g.best_players = request.form.get('best_players','').strip()
        g.company      = request.form.get('company','').strip()
        file = request.files.get('image_file')
        if file and allowed_file(file.filename):
            fn = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, fn))
            g.image_filename = fn
        db.session.commit()
        flash("Oyun güncellendi.","success")
        return redirect(url_for('index', game_id=g.id))
    return render_template('edit_game.html', game=g)

@app.route('/delete_game/<int:game_id>')
def delete_game(game_id):
    g = Game.query.get_or_404(game_id)
    db.session.delete(g)
    db.session.commit()
    flash(f"{g.name} silindi.","success")
    return redirect(url_for('index'))

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    msg = request.form['message'].strip()
    if msg:
        db.session.add(Feedback(message=msg))
        db.session.commit()
        flash("Geri bildirim alındı.","success")
    else:
        flash("Mesaj boş olamaz.","error")
    return redirect(url_for('index'))

@app.route('/gift')
def gift():
    return render_template('gift.html')

@app.errorhandler(Exception)
def handler(e):
    return f"<h3>Hata:</h3><pre>{e}</pre>",500

if __name__=='__main__':
    init_app()
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
