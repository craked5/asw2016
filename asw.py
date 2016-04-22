from flask import Flask, render_template, request, session, redirect, escape, url_for, flash, make_response
from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import db_utils_flask
from collections import OrderedDict
import time
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
#app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 20000
#app.config['SESSION_TYPE'] = 'filesystem'

#UPLOAD_FOLDER = '/imagens_USER'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cur = conn.cursor()

@app.route('/')
def leiloes():
    auctions = db_utils_flask.get_all_auctions(cur)
    print len(auctions)

    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        res = make_response(render_template('auctions.html', session_user_name=username_session, auctions = auctions))
        res.headers.set('Cache-Control', 'public, max-age=0')
        return res
    return render_template('auctions.html', auctions=auctions)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

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
            return render_template("auctions.html", message="Regist was done good, please login!")

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

@app.route("/leilao/<item_id>", methods=["GET", "POST"])
def leilao(item_id):

    auction = db_utils_flask.get_user_auction(cur, item_id)
    auction_owner = db_utils_flask.get_user_nick_from_userid(cur, auction[0][2])
    tags = db_utils_flask.get_auction_tags(cur, item_id)
    last_bidder = db_utils_flask.get_user_nick_from_userid(cur, auction[0][7])

    if last_bidder is None:
        last_bidder = []
        last_bidder.append("Nenhum")

    if request.method == "POST":

        if datetime.datetime.today() > auction[0][6]:
            res = make_response(render_template("auction.html", session_user_name=session["username"], is_user_auction=False,
                                   tags=tags, auction_info=auction, auction_owner=auction_owner,
                                   message="Este leilao ja acabou!", last_bidder = last_bidder[0]))
            res.headers.set('Cache-Control', 'public, max-age=0')
            return res
        elif datetime.datetime.today() < auction[0][5]:
            res =  make_response(render_template("auction.html", session_user_name=session["username"], is_user_auction=False,
                                   tags=tags, auction_info=auction, auction_owner=auction_owner,
                                   message="Este leilao ainda nao comecou!", last_bidder=last_bidder[0]))
            res.headers.set('Cache-Control', 'public, max-age=0')
            return res

        bid_amount = request.form["bid_amount"]
        if auction[0][8] is not None:
            print float(bid_amount) <= float(auction[0][8])
            print float(bid_amount)
            print float(auction[0][8])
            if float(bid_amount) <= float(auction[0][8]):
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="O valor da sua bid foi menor que o ultimo bid existente!", last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
            elif float(bid_amount) <= float(auction[0][3]):
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="O valor da sua bid foi menor que o valor base!",
                                       last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

            if auction_owner == session["username"]:
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="Nao pode fazer bids nos seus leiloes!",
                                       last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

            if db_utils_flask.update_bid_amount(conn, cur, session["username"], auction[0][0], bid_amount):
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="A sua bid foi aceite!", last_bidder = session["username"], new_bid = bid_amount))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
            else:
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="Ocurreu um error a fazer a sua bid", last_bidder = last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

    if db_utils_flask.is_user_auction(cur, session["username"], item_id):
        res = make_response(render_template("auction.html", is_user_auction = True, session_user_name = session["username"],
                               tags=tags, auction_info = auction, message=auction_owner, last_bidder = last_bidder[0]))
        res.headers.set('Cache-Control', 'public, max-age=0')
        return res

    res = make_response(render_template("auction.html", session_user_name = session["username"], is_user_auction = False,
                           tags=tags, auction_info=auction, auction_owner=auction_owner, last_bidder = last_bidder[0]))
    res.headers.set('Cache-Control', 'public, max-age=0')
    return res


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

        auctions_dict = {}
        tags_dict = {}
        user_info = db_utils_flask.get_user_info(cur, session["username"])

        user_number_auctions = db_utils_flask.get_user_auctions_number(cur, session["username"])

        for auction_number in user_number_auctions:
            print auction_number[0]
            auctions_dict[str(auction_number[0])] = db_utils_flask.get_user_auction(cur, auction_number[0])
            tags_dict[str(auction_number[0])] = db_utils_flask.get_auction_tags(cur, auction_number[0])
        print auctions_dict
        print tags_dict

        res = make_response(render_template("profile.html", session_user_name=session["username"], user_info=user_info,
                               auctions_info=auctions_dict, tags_info=tags_dict , datetime = datetime.datetime.today()))
        res.headers.set('Cache-Control', 'public, max-age=0')
        return res

@app.route("/editar_leilao/<item_id>", methods=["GET", "POST"])
def editar_leilao(item_id):
    if "username" in session:

        auction = db_utils_flask.get_user_auction(cur, item_id)
        auction_owner = db_utils_flask.get_user_nick_from_userid(cur, auction[0][2])
        tags = db_utils_flask.get_auction_tags(cur, item_id)
        last_bidder = db_utils_flask.get_user_nick_from_userid(cur, auction[0][7])

        print last_bidder

        print last_bidder == None

        if last_bidder is None:
            last_bidder = []
            last_bidder.append("Nenhum")

        info = {}
        if request.method == 'POST':
            info["nome_artigo"] = request.form['nome-artigo']
            info["descricao_artigo"] = request.form['descricao-artigo']
            info["valor_base"] = request.form['valor-base']
            info["tags"] = request.form['tags']
            print request.form['data-inicio']


            if request.form['data-inicio'] != '':
                info["data_inicio"] = request.form['data-inicio']
            else:
                info["data_inicio"] = auction[0][5]
            if request.form['data-fim'] != '':
                info["data_fim"] = request.form['data-fim']
            else:
                info["data_fim"] = auction[0][6]

            if datetime.datetime.today() >= auction[0][5]:
                return render_template("auction.html", message="Nao e possivel editar este leilao porque ja comecou!",
                                       session_user_name=session["username"],
                                       auction_info=auction, tags=tags, last_bidder="Nenhum",
                                       auction_owner=auction_owner)

            if db_utils_flask.update_auction(conn, cur, session["username"], auction[0][0], info["nome_artigo"],
                                               info["descricao_artigo"],
                                               info["valor_base"], info["tags"], info["data_inicio"],
                                               info["data_fim"]):

                auction = db_utils_flask.get_user_auction(cur, item_id)
                auction_owner = db_utils_flask.get_user_nick_from_userid(cur, auction[0][2])
                tags = db_utils_flask.get_auction_tags(cur, item_id)
                return render_template("auction.html", message="Leilao editado com sucesso!",
                                       session_user_name=session["username"],
                                       auction_info=auction, tags=tags, last_bidder="Nenhum", auction_owner=auction_owner)

        return render_template("edit_auction.html", session_user_name=session["username"],
                               auction = auction, auction_owner= auction_owner, tags=tags)

    return render_template("auctions.html", error="Por favor faca Login para editar um leilao!")

@app.route("/procurar", methods=["GET", "POST"])
def procurar():
    if "username" in session:
        if request.method == "POST":
            pass

        return render_template("search.html", session_user_name = session["username"])

    return render_template("search.html")

if __name__ == '__main__':
    app.run(debug=True)
