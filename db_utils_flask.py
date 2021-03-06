from flask.ext.mysql import MySQL
from collections import OrderedDict
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_id(cur, nick):
    cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [nick])
    return cur.fetchone()[0]

def login(cur, username, password):

    cur.execute("SELECT nick FROM utilizadores WHERE nick = %s;", [username]) # CHECKS IF USERNAME EXSIST

    if cur.fetchone() != None:
        cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [username])

        user_id = cur.fetchone()[0]

        cur.execute("SELECT pal_chave FROM palavraschave WHERE item_id = '%s';", (user_id,))

        if password == cur.fetchone()[0]:
            return True
        else:
             return "Invalid Username or Password"
    else:
        return "Invalid Username or Password"

def register(conn, cur, username, email, password, first_name, last_name, gender, country, birth_date, district, conselho):

    querie = "SELECT nick FROM utilizadores WHERE email = %s or nick = %s;"
    cur.execute(querie, [email, username])

    if cur.fetchall() == ():
        #try:
        querie_get_max_id = "SELECT MAX(user_id)+1 from utilizadores"
        if cur.execute(querie_get_max_id) == 1:
            max_id = cur.fetchone()[0]
            if max_id == None:
                max_id = 1

        querie_regist_password = "INSERT INTO `palavraschave` VALUES (%s, '%s');" % (max_id, password)
        if cur.execute(querie_regist_password) == 1:

            querie_regist_user = "INSERT INTO `utilizadores` VALUES (%s, 0, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '', '%s');" \
                                 % (max_id, username, first_name, last_name, email,
                                    country, conselho, district, birth_date)
            if cur.execute(querie_regist_user) == 1:
                conn.commit()
                return [True, max_id]
    else:
        return [False, "O username ja existe! Por favor faca login!"]

def search_user(cur, nick_email):

    #querie = "SELECT * FROM utilizadores WHERE email = %s or nick = %s;" % (nick_email, nick_email)
    cur.execute("SELECT * FROM utilizadores WHERE email = %s or nick = %s;", [nick_email, nick_email])
    res = cur.fetchone()

    if res == None:
        return False
    else:
        return res

def is_admin(cur, nick):

    cur.execute("SELECT admin FROM utilizadores WHERE nick = %s;", [nick])
    return cur.fetchone()[0]

def is_user_auction(cur, nick, leilao_id):

    cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [nick])
    user_id = cur.fetchone()[0]

    cur.execute("SELECT user_id FROM artigos WHERE item_id = %s;", [leilao_id])

    if user_id == cur.fetchone()[0]:
        return True
    else:
        return False

def get_user_info(cur, nick):

    cur.execute("SELECT * FROM utilizadores WHERE nick = %s;", [nick])
    return cur.fetchone()

def get_user_auctions_number(cur, nick):
    user_id = get_user_id(cur,nick)
    cur.execute("SELECT item_id FROM artigos WHERE user_id = %s;", [user_id])
    return cur.fetchall()

def get_user_auction(cur, item_id):
    cur.execute("SELECT * FROM artigos WHERE item_id = %s;", [item_id])
    return cur.fetchall()

def get_auction_tags(cur, item_id):
    cur.execute("SELECT * FROM tags WHERE item_id = %s;", [item_id])
    return cur.fetchall()

def get_max_tag_id(cur):
    querie_get_max_tag_id = "SELECT MAX(tag_id)+1 from tags"
    if cur.execute(querie_get_max_tag_id) == 1:
        max_id = cur.fetchone()[0]
        if max_id == None:
            max_id = 1
            return max_id - 1
        return max_id - 1

def make_new_auction(conn, cur, nick, nome_artigo, desc_artigo, base_value, tags, initial_date, end_date):

    max_auction_id = 0
    user_id = get_user_id(cur,nick)

    try:
        querie_get_max_id = "SELECT MAX(item_id)+1 from artigos"
        if cur.execute(querie_get_max_id) == 1:
            max_auction_id = cur.fetchone()[0]
            if max_auction_id == None:
                max_auction_id = 1
    except:
        return "Error getting new id for an auction"

    tags = tags.split(" ")
    tag_id = get_max_tag_id(cur)

    for index, tag in enumerate(tags):
        tag_id += 1
        querie_new_tags = "INSERT INTO `tags` VALUES (%s, %s, %s, '%s');" \
            % (tag_id, user_id, max_auction_id, tags[index])
        cur.execute(querie_new_tags)

    querie_new_auction = "INSERT INTO `artigos` VALUES (%s, '%s', %s, %s, '%s', '%s', '%s', %s, %s, %s, %s);" \
                         % (max_auction_id, nome_artigo, user_id, base_value, desc_artigo, initial_date, end_date, "NULL", "NULL", 0, 0)
    if cur.execute(querie_new_auction) == 1:
        conn.commit()
        return [True, max_auction_id, user_id]
    else:
        return [False, '']

def get_all_auctions(cur):
    cur.execute("SELECT * FROM artigos ORDER BY data_fim")
    return cur.fetchall()

def get_user_nick_from_userid(cur, user_id):
    cur.execute("SELECT nick FROM utilizadores WHERE user_id = %s", [user_id])
    return cur.fetchone()

def update_bid_amount(conn, cur, bidder, item_id, data_bid, bid, anon):
    print bidder

    user_id = get_user_id(cur, bidder)

    if anon:
        anonimo = 1
    else:
        anonimo = 0

    querie_get_max_id = "SELECT MAX(bid_id)+1 from licitacoes"
    if cur.execute(querie_get_max_id) == 1:
        max_auction_id = cur.fetchone()[0]
        if max_auction_id == None:
            max_auction_id = 1
    else:
        return False

    update_bid_querie = "UPDATE `artigos` SET `melhor_lic`= %s, `melhor_val`= %s, anon_bid = %s WHERE" \
                        " `item_id`= %s;" % (user_id, bid, anonimo, item_id)
    print update_bid_querie

    update_bid_table_querie = "INSERT INTO `licitacoes` VALUES (%s, %s, %s, %s, '%s', %s);" \
                              % (max_auction_id, user_id, item_id, anonimo, data_bid, bid)
    print update_bid_table_querie
    if cur.execute(update_bid_querie) == 1:
        if cur.execute(update_bid_table_querie) == 1:
            conn.commit()
            return True
    else:
        return False

def update_auction(conn, cur, nick, auction_id, nome_artigo, desc_artigo, base_value, tags, initial_date, end_date):

    user_id = get_user_id(cur, nick)

    tags = tags.split(" ")
    tag_id = get_max_tag_id(cur)

    for index, tag in enumerate(tags):
        tag_id += 1
        querie_new_tags = "INSERT INTO `tags` VALUES (%s, %s, %s, '%s');" \
                          % (tag_id, user_id, auction_id, tags[index])
        cur.execute(querie_new_tags)

    querie_new_auction = "UPDATE `artigos` SET `item_id` = %s, `designacao` = '%s', `user_id`= %s," \
                         " `valor_base`=%s, `descricao`='%s', `data_entr`='%s', `data_fim`= '%s', " \
                         "`melhor_lic`= %s, `melhor_val`= %s where item_id = %s;" \
                         % (auction_id, nome_artigo, user_id, base_value, desc_artigo, initial_date, end_date,
                            "NULL", "NULL", auction_id)
    if cur.execute(querie_new_auction) == 1:
        conn.commit()
        return True
    else:
        return False

def get_auctions_participate(cur, username):

        user = get_user_id(cur, username)
        cur.execute("SELECT DISTINCT item_id FROM licitacoes where user_id = %s;", [user])
        my_biddings = cur.fetchall()

        auction_dict = {}
        last_bidders = {}
        i = 0

        for bidding_auction in my_biddings:
            i+=1
            cur.execute("SELECT * from artigos where item_id = %s;", [bidding_auction])
            auction_dict[i] = cur.fetchone()

            if auction_dict[i][8] != None:
                if auction_dict[i][9] != 1:
                    last_bidders[i] = get_user_nick_from_userid(cur, auction_dict[i][7])[0]
                else:
                    last_bidders[i] = "Anonimo"
            else:
                last_bidders[i] = "Nenhum"

        ordered = OrderedDict(sorted(auction_dict.items(), key=lambda t: t[1], reverse=True))
        return (ordered, last_bidders)

def get_all_bids_from_auction(cur, auction_id):

    bids = {}
    i = 0

    cur.execute("SELECT * from licitacoes where item_id = %s;", [auction_id])
    bids_raw = cur.fetchall()

    for bid in bids_raw:
        temp = []
        if bid[3] != 1:
            temp.append(get_user_nick_from_userid(cur, bid[1])[0])
        else:
            temp.append("Anonimo")
        temp.append(bid[5])
        temp.append(bid[4])

        bids[bid[0]] = temp

    return bids


def get_all_ended_auctions_participate(cur, user_id):

    bids = {}
    i = 0

    cur.execute("SELECT DISTINCT item_id from licitacoes where user_id = %s;", [user_id])
    bids_raw = cur.fetchall()
    print "stuff"
    print bids_raw

    for bid in bids_raw:
        temp = []
        if bid[3] != 1:
            temp.append(get_user_nick_from_userid(cur, bid[1])[0])
        else:
            temp.append("Anonimo")
        temp.append(bid[5])
        temp.append(bid[4])

        bids[bid[0]] = temp

def set_email_sent(conn, cur, item_id):

    querie = "UPDATE `artigos` SET `sent_email`= 1 WHERE" \
                        " `item_id`= %s;" % (item_id)

    if cur.execute(querie) == 1:
        conn.commit()
        return True
    else:
        return False

def search_articles(cur, *args):
    cur.execute("SELECT * FROM artigos where item_id = %s or designacao = %s or descricao = %s or data_fim = %s or data_entr = %s or valor_base = %s", [args[0], args[0],args[0],args[0],args[0],args[0]])
    res = cur.fetchall()
    return res


def get_highest_bid_item_id(cur, item_id):
    cur.execute("SELECT * FROM artigos where item_id = %s", [item_id])
    return cur.fetchall()

def check_user_exists(cur, username):
    cur.execute("SELECT DISTINCT nick FROM utilizadores where nick = %s", [username])
    users = cur.fetchall()
    if len(users) == 0:
        return False
    else:
        return True

def get_user_password_with_username(cur, username):
    id = get_user_id(cur, username)
    cur.execute("SELECT pal_chave FROM palavraschave where item_id = %s", [id])
    return cur.fetchone()[0]

def get_max_image_id_user(cur):
    querie_get_max_image_id = "SELECT MAX(item_id)+1 from imagens_user"
    if cur.execute(querie_get_max_image_id) == 1:
        max_id = cur.fetchone()[0]
        if max_id == None:
            max_id = 1
            return max_id - 1
        return max_id - 1

def add_new_image_user(conn, cur, path, user_id):

    item_id = get_max_image_id_user(cur)
    querie_new_image = "INSERT INTO `imagens_user` VALUES (%s, %s, '%s');" \
                      % (user_id, item_id, path)
    if cur.execute(querie_new_image):
        conn.commit()
        return True
    else:
        return False

def get_latest_user_image_user(cur, username):
    user_id = get_user_id(cur, username)

    cur.execute("SELECT MAX(item_id) from imagens_user where user_id = %s;", [user_id])
    max_image_id = cur.fetchone()
    if max_image_id[0] is not None:
        cur.execute("SELECT nome_img from imagens_user where item_id = %s;", [max_image_id[0]])
        path = cur.fetchone()[0]
        return [True, path]
    else:
        return [False, '']

def get_max_image_id_leilao(cur):
    querie_get_max_image_id = "SELECT MAX(item_id)+1 from imagens_leiloes"
    if cur.execute(querie_get_max_image_id) == 1:
        max_id = cur.fetchone()[0]
        if max_id == None:
            max_id = 1
            return max_id - 1
        return max_id - 1

def add_new_image_leilao(conn, cur, user_id, item_id, path):

    querie_new_image = "INSERT INTO `imagens_leiloes` VALUES (%s, %s, '%s');" \
                      % (user_id, item_id, path)
    if cur.execute(querie_new_image):
        conn.commit()
        return True
    else:
        return False

def get_latest_user_image_leilao(cur, username):
    user_id = get_user_id(cur, username)

    cur.execute("SELECT MAX(item_id) from imagens_leiloes where user_id = %s;", [user_id])
    max_image_id = cur.fetchone()
    if len(max_image_id) > 0:
        cur.execute("SELECT nome_img from imagens_leiloes where item_id = %s;", [max_image_id[0]])
        path = cur.fetchone()[0]
        return [True, path]
    else:
        return [False, '']

def get_leilao_image_by_id(cur, item_id):

    cur.execute("SELECT nome_img from imagens_leiloes where item_id = %s;", [item_id])
    path = cur.fetchone()
    if path is not None:
        return [True, path]
    else:
        return [False, '']
