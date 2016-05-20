import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8081/")

def valorAtual(n):
    return str(proxy.valorAtualDoItem(n))

def licitaItem(id, valor, username, password):
    return str(proxy.licitaItem(id, valor, username, password))

while True:
    
    n = raw_input('Qual o comando? ')
    
    if n == 'exit':
        break

    elif n == "valor":
        id = raw_input("Insira o id do leilao: ")
        try:
            print valorAtual(int(id))
        except TypeError:
            print 'o id esta errado\n'

    elif n == "licitaItem":
        id = raw_input("Insira o id do leilao: ")
        valor = raw_input("Insira o valor da nova bid: ")
        username = raw_input("Insira o seu username: ")
        password = raw_input("Insira a sea password: ")
        try:
            print licitaItem(int(id), float(valor), username, password)
        except TypeError:
            print 'os argumentos estao errados\n'
    else:
        print "Opcao errada! Escolha valorAtualDoItem ou licitaItem\n"


#print "100 e par: %s" % str(proxy.e_par(100))