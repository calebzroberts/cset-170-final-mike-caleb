from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text

app = Flask(__name__)

# conn_str = "mysql://root:cset155@localhost/bankdb"
# engine = create_engine(conn_str, echo=True)
# conn = engine.connect()

app.secret_key = 'CSET170SecretKey' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # validate user here later
        session['logged_in'] = True
        return redirect(url_for('account'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # For now, just redirect to login after "signup"
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/account')
def account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('account.html')

@app.route('/transactions')
def transactions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('transactions.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # For now, just redirect to login after "signup"
        return redirect(url_for('transactions'))
    
    return render_template('transfer.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.context_processor
def inject_user():
    return dict(logged_in=session.get('logged_in', False))

if __name__ == '__main__':
    app.run(debug=True)