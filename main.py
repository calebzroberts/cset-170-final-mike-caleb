from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, create_engine, Connection, text
from sqlalchemy.orm import sessionmaker
import hashlib as hash
import random

app = Flask(__name__)


# ====== DATABASE SETUP ======

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
Session = sessionmaker(bind=engine)
db_session = Session()

app.secret_key = 'CSET170SecretKey' 


# ====== ROUTES ======

@app.route('/')
def index():
    logged_in = session.get('logged_in')

    is_admin1=session.get('is_admin', False)

    is_admin2 = is_admin(session.get('user_id')) if logged_in else False

    if is_admin1 == True and is_admin2 == True:
        return render_template('index.html', logged_in=logged_in, is_admin = is_admin1)
    
    return render_template('index.html', logged_in=logged_in, is_admin = False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_error = None
    if request.method == 'POST':
        form = request.form
        username = form.get("username")
        stored_pass = conn.execute(text("SELECT password FROM people WHERE username = :username"),
                                   {"username": username}).first()[0]

        if hash_from_str(form.get("password")) == stored_pass:
            session['logged_in'] = True
            session['user_id'] = username
            if is_admin(username):
                session['is_admin'] = True
                return redirect(url_for('admin'))
            return redirect(url_for('account'))
        else:
            login_error = "Username or Password Incorrect!"
    return render_template('login.html', error = login_error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_error = None
    if request.method == 'POST':
        form = request.form
        if all(form.values()):
            user = {
                "username":form.get("username"),
                "password":hash_from_str(form.get("password")),
                "first_name":form.get("first_name"),
                "last_name":form.get("last_name"),
                "address":str("\"" + form.get("street_address") + " "
                              + form.get("city")+", "
                              + form.get("state") + " "
                              + form.get("zip_code") + "\""),
                "phone":f"\"{form.get("phone_numer")}\"",
                "ssn":hash_from_str(form.get("ssn")),
            }
            create_user(user)
            return redirect(url_for('login'))
        else:
            signup_error = "Please complete all fields."
    return render_template('signup.html', error = signup_error)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        return "Unauthorized", 403

    users = get_users() 
    return render_template('admin.html', users=users)

@app.route('/admin/approve', methods=['POST'])
def approve_user():
    if not session.get('logged_in') or not session.get('is_admin'):
        return "Unauthorized", 403

    username = request.form.get("username")
    if not username:
        return "Bad request", 400
    
    # Update the database
    stmt = text("UPDATE users SET approved = TRUE WHERE username = :username")
    conn.execute(stmt, {"username": username})
    conn.commit()

    def generate_acct_num():
        return random.randint(11111111, 99999999)
    acct_num = generate_acct_num()
    rslt = conn.execute(text("SELECT acct_num FROM accounts")).all()
    while acct_num in rslt:
        acct_num = generate_acct_num()

    ssn = get_user(username).get("ssn")

    data = {"acct_num": acct_num, "ssn": ssn}
    
    stmt = text("""
                INSERT INTO accounts (acct_num, ssn, balance)
                VALUES (:acct_num, :ssn, 0.00)
                """)
    conn.execute(stmt, data)
    conn.commit()

    return redirect(url_for('admin'))

@app.route('/account')
def account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    user = get_user(user_id)
    account = get_account_with_approval(user_id)

    approved = account['approved'] if account else False

    return render_template(
        'account.html',
        user=user,
        account=account,
        approved=approved
)

@app.route('/reset-db', methods=['POST'])
def reset_db():
    if not session.get('logged_in') or not session.get('is_admin'):
        return "Unauthorized", 403

    # Drop the database
    conn.execute(text("DROP DATABASE IF EXISTS bankdb"))
    conn.commit()
    return "Database reset successfully. Please restart the server to reinitialize.", 200


# @app.route('/transactions')
# def transactions():
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))

#     user_id = session.get('user_id')
#     transactions = get_user_transactions(user_id)
#     return render_template('transactions.html', transactions=transactions)

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
    return dict(
        logged_in=session.get('logged_in', False),
        is_admin=session.get('is_admin', False))


# ====== HELPER FUNCTIONS ======

def hash_from_str(inp_str:str) -> str:
    pepper = hash.sha256("sparkles".encode()).hexdigest()
    return hash.sha256((inp_str+pepper).encode()).hexdigest()

def get_user(username):
    """Fetch a single user by username, including person info and role"""
    stmt = text("""
        SELECT u.ssn, u.username, u.address, u.phone, u.approved,
               p.first_name, p.last_name,
               r.is_admin
        FROM users u
        JOIN people p ON u.username = p.username
        LEFT JOIN roles r ON u.username = r.username
        WHERE u.username = :username
    """)
    result = conn.execute(stmt, {"username": username}).mappings().first()

    if not result:
        return None
    
    user = dict(result)

    user['approved'] = bool(user['approved'])
    return user


def get_users():
    """Fetch all unapproved users"""
    stmt = text("""
        SELECT u.ssn, u.username, u.address, u.phone, u.approved,
               p.first_name, p.last_name,
               r.is_admin
        FROM users u
        JOIN people p ON u.username = p.username
        LEFT JOIN roles r ON u.username = r.username
        WHERE u.approved = FALSE
        ORDER BY u.ssn ASC
    """)
    results = conn.execute(stmt).mappings().all()
    return [dict(user) for user in results]



def create_user(data:dict):
    """
    Insert a new person, role (optional), and user.
    `data` must include: username, password, first_name, last_name, address, phone
    """
    # Insert person
    stmt_person = text("""
        INSERT INTO people (username, password, first_name, last_name)
        VALUES (:username, :password, :first_name, :last_name)
    """)
    conn.execute(stmt_person, data)

    # Set role
    stmt_person = text("""
        INSERT INTO roles (username, is_admin)
        VALUES (:username, FALSE)
    """)
    conn.execute(stmt_person, data)

    # Insert user
    stmt_user = text("""
        INSERT INTO users (ssn, username, address, phone, approved)
        VALUES (:ssn, :username, :address, :phone, FALSE)
    """)
    conn.execute(stmt_user, data)
    conn.commit()

    # Fetch the newly inserted user
    return get_user(data['username'])

def is_admin(username):
    result = bool(conn.execute(
        text("SELECT is_admin FROM roles WHERE username = :username"),
        {"username": username}
    ).first()[0])
    return result

def create_transaction(ssn, amount, txn_type):
    """
    Insert a transaction for a user's account.
    `txn_type` can be 'deposit' or 'withdrawal' or similar.
    """
    # Get user's account
    acct_stmt = text("SELECT acct_num FROM accounts WHERE ssn = :ssn LIMIT 1")
    account = conn.execute(acct_stmt, {"ssn": ssn}).mappings().first()
    if not account:
        return None  # No account exists

    acct_num = account['acct_num']

    # Insert transaction
    txn_stmt = text("""
        INSERT INTO transactions (account_id, amount, type, date)
        VALUES (:acct_num, :amount, :txn_type, NOW())
    """)
    conn.execute(txn_stmt, {"acct_num": acct_num, "amount": amount, "txn_type": txn_type})
    conn.commit()

    # Fetch the inserted transaction (latest for account)
    fetch_stmt = text("""
        SELECT id, account_id, amount, type, date
        FROM transactions
        WHERE account_id = :acct_num
        ORDER BY id DESC
        LIMIT 1
    """)
    txn = conn.execute(fetch_stmt, {"acct_num": acct_num}).mappings().first()
    return dict(txn) if txn else None

def get_account_with_approval(username):
    stmt = text("""
        SELECT a.acct_num, a.balance,
               u.approved
        FROM users u
        JOIN accounts a ON u.ssn = a.ssn
        WHERE u.username = :username
        LIMIT 1
    """)
    result = conn.execute(stmt, {"username": username}).mappings().first()

    if not result:
        return None

    account = dict(result)
    account['approved'] = bool(account['approved'])
    return account

def reset_databases():
    conn.execute(text("DROP DATABASE IF EXISTS bankdb"))

# def get_user_transactions(user_id):
#     # Get first account for the user
#     stmt = text("SELECT id FROM accounts WHERE user_id = :uid LIMIT 1")
#     account = conn.execute(stmt, {"uid": user_id}).mappings().first()
#     if not account:
#         return []

#     account_id = account['id']

#     # Get transactions for that account
#     txn_stmt = text("""
#         SELECT id, amount, type, date
#         FROM transactions
#         WHERE account_id = :aid
#         ORDER BY date DESC
#     """)
#     transactions = conn.execute(txn_stmt, {"aid": account_id}).mappings().all()
#     return [dict(txn) for txn in transactions]



if __name__ == '__main__':
    app.run(debug=True)