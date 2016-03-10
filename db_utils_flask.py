from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

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