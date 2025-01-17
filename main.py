from flask import Flask, request, flash, render_template, url_for, session, redirect
import sqlite3
from cachelib import FileSystemCache
from flask_session import Session

app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)

con = sqlite3.connect("date.bd", check_same_thread=False)
cursor = con.cursor()


@app.route("/", methods=['POST', 'GET'])
def main_posts():
    cursor.execute('SELECT * FROM image_db')
    a = cursor.fetchall()
    if request.method == 'POST':
        flash('Успешное успешье', 'succerss')
        return render_template("save_post.html", db=a)
    else:
        return render_template("save_post.html", db=a)


@app.route("/save_post_more/<int:id_user>")
def save_post_more(id_user):
    cursor.execute('SELECT * FROM image_db WHERE id = (?)', (id_user,))
    a = cursor.fetchall()
    for i in a:
        if i[0] == id_user:
            break
    return render_template("save_post_more.html", post=i)


@app.route("/save_post/", methods=['POST'])
def save_post():
    image = request.files.get('image')
    image.save(f'static/{image.filename}')
    cursor.execute(
        "INSERT INTO image_db (title, file_name, description) VALUES (?,?,?) ",
        (request.form['title'],
         f'static/{image.filename}',
         request.form['description']))
    con.commit()
    return redirect(url_for('main_posts'))


@app.route("/register/")
def register_page():
    return render_template("register.html")


@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля ', 'succerss')
    return redirect(url_for('main_posts'))


@app.route("/add/")
def add():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('page_login'))
    return render_template('add.html')


@app.route("/login/")
def page_login():
    return render_template("login.html")


@app.route("/save_register/", methods=['POST', 'GET'])
def page_index():
    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO password_email ( last_name , name, patronymic, gender,  email, username, password) VALUES (?,?,?,?,?,?,?) ",
            (request.form['last_name'],
             request.form['name'],
             request.form['patronymic'],
             request.form['gender'],
             request.form['email'],
             request.form['username'],
             request.form['password']))
        con.commit()
        return 'регистрированние закончено'
    return 'зарегестрованный'


@app.route("/authorization/", methods=['POST', 'GET'])
def authorization_page():
    if request.method == 'POST':
        session['login'] = True
        # session['username'] = login
        session.permanent = False
        session.modified = True
        login = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM password_email  WHERE username=(?) and password=(?)', (login, password))
        data = cursor.fetchall()
        if data:
            flash('Вы авторизованны', 'succerss')
            return redirect(url_for('main_posts'))
        else:
            flash('Неверный логин или пароль', 'danger')
            return render_template('login.html')
    return render_template('authorization.html')


app.run(debug=True)
