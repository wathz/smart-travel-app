from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        reset_code TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/onboarding1')
def onboarding1():
    return render_template('onboarding1.html')

@app.route('/onboarding2')
def onboarding2():
    return render_template('onboarding2.html')

@app.route('/onboarding3')
def onboarding3():
    return render_template('onboarding3.html')

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('onboarding1.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, password))
            conn.commit()
            conn.close()

            return redirect('/login')

        except:
            conn.close()
            flash("Email already exists!", "error")
            return redirect('/register')

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect('/dashboard')
        else:
            flash("Invalid email or password", "error")
            return redirect('/login')

    return render_template('login.html')

@app.route('/guest')
def guest():
    session['user_name'] = "Guest"
    return redirect('/dashboard')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------- GENERATE CODE ----------
def generate_code():
    return str(random.randint(100000, 999999))

# ---------- FORGOT PASSWORD ----------
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        print("EMAIL ENTERED:", email)
        print("USER FOUND:", user)

        if user:
            code = generate_code()

            cursor.execute("UPDATE users SET reset_code=? WHERE email=?", (code, email))
            conn.commit()
            conn.close()

            print("RESET CODE:", code)  # 🔥 IMPORTANT (check terminal)

            return redirect(url_for('verify_code', email=email))
        else:
            conn.close()
            flash("Email not found", "error")
            return redirect('/forgot-password')

    return render_template('forgot_password.html')

# ---------- VERIFY CODE ----------
@app.route('/verify-code/<email>', methods=['GET', 'POST'])
def verify_code(email):
    if request.method == 'POST':
        entered_code = request.form['code']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT reset_code FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        conn.close()

        if result and entered_code == result[0]:
            return redirect(url_for('reset_password', email=email))
        else:
            flash("Invalid code", "error")
            return redirect(request.url)

    return render_template('verify_code.html', email=email)

# ---------- RESET PASSWORD ----------
@app.route('/reset-password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        new_password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET password=?, reset_code=NULL WHERE email=?",
                       (new_password, email))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('reset_password.html')


# ---------- Notification ----------
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')    

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)