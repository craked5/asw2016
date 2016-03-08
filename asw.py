from flask import Flask, render_template, request, session, redirect, escape, url_for
from flask.ext.mysql import MySQL
from bs4 import BeautifulSoup

app = Flask(__name__)

mysql = MySQL()


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cur = conn.cursor()


querie = "INSERT INTO `utilizadores` " \
                "(`user_id`, `nick`, `nome`, `apelido`, `email`, `pais`, `concelho`, `distrito`, `foto`, `data_reg`, `password`) " \
                "VALUES ('MAX(user_id)+1', %s, %s, %s, %s, %s, %s, %s, %s, %s);"
args = ("dwada", "dwadwda", "dwadawda", "dwdawdaw",
        "dwadwd", "fefefs", "dwfegregsgrg", "", "2016-03-29", "dpwadwd",)
cur.execute(querie, args)
print cur.fetchall()

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
        cur.execute("SELECT nick FROM utilizadores WHERE nick = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        if cur.fetchone()[0]:
            cur.execute("SELECT password FROM utilizadores WHERE password = %s;", [password_form]) # FETCH THE HASHED PASSWORD
            for row in cur.fetchall():
                if password_form == row[0]:
                    session['username'] = request.form['username']
                    return redirect(url_for('leiloes'))
                else:
                    error = "Invalid Username or Password"
        else:
            error = "Invalid Username or Password"
    return render_template('login_register.html', error=error)

@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
    info = {}

    if 'username' in session:
        return redirect(url_for('leiloes'))
    if request.method == 'POST':
        info["username"] = request.form['username']
        info["email"] = request.form['email']
        print request.form['password']
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
                return render_template('login_register.html', error=error)

        querie = "SELECT email FROM utilizadores WHERE email = %s or nick = %s;"
        cur.execute(querie, [info["email"], info["username"]])
        print cur.fetchone()
        if cur.fetchall() == ():

            querie = "INSERT INTO `utilizadores` " \
                "(`user_id`, `nick`, `nome`, `apelido`, `email`, `pais`, `concelho`, `distrito`, `foto`, `data_reg`, `password`) " \
                "VALUES ('MAX(user_id)+1', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
            args = (info["username"], info["first_name"], info["last_name"], info["email"],
                    info["country"], info["conselho"], info["district"], None, info["birth_date"], info["password"])

            cur.execute(querie, args)
            if conn.commit():
                return render_template("login_register.html", message="Regist was done good")
        else:
            error = "This email already exists. Please login."

    return render_template('login_register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('leiloes'))

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run()
