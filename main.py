from flask import Flask, Response, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text, Connection

app = Flask(__name__)

# def initialize_db(conn:Connection, dbname:str):
#     conn.execute(text(f"CREATE DATABASE {dbname}"))


conn_str = "mysql://root:cset155@localhost/"
db_name = "bankdb"
server_engine = create_engine(conn_str, echo=True, connect_args={"local_infile":1})
conn = server_engine.connect()
result = conn.execute(text("SHOW DATABASES"))
databases = [row[0] for row in result.fetchall()]
if db_name not in databases:
    with open("scripts/sql/schema.sql") as f:
        sql = f.read()
    statements = [statement.strip() for statement in sql.split(';') if statement.strip()]
    with server_engine.begin() as transaction:
        for statement in statements:
            transaction.execute(text(statement))
engine = create_engine(conn_str+db_name, echo=True)
conn = engine.connect()

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