from flask import Flask, render_template, request
from flask.ext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'halflife2'
app.config['MYSQL_DATABASE_DB'] = 'asw'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

cursor = conn.cursor()
cursor.execute("INSERT INTO utilizadores (`user_id`, `nick`, `nome`, `apelido`, `email`, `pais`, `concelho`, `distrito`, `data_reg`) VALUES ('3', 'wad', 'awd', 'awd', 'awdawd', 'awd', 'awd', 'awd', '2016-03-03')")
users = cursor.fetchall()
print users

@app.route('/')
def leiloes():
    return render_template('leiloes.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login_register.html')

@app.route('/register', methods=["GET", "POST"])
def register():

    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    cursor = conn.cursor()
    cursor.execute("INSERT INTO utilizadores (`user_id`, `nick`, `nome`, `apelido`, `email`, `pais`, `concelho`, `distrito`, `data_reg`) VALUES ('3', 'wad', 'awd', 'awd', 'awdawd', 'awd', 'awd', 'awd', '2016-03-03')")
    users = cursor.fetchall()
    print users

    return render_template('login_register.html')

if __name__ == '__main__':
    app.run()
