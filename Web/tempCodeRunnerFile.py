from flask import Flask, render_template, url_for, redirect

app = Flask(__name__, static_folder='static', template_folder='templates')

# 🔹 Route landing
@app.route('/')
@app.route('/landing')
def landing():
    return render_template('landing.html')

# 🔹 Route login
@app.route('/login')
def login():
    return render_template('login.html')

# 🔹 Route register
@app.route('/register')
def register():
    return render_template('register.html')

# 🔹 Route index (setelah login berhasil)
@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
