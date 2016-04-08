from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_id(cur, nick):
    cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [nick])
    return cur.fetchone()[0]

def login(cur, username, password):

    cur.execute("SELECT nick FROM utilizadores WHERE nick = %s;", [username]) # CHECKS IF USERNAME EXSIST

    if cur.fetchone() != None:
        cur.execute("SELECT user_id FROM utilizadores WHERE nick = %s;", [username])

        user_id = cur.fetchone()[0]

        cur.execute("SELECT pal_chave FROM palavraschave WHERE item_id = %s;", (user_id,))

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
                return True
    else:
        return "This nick already exists. Please login."

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

    querie_new_auction = "INSERT INTO `artigos` VALUES (%s, '%s', %s, %s, '%s', '%s', '%s', %s, %s);" \
                         % (max_auction_id, nome_artigo, user_id, base_value, desc_artigo, initial_date, end_date, "NULL", "NULL")
    if cur.execute(querie_new_auction) == 1:
        conn.commit()
        return True
    else:
        return False

def get_all_auctions(cur):
    cur.execute("SELECT * FROM artigos")
    return cur.fetchall()

def get_user_nick_from_userid(cur, user_id):
    cur.execute("SELECT nick FROM utilizadores WHERE user_id = %s", [user_id])
    return cur.fetchone()

def update_bid_amount(conn, cur, bidder, item_id, bid):

    user_id = get_user_id(cur, bidder)

    update_bid_querie = "UPDATE `artigos` SET `melhor_lic`=%s, `melhor_val`= %s WHERE" \
                        " `item_id`= %s;" % (user_id, bid, item_id)

    if cur.execute(update_bid_querie) == 1:
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
