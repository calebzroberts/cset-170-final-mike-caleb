from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # For now, just redirect to main page after "login"
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # For now, just redirect to login after "signup"
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/account')
def account():
    return render_template('account.html')

if __name__ == '__main__':
    app.run(debug=True)