#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, session, redirect, escape, url_for, \
    flash, make_response, g, send_from_directory
from flask.ext.mysql import MySQL
from flask.ext.socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import db_utils_flask
import datetime
import smtplib
import time
import os
import threading
import random

#------------------------------------------------APP CONFIG AND THREADING------------------------------------------------

UPLOAD_FOLDER = 'static/imagens'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SESSION_PERMANENT'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
mysql = MySQL()
socket = SocketIO(app, allow_upgrades=True, engineio_logger = True)


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#thread1 = emailSender(1, "emailSenderThread", 1)
#thread1.start()
#print threading.activeCount()
#print threading.enumerate()

#------------------------------------------------FLASK ROUTES------------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.before_request
def before_request_callbacks():
    g.conn = mysql.connect()
    g.cur = g.conn.cursor()

@app.teardown_request
def close_db(*args):
    g.conn.close()

@app.route('/')
def leiloes():
    auctions = db_utils_flask.get_all_auctions(g.cur)
    auctions_temp = []

    for index, item in enumerate(auctions):
        if datetime.datetime.today() <= item[6]:
            image_path = db_utils_flask.get_leilao_image_by_id(g.cur, item[0])
            image_path = image_path[1],
            item_temp = item + image_path
            print item
            print item_temp
            auctions_temp.append(item_temp)


    print auctions_temp

    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        res = make_response(render_template('auctions.html', session_user_name=username_session, auctions = auctions_temp))
        res.headers.set('Cache-Control', 'public, max-age=0')

        return res

    res = make_response(render_template('auctions.html', auctions=auctions_temp))
    res.headers.set('Cache-Control', 'public, max-age=0')
    return res

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

        l_res = db_utils_flask.login(g.cur, username_form, password_form)
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
        file = request.files['imagem']
        filename = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        for key in info:
            if bool(BeautifulSoup(info[key], "html.parser").find()):
                error = "HTML detetado em " + str(key)
                return render_template('register.html', error=error)

        res = db_utils_flask.register(g.conn, g.cur, info["username"], info["email"], info["password"], info["first_name"],
                                info["last_name"], info["gender"], info["country"],
                                info["birth_date"], info["conselho"], info["district"])
        if res[0] is True:
            if db_utils_flask.add_new_image_user(g.conn, g.cur, filename, res[1]):
                return render_template("auctions.html", message="O seu registo foi efectuado com sucesso! Faca login para bidar!")
            else:
                return render_template("register.html",
                                       error="Erro ao efetuar o seu registo!")
        else:
            return render_template("register.html",
                                   error=res[1])

    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    res = make_response(redirect(url_for('leiloes')))
    res.headers.set('Cache-Control', 'public, max-age=0')
    return res

@app.route('/admin', methods=["GET", "POST"])
def admin():
    error = None
    if 'username' in session:
        if db_utils_flask.is_admin(g.cur, session['username']) == 1:
            return redirect(url_for('admin_logged'))
        else:
            return redirect(url_for("leiloes"))

    if request.method == 'POST':
        username_form = request.form['username']
        password_form = request.form['password']
        if db_utils_flask.is_admin(g.cur, username_form) == 1:
            l_res = db_utils_flask.login(g.cur, username_form, password_form)
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
        if db_utils_flask.is_admin(g.cur, session["username"]) == 1:
            if request.method == 'POST':
                username_email  = request.form['username_email']
                res = db_utils_flask.search_user(g.cur, username_email)

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

    auction = db_utils_flask.get_user_auction(g.cur, item_id)
    auction_owner = db_utils_flask.get_user_nick_from_userid(g.cur, auction[0][2])
    tags = db_utils_flask.get_auction_tags(g.cur, item_id)
    bids = db_utils_flask.get_all_bids_from_auction(g.cur, item_id)

    if auction[0][9] == 1:
        last_bidder = ["Anonimo"]
    else:
        last_bidder = db_utils_flask.get_user_nick_from_userid(g.cur, auction[0][7])

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    if last_bidder is None:
        last_bidder = []
        last_bidder.append("Nenhum")

    if request.method == "POST":
        if "username" in session:
            if datetime.datetime.today() > auction[0][6]:
                res = make_response(render_template("auction.html", session_user_name=session["username"], is_user_auction=False,
                                       tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                       error="Este leilao ja acabou!", last_bidder = last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
            elif datetime.datetime.today() < auction[0][5]:
                res =  make_response(render_template("auction.html", session_user_name=session["username"], is_user_auction=False,
                                       tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                       error="Este leilao ainda nao comecou!", last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

            bid_amount = request.form["bid_amount"]
            if request.form.get('anon') == "anon":
                anon = True
            else:
                anon = False


            if auction[0][8] is not None:

                if float(bid_amount) <= float(auction[0][8]):
                    res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                           tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                           error="O valor da sua bid foi menor que o ultimo bid existente!", last_bidder=last_bidder[0]))
                    res.headers.set('Cache-Control', 'public, max-age=0')
                    return res

            if float(bid_amount) <= float(auction[0][3]):
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                       error="O valor da sua bid foi menor que o valor base!",
                                       last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

            if auction_owner[0] == session["username"]:
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                       error="Nao pode fazer bids nos seus leiloes!",
                                       last_bidder=last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

            if db_utils_flask.update_bid_amount(g.conn, g.cur, session["username"], auction[0][0], today ,bid_amount, anon):
                if anon:
                    last_bidder = ["Anonimo"]
                else:
                    last_bidder = [session["username"]]
                socket.emit("bid", {'bid': bid_amount, 'id':auction[0][0]}, broadcast=True)
                bids = db_utils_flask.get_all_bids_from_auction(g.cur, item_id)
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner,
                                       message="A sua bid foi aceite!", last_bidder = last_bidder[0],
                                                    new_bid = bid_amount, licitacoes=bids))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
            else:
                res = make_response(render_template("auction.html", is_user_auction=True, session_user_name=session["username"],
                                       tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                       error="Ocurreu um error a fazer a sua bid", last_bidder = last_bidder[0]))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
        else:
            res = make_response(
                render_template("auction.html", is_user_auction=True,
                                tags=tags, auction_info=auction, auction_owner=auction_owner, licitacoes=bids,
                                error="Tem de fazer o Login para poder biddar!", last_bidder=last_bidder[0]))
            res.headers.set('Cache-Control', 'public, max-age=0')
            return res
    if session.has_key("username"):
        sess_user = session["username"]
    else:
        sess_user = ""
    res = make_response(
        render_template("auction.html", session_user_name=sess_user, is_user_auction=False, licitacoes=bids,
                        tags=tags, auction_info=auction, auction_owner=auction_owner, last_bidder=last_bidder[0]))
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
            file = request.files['imagem']
            filename = ''
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            res = db_utils_flask.make_new_auction(g.conn,g.cur,session["username"], info["nome_artigo"], info["descricao_artigo"],
                                               info["valor_base"], info["tags"], info["data_inicio"], info["data_fim"])
            if res[0] is True:
                if db_utils_flask.add_new_image_leilao(g.conn, g.cur, filename, res[1]):
                    return render_template("auctions.html", message="Leilao criado com sucesso!",
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
        user_info = db_utils_flask.get_user_info(g.cur, session["username"])
        filename = db_utils_flask.get_latest_user_image_user(g.cur, session["username"])
        user_number_auctions = db_utils_flask.get_user_auctions_number(g.cur, session["username"])
        for auction_number in user_number_auctions:
            print auction_number[0]
            auctions_dict[str(auction_number[0])] = db_utils_flask.get_user_auction(g.cur, auction_number[0])
            tags_dict[str(auction_number[0])] = db_utils_flask.get_auction_tags(g.cur, auction_number[0])

        auctions_dict_participate, last_bidders = db_utils_flask.get_auctions_participate(g.cur, session["username"])

        #last_bidders_ended = {}
        aucts_dict_participate_end = {}
        for aucts in auctions_dict_participate:
            if auctions_dict_participate[aucts][6] <= datetime.datetime.today():
                aucts_dict_participate_end[auctions_dict_participate[0]] = aucts
                #last_bidders_ended[auctions_dict_participate[0]] = last_bidders[auctions_dict_participate[0]]

        if filename[0] is True:
            res = make_response(render_template("profile.html", session_user_name=session["username"], user_info=user_info,
                                   auctions_info=auctions_dict, tags_info=tags_dict , datetime = datetime.datetime.today(),
                                    bid_auctions_ended=aucts_dict_participate_end, bid_auctions=auctions_dict_participate,
                                    last_bidders=last_bidders, user_image_file=filename[1]))
            res.headers.set('Cache-Control', 'public, max-age=0')
            return res
        else:
            res = make_response(
                render_template("profile.html", session_user_name=session["username"], user_info=user_info,
                                auctions_info=auctions_dict, tags_info=tags_dict, datetime=datetime.datetime.today(),
                                bid_auctions_ended=aucts_dict_participate_end, bid_auctions=auctions_dict_participate,
                                last_bidders=last_bidders))
            res.headers.set('Cache-Control', 'public, max-age=0')
            return res

@app.route("/editar_leilao/<item_id>", methods=["GET", "POST"])
def editar_leilao(item_id):
    if "username" in session:

        auction = db_utils_flask.get_user_auction(g.cur, item_id)
        auction_owner = db_utils_flask.get_user_nick_from_userid(g.cur, auction[0][2])
        tags = db_utils_flask.get_auction_tags(g.cur, item_id)
        last_bidder = db_utils_flask.get_user_nick_from_userid(g.cur, auction[0][7])

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

            if db_utils_flask.update_auction(g.conn, g.cur, session["username"], auction[0][0], info["nome_artigo"],
                                               info["descricao_artigo"],
                                               info["valor_base"], info["tags"], info["data_inicio"],
                                               info["data_fim"]):

                auction = db_utils_flask.get_user_auction(g.cur, item_id)
                auction_owner = db_utils_flask.get_user_nick_from_userid(g.cur, auction[0][2])
                tags = db_utils_flask.get_auction_tags(g.cur, item_id)
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
            args = request.form["search_article"]

            searched_items = db_utils_flask.search_articles(g.cur, args)

            if searched_items != ():
                res = make_response(render_template("search.html", session_user_name = session["username"], search_auctions = searched_items))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res
            else:
                res = make_response(render_template("search.html", session_user_name=session["username"], error="Nao foram encontrados nenhuns leiloes com a sua pesquisa!"))
                res.headers.set('Cache-Control', 'public, max-age=0')
                return res

        return render_template("search.html", session_user_name = session["username"])

    return render_template("search.html")

@app.route("/php/valorActualDoItem", methods=["POST"])
def valorActualDoItem():

    item_id  = request.get_json(force=True)


    item = db_utils_flask.get_highest_bid_item_id(g.cur, item_id['id'])

    print item
    if item[0][8] is None:
        return "0"
    else:
        return str(item[0][8])


@app.route("/php/licitaItem", methods=["POST"])
def licitaItem():

    stuff  = request.get_json(force=True)
    print stuff
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    item = db_utils_flask.get_user_auction(g.cur, int(stuff["id"]))

    if db_utils_flask.check_user_exists(g.cur, stuff["username"]):
        if stuff["password"] == db_utils_flask.get_user_password_with_username(g.cur, stuff['username']):
            pass
        else:
            return "Nao Aceite - Password para o user " + str(stuff["username"]) + ' esta errada!'
    else:
        return "Nao Aceite - O user " + str(stuff["username"]) + ' nao existe!'

    if len(item)==0:
        return "Nao Aceite - item nao existe!"

    elif item[0][8] is None:
        pass

    elif item[0][6] < datetime.datetime.today():
        return "Terminado"

    elif int(item[0][2]) == int(db_utils_flask.get_user_id(g.cur, stuff["username"])):
        return "Nao Aceite - Nao pode bidar nos seus leiloes!"

    elif item[0][8] < stuff["valor"]:
        if item[0][3] < stuff["valor"]:
            pass
        else:
            return "Nao Aceite - bid inferior ao valor base!"
    else:
        return "Nao Aceite - bid inferior a ultima bid!"


    if db_utils_flask.update_bid_amount(g.conn, g.cur, stuff["username"], stuff["id"], today, stuff["valor"], 0):
        socket.emit("bid", {'bid': stuff["valor"], 'id':item[0][0]}, broadcast=True)
        return "Aceite"
    else:
        return "Nao Aceite - erro!"

if __name__ == '__main__':
    socket.run(app, debug=True)




