from flask import Flask, render_template, request, session, redirect, escape, url_for, flash
from flask.ext.mysql import MySQL
from bs4 import BeautifulSoup

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'asw44285'
app.config['MYSQL_DATABASE_PASSWORD'] = 'asw44285'
app.config['MYSQL_DATABASE_DB'] = 'asw44285'
app.config['MYSQL_DATABASE_HOST'] = 'appserver.di.fc.ul.pt'
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

        cur.execute("SELECT nick FROM utilizadores WHERE nick = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        if cur.fetchone()[0]:

            cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [username_form])
            user_id = cur.fetchone()[0]

            cur.execute("SELECT pal_chave FROM palavraschave WHERE item_id = %s;", (user_id,))
            if password_form == cur.fetchone()[0]:
                session["username"] = username_form
                flash("You logged in successfully!")
                return redirect(url_for('leiloes'))
            else:
                error = "Invalid Username or Password"
        else:
            error = "Invalid Username or Password"
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

                querie_regist_user = "INSERT INTO `utilizadores` VALUES (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '', '%s');" \
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

@app.route('/admin')
def admin():
    return render_template("admin.html")

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)
