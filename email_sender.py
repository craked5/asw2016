class emailSender (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print "Starting " + self.name
        thread_email_sender()
        print "Exiting " + self.name

def send_email_new_item(email_server, FROM, TO_seller, TO_buyer, item_name, item_url):

    SUBJECT_seller = "Parabens, vendeu o item " + item_name
    SUBJECT_buyer = "Parabens, ganhou o item " + item_name
    text_seller = "Voce vendeu o seu item " + item_name + "! \n Pode visitar o item em causa em " + item_url
    text_buyer = "Voce ganhou o item " + item_name + "! \n Pode visitar o item em causa em " + item_url

    try:
        message_seller = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO_seller), SUBJECT_seller, text_seller)
        message_buyer = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO_buyer), SUBJECT_buyer, text_buyer)
        email_server.sendmail(FROM, TO_seller, message_seller)
        email_server.sendmail(FROM, TO_buyer, message_buyer)
        return True
    except smtplib.SMTPRecipientsRefused:
        print 'The email was not sent, the target refused'
        return False
    except smtplib.SMTPServerDisconnected:
        print 'The server is disconnected.'
        return False
    except:
        print 'SHIT HAPPENED DEAL WITH IT'
        return False

def thread_email_sender():
    print "STARTED EMAIL SENDER THREAD!"
    while True:
        email_server = smtplib.SMTP_SSL("smtp.live.com", 25)
        email_server.ehlo()
        email_server.starttls()
        email_server.login("asw_leiloes@hotmail.com", "halflife2")
        conn_thread = mysql.connect()
        cur_thread = conn_thread.cursor()
        cur_thread.execute("SELECT * FROM artigos;")
        auctions = cur_thread.fetchall()
        for auct in auctions:
            if datetime.datetime.today() >= auct[6]:
                if auct[8] != None:
                    if auct[10] == 0:
                        db_utils_flask.set_email_sent(conn_thread, cur_thread, auct[0])
                        cur_thread.execute("SELECT * FROM utilizadores where user_id = %s;", [auct[7]])
                        auct_winner = cur_thread.fetchone()
                        cur_thread.execute("SELECT email from utilizadores where user_id = %s;", [auct[2]])
                        auct_seller = cur_thread.fetchone()[0]

                        if send_email_new_item(email_server, "opskinsemailsender@gmail.com", auct_seller,
                                            auct_winner[5], auct[1], "http://163.172.132.51/leiloes/"+str(auct[0])):
                            db_utils_flask.set_email_sent(conn_thread, cur_thread,auct[0])
                            print "Sent email to buyer " + auct_winner[5]
                            print "Sent email to seller" + auct_seller
        email_server.close()
        conn_thread.close()
        time.sleep(random.randrange(60,120))