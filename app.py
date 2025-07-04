import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
DB_DIR     = os.path.join(BASE_DIR, 'static', 'data')
DB_PATH    = os.path.join(DB_DIR, 'gameface.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED_EXT= {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY']              = 'local-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']           = UPLOAD_DIR

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
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

def init_app():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            # 100 demo oyun
            demos = []
            for i in range(1, 101):
                demos.append(Game(
                    name=f"Game {i}",
                    story=f"Bu Game {i} için rastgele oluşturulmuş bir hikâye.",
                    best_players=f"Player{i}A, Player{i}B",
                    company=f"Company {i}",
                    image_filename='default.png'
                ))
            db.session.bulk_save_objects(demos)
            db.session.commit()

@app.route('/')
def index():
    search   = request.args.get('search','').strip()
    game_id  = request.args.get('game_id', type=int)
    query    = Game.query.order_by(Game.name)
    games    = query.filter(Game.name.ilike(f'%{search}%')).all() if search else query.all()
    game     = Game.query.get(game_id) if game_id else None
    feedbacks= Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('index.html',
        games=games, game=game, feedbacks=feedbacks, search=search
    )

@app.route('/add_game', methods=['POST'])
def add_game():
    name   = request.form.get('name','').strip()
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

@app.route('/delete_game/<int:game_id>')
def delete_game(game_id):
    g = Game.query.get_or_404(game_id)
    db.session.delete(g)
    db.session.commit()
    flash(f"{g.name} silindi.","success")
    return redirect(url_for('index'))

@app.route('/edit_game/<int:game_id>', methods=['GET','POST'])
def edit_game(game_id):
    g = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        g.name         = request.form.get('name','').strip()
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

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    msg = request.form.get('message','').strip()
    if msg:
        db.session.add(Feedback(message=msg))
        db.session.commit()
        flash("Teşekkürler, geri bildirim alındı.","success")
    else:
        flash("Boş bırakılamaz.","error")
    return redirect(url_for('index'))

@app.route('/gift/<int:game_id>', methods=['GET','POST'])
def gift(game_id):
    g = Game.query.get_or_404(game_id)
    if request.method=='POST':
        iban = request.form.get('iban','').strip()
        flash(f"{g.name} için bağış talebiniz alındı (IBAN: {iban}).","success")
        return redirect(url_for('index', game_id=game_id))
    return render_template('gift.html', game=g)

@app.errorhandler(Exception)
def on_error(e):
    return f"<h3>Beklenmedik hata:</h3><pre>{e}</pre>",500

if __name__=='__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
