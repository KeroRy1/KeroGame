import os
from flask import Flask, render_template

app = Flask(__name__)

# Config: hem kod içinde hem de Render Env Vars üzerinden yönetilebilir
app.config['SECRET_KEY']    = os.environ.get('SECRET_KEY', 'dev-key')
app.config['DONATION_IBAN'] = os.environ.get('DONATION_IBAN', 'TR76 1234 5678 9012 3456 7890 12')
app.config['DONATION_NAME'] = os.environ.get('DONATION_NAME', 'Kerem Yılmaz')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gift')
def gift():
    return render_template('gift.html')

if __name__ == '__main__':
    # Render PORT env var kullanır; yoksa 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
