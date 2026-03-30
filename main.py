from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)


# ====== MODELS ======

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))
    phone_number = Column(String(20))
    street_address = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(20))

    accounts = relationship("Account", back_populates="user")


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    balance = Column(Float, default=0.0)
    account_number = Column(String(20), unique=True)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    amount = Column(Float)
    type = Column(Enum('debit', 'credit', name='transaction_type'))
    date = Column(DateTime)

    account = relationship("Account", back_populates="transactions")


# ====== DATABASE SETUP ======

conn_str = "mysql://root:cset155@localhost/bankdb"
engine = create_engine(conn_str, echo=True)
Session = sessionmaker(bind=engine)
db_session = Session()


app.secret_key = 'CSET170SecretKey' 


# ====== ROUTES ======

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Here you would normally check username/password
        user = {"id": 1, "username": "johndoe"}  # Mock user for now

        session['logged_in'] = True
        session['user_id'] = user['id']  # <-- store user ID for DB queries

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
    
    users = get_users()  # Placeholder function to fetch all users from DB
    return render_template('admin.html', users=users)

@app.route('/account')
def account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    user = get_user(user_id)  # Placeholder function to fetch user details from DB
    return render_template('account.html', user=user)

@app.route('/transactions')
def transactions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    transactions = get_user_transactions(user_id)
    return render_template('transactions.html', transactions=transactions)

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


# ====== HELPER FUNCTIONS ======

def get_user(user_id):
    # Placeholder: will query database once ready
    return db_session.query(User).filter(User.id == user_id).first()

def get_user_transactions(user_id):
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user or not user.accounts:
        return []
    # Return all transactions for first account (simplified)
    return user.accounts[0].transactions

def get_users():
    return db_session.query(User).all()

def create_user(data):
    user = User(**data)
    db_session.add(user)
    db_session.commit()
    return user

def create_transaction(account_id, amount, txn_type):
    txn = Transaction(account_id=account_id, amount=amount, type=txn_type)
    db_session.add(txn)
    db_session.commit()
    return txn

if __name__ == '__main__':
    app.run(debug=True)