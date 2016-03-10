from flask import Flask, render_template, request, session, redirect, escape, url_for, flash
from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import db_utils_flask
import time

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SESSION_TYPE'] = 'memcached'

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cur = conn.cursor()

@app.route('/')
def leiloes():
    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        return render_template('leiloes.html', session_user_name=username_session)
    return render_template('leiloes.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('leiloes'))
    if request.method == 'POST':
        username_form  = request.form['username']
        password_form  = request.form['password']

        l_res = db_utils_flask.login(cur, username_form, password_form)
        error= l_res
        if l_res is True:
            session["username"] = username_form
            flash("You logged in successfully, redirecting...!")
            return redirect(url_for('leiloes'))

    return render_template('login.html', error=error)

@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
    info = {}

    if 'username' in session:
        return redirect(url_for('leiloes'))
    if request.method == 'POST':
        info["username"] = request.form['username']
        info["email"] = request.form['email']
        info["password"] = request.form['password']
        info["first_name"] = request.form['first-name']
        info["last_name"] = request.form['last-name']
        info["gender"] = request.form['male'] or request.form['female']
        info["country"] = request.form['country']
        info["birth_date"] = request.form['birth-date']
        info["district"] = request.form['district']
        info["conselho"] = request.form['conselho']

        for key in info:
            if bool(BeautifulSoup(info[key], "html.parser").find()):
                error = "A info em " + str(key) + " e ma!"
                return render_template('register.html', error=error)

        querie = "SELECT nick FROM utilizadores WHERE email = %s or nick = %s;"
        cur.execute(querie, [info["email"], info["username"]])

        if cur.fetchall() == ():
            #try:
            querie_get_max_id = "SELECT MAX(user_id)+1 from utilizadores"
            if cur.execute(querie_get_max_id) == 1:
                max_id = cur.fetchone()[0]
                if max_id == None:
                    max_id = 1

            querie_regist_password = "INSERT INTO `palavraschave` VALUES (%s, '%s');" % (max_id, info["password"])
            if cur.execute(querie_regist_password) == 1:

                querie_regist_user = "INSERT INTO `utilizadores` VALUES (%s, 0, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '', '%s');" \
                                     % (max_id, info["username"], info["first_name"], info["last_name"], info["email"],
                                        info["country"], info["conselho"], info["district"], info["birth_date"])
                if cur.execute(querie_regist_user) == 1:
                    conn.commit()
                    return render_template("register.html", message="Regist was done good, please login!")
            #except:
                #error = "Problem talking to the database :("
        else:
            error = "This email already exists. Please login."

    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('leiloes'))

@app.route('/admin', methods=["GET", "POST"])
def admin():
    error = None
    if 'username' in session:
        if db_utils_flask.is_admin(cur, session['username']) == 1:
            return redirect(url_for('admin_logged'))
        else:
            return redirect(url_for("leiloes"))

    if request.method == 'POST':
        username_form = request.form['username']
        password_form = request.form['password']
        if db_utils_flask.is_admin(cur, username_form) == 1:
            l_res = db_utils_flask.login(cur, username_form, password_form)
            error= l_res
            if l_res is True:
                session["username"] = username_form
                flash("You logged in successfully, redirecting...!")
                time.sleep(2)
                return redirect(url_for('admin_logged'))
        else:
            error="Your are not an Admin!"

    return render_template('admin.html', error=error)

@app.route("/admin_logged", methods=["GET", "POST"])
def admin_logged():
    error = None
    res = ''
    message = ''

    if 'username' in session:
        if db_utils_flask.is_admin(cur, session["username"]) == 1:
            if request.method == 'POST':
                username_email  = request.form['username_email']
                res = db_utils_flask.search_user(cur, username_email)

                if res != False:
                    for index, key in enumerate(res):
                        message += str(res[index]) + '\n\n\n'
                else:
                    message = "O username ou email inserido nao existe!"

                return render_template("admin_logged.html", message=message)

            username_session = escape(session['username']).capitalize()
            return render_template('admin_logged.html', session_user_name=username_session)
        else:
            return redirect(url_for("leiloes"))

    error= "NOT ADMIN!"
    return redirect(url_for('leiloes'))

if __name__ == '__main__':
    app.run(debug=True)
