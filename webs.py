from SimpleXMLRPCServer import SimpleXMLRPCServer
import requests
import json

def valorAtualDoItem(id):

    url = 'http://163.172.132.51/php/valorActualDoItem'

    data = {
        "id":id
    }

    res = requests.post(url, data=json.dumps(data))
    print res.status_code
    print res.content

    return res.content


def licitaItem(id, valor, username, password):

    url = 'http://163.172.132.51/php/licitaItem'

    data = {
        "id":id,
        "valor":valor,
        "username":username,
        "password":password
    }

    res = requests.post(url, json.dumps(data))

    print res.status_code
    print res.content
    return res.content


server = SimpleXMLRPCServer(("localhost", 80))
print "A escuta no porto 8888..."
server.register_function(valorAtualDoItem, "valorAtualDoItem")
server.register_function(licitaItem, "licitaItem")
server.serve_forever()