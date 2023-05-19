from urllib import response
from flask import Flask, request, render_template, url_for, redirect
import os
from time import time

import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from DataBase import AppDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter

# конфигурация
DATABASE = '/explorer.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
#MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__, static_folder="")

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'explorer.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('init_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    print("connecting to database")
    global dbase
    db = get_db()
    dbase = AppDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


"""
@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())
"""

"""
@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu = dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h
"""

"""
@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))
"""

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def root_dir():
    return redirect("/explorer")

@app.route("/explorer/")
def root_dir1():
    return subdir("")

def file_menu(file_path : str):
    ext = file_path.split('.')[-1]
    print('Opening file menu. Path =', file_path)
    exts = ['h', 'hpp', 'c', 'cpp', 'html', 'css', 'py', 'sh']
    fd = os.open(file_path, flags=os.O_RDONLY)
    content = (os.read(fd, 100000)).decode()
    if exts.count(ext) > 0:

        return highlight(content, guess_lexer_for_filename(file_path, content), HtmlFormatter(linenos=True, noclasses=True))
    
    return render_template('file_view.html', content=content)

@app.route("/explorer/<path:subpath>")
def subdir(subpath : str):
    realpath = '/' + subpath
    print("Explorer at path =", realpath)

    if (os.path.isfile("/"+subpath)):
        return file_menu("/"+subpath)
    
    if (os.path.isdir("/"+subpath)):
        subdirs = []
        dirlist = os.listdir("/"+subpath.strip())
        dirlist.sort() 
        for i in dirlist:
            i_path = os.path.join(realpath, i)
            i_params = dict()
            i_params["name"] = i
            i_params["size"] = 0
            if (os.path.islink(i_path)):
                i_params["type_icon"] = "/static/link.png"
                i_params["type"] = "link"
            elif (os.path.isdir(i_path)):
                i_params["type_icon"] = "/static/folder.png"
                i_params["type"] = "folder"
            elif (os.path.isfile(i_path)):
                i_params["type_icon"] = "/static/paper.png"
                i_params["type"] = "file"
            else:
                i_params["type_icon"] = "/static/question.png"
                i_params["type"] = "undefined type"

            i_params["href_path"] = "/explorer" + i_path
            subdirs.append(i_params)
        
        return render_template("index.html",
                                curdir="/explorer/"+subpath.strip(),
                                subdirs=subdirs, 
                                up_dir='/explorer/' + (os.path.split(subpath)[0] if subpath.strip() else ""),
                                menu=dbase.getMenu()
                              )


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    before_request()