from flask import Flask, render_template

app = Flask(__name__)

#Home Page
@app.route('/')
def index():
    return render_template('index.html')

#Login Page
@app.route('/login')
def login():
    return render_template('login.html')

#Signup Page
@app.route('/signup')
def signup():
    return render_template('signup.html')

#Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)