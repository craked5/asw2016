from flask import Flask, render_template, request, session, redirect, escape, url_for, flash
from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import db_utils_flask
import time

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 20000
app.config['SESSION_TYPE'] = 'filesystem'

UPLOAD_FOLDER = '/imagens_USER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw44285'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cur = conn.cursor()

@app.route('/')
def leiloes():
    if 'username' in session:
        username_session = escape(session['username']).capitalize()






        return render_template('auctions.html', session_user_name=username_session)
    return render_template('auctions.html')

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

@app.route('/registo', methods=["GET", "POST"])
def registo():
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
        info["gender"] = request.form['gender']
        info["country"] = request.form['country']
        info["birth_date"] = request.form['birth-date']
        info["district"] = request.form['district']
        info["conselho"] = request.form['conselho']

        for key in info:
            if bool(BeautifulSoup(info[key], "html.parser").find()):
                error = "HTML detetado em " + str(key)
                return render_template('register.html', error=error)

        if db_utils_flask.register(conn, cur, info["username"], info["email"], info["password"], info["first_name"],
                                info["last_name"], info["gender"], info["country"],
                                info["birth_date"], info["conselho"], info["district"]) == True:
            return render_template("register.html", message="Regist was done good, please login!")

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

                return render_template("admin_logged.html", message=message, session_user_name = session['username'])

            username_session = escape(session['username'])
            return render_template('admin_logged.html', session_user_name=username_session)
        else:
            return redirect(url_for("leiloes", error="NOT ADMIN"))

    return redirect(url_for('leiloes'))

@app.route("/leilao/<leilao_id>", methods=["GET", "POST"])
def leilao(leilao_id):

    if request.method == "POST":
        pass


    if db_utils_flask.is_user_auction(cur, session["username"], leilao_id):
        render_template(leilao.html, is_user_auction = True, session_user_name = session["username"])
    else:
        render_template(leilao.html, session_user_name = session["username"])

@app.route("/leiloar", methods=["GET", "POST"])
def leiloar():

    info = {}
    if "username" in session:
        if request.method == 'POST':
            info["nome_artigo"] = request.form['nome-artigo']
            info["descricao_artigo"] = request.form['descricao-artigo']
            info["valor_base"] = request.form['valor-base']
            info["tags"] = request.form['tags']
            info["data_inicio"] = request.form['data-inicio']
            info["data_fim"] = request.form['data-fim']

            if db_utils_flask.make_new_auction(conn,cur,session["username"], info["nome_artigo"], info["descricao_artigo"],
                                               info["valor_base"], info["tags"], info["data_inicio"], info["data_fim"]):
                return render_template("new_auction.html", message="Leilao criado com sucesso!",
                                       session_user_name = session["username"])

        return render_template("new_auction.html", session_user_name = session["username"])

    return render_template("auctions.html", error="Por favor faca Login para criar um leilao novo!")

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "username" in session:
        if request.method == "POST":
            pass

        user_info = db_utils_flask.get_user_info(cur, session["username"])
        print user_info
        #TODO what info do i want to show here? return templates with that info
        return render_template("profile.html", session_user_name=session["username"], user_info=user_info)


if __name__ == '__main__':
    app.run(debug=True)