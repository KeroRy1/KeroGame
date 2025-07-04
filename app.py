import os
from flask import Flask, render_template

app = Flask(__name__)

# Config: hem kod içinde hem de Render Env Vars üzerinden yönetilebilir
app.config['SECRET_KEY']    = os.environ.get('SECRET_KEY', 'dev-key')
app.config['DONATION_IBAN'] = os.environ.get('DONATION_IBAN', 'TR18 0001 5001 5800 7341 5288 14')
app.config['DONATION_NAME'] = os.environ.get('DONATION_NAME', 'Eymen Yiğit Karaman')

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
