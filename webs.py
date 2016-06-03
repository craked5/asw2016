from SimpleXMLRPCServer import SimpleXMLRPCServer
import requests
import json

def valorAtualDoItem(id):

    url = ''

    data = {
        "id":id
    }

    res = requests.post(url, data=json.dumps(data))
    print res.status_code
    print res.content

    return res.content


def licitaItem(id, valor, username, password):

    url = ''

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


server = SimpleXMLRPCServer(("0.0.0.0", 80))
print "A escuta no porto 8888..."
server.register_function(valorAtualDoItem, "valorAtualDoItem")
server.register_function(licitaItem, "licitaItem")
server.serve_forever()