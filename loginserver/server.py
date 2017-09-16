from twisted.internet.protocol import Factory, ClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import MD5
import json
import base64
import bcrypt
import pymysql
import random
import string
import time

loginAuthKey = ''#THIS SHOULD BE THE SAME AS SET IN THE GAMESERVER'S GLOBALVARS.PY FILE
GAMESERVER_IP='127.0.0.1' #IP OF THE GAMESERVER
GAMESERVER_PORT=2727
port = 2729
GAME_VERSION='0.1f'
DBHOST='127.0.0.1'
DBUSER='dbuser'
DBPASS='dbpass'
DBNAME='dbname'

global gameServer
ServerPackets = {
    "AskForLoginInformation":0,
    "VersionOutdated":1,
    "LoginWrong":2,
    "PasswordOK":3,
    "Banned":4,
    "GameServerDown":5
}
ClientPackets = {
    "SendLoginInformation":0
}
GameServerPackets = {
    'RequestAuthentication':0,
    'SendClientInfo':1
}
GameClientPackets = {
    'SendAuthentication':0,
    'NewAuthentication':1
}
KEY_LENGTH = 2048
random_gen = Random.new().read
privatekey = RSA.generate(KEY_LENGTH,random_gen)
pubkey = privatekey.publickey().exportKey()

GameServerKey=None
def saveLoginToDb(username,ip_address,success):
    database.sendQuery("INSERT INTO logins (username, ip_address, success, timedate) values (%s, %s, %s, %s);",(username,ip_address,success,time.strftime('%Y-%m-%d %H:%M:%S')))
    database.saveChanges()
def setupDatabase():
    global database
    database = Database()
class Database():
    def __init__(self):
        self.conn = pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASS,db=DBNAME)
        self.cursor = self.conn.cursor()
        self.checkDatabase()
    def checkDatabase(self):
        if self.sendQuery("SHOW TABLES LIKE 'logins'") == 0:
            self.sendQuery("CREATE TABLE logins (id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(20), ip_address VARCHAR(45), success TINYINT(1), timedate DATETIME);")
        self.saveChanges()
    def saveChanges(self):
        self.conn.commit()
    def sendQuery(self, query, *args):
        try:
            return self.cursor.execute(query, *args)
        except Exception, e:
            print Exception, e
class LoginServer():
    def __init__(self):
        factory = clientServerFactory(self)
        reactor.listenTCP(port,factory)
        self.conn = factory.protocol(factory)
        #connectionProtocol = startConnection()
        self.gameConn = None
        self.connectedToGameServer=False
        self.connectToGameServer()
        setupDatabase()
        reactor.run()
    def connectToGameServer(self):
        self.gameConn = TCPConnection(self.startConnection())
    def startConnection(self):
        factory = gameFactory(self)
        reactor.connectTCP(GAMESERVER_IP,GAMESERVER_PORT,factory)
        return factory.protocol
def clean_name(some_var):
    return ''.join(char for char in some_var if char.isalnum())
def loginOK(name,password):
    #name=clean_name(name).title()
    database.saveChanges()
    q = database.sendQuery("SELECT * FROM www_accounts WHERE username = %s", (name))
    rows = database.cursor.fetchone()
    if not rows:
        return False
    if bcrypt.hashpw(password.encode('UTF-8'),rows[2].encode('UTF-8')).decode() != rows[2]:
        return False
    else:
        return True
    
class clientServerProtocol(LineReceiver):
    def __init__(self,factory):
        self.factory=factory
    def connectionMade(self):
        self.factory.clients.append([self,None])
        packet = json.dumps({"p": ServerPackets["AskForLoginInformation"], 'k':pubkey})
        self.sendDataTo(packet,self.findClientIndex(self))
    def closeConnection(self,index):
        self.factory.clients[index][0].transport.loseConnection()
        del self.factory.clients[index]
    def lineReceived(self,data):
        decodedData = base64.b64decode(data)
        index = self.findClientIndex(self)
        jsonData = json.loads(decodedData)
        #print type(decodedData)
        packetType = jsonData["p"]
        if packetType == ClientPackets["SendLoginInformation"]:
            if self.factory.parent.connectedToGameServer==False:
                packet = json.dumps({"p": ServerPackets["GameServerDown"]})
                self.sendDataTo(packet,index)
                self.closeConnection(index)
                return
            if jsonData["v"] != GAME_VERSION:
                packet = json.dumps({"p": ServerPackets["VersionOutdated"]})
                self.sendDataTo(packet,index)
                self.closeConnection(index)
                return
            name = clean_name(base64.b64decode(privatekey.decrypt(base64.b64decode(jsonData["n"])))).title()
            password = base64.b64decode(privatekey.decrypt(base64.b64decode(jsonData["pw"])))
            if len(name)<3 or len(password)<7 or len(name)>12 or len(password)>254:
                packet = json.dumps({"p":ServerPackets["LoginWrong"]})
                self.sendDataTo(packet,index)
                saveLoginToDb(name,self.factory.clients[index][0].transport.client[0],0)
                self.closeConnection(index)
                return
            elif not loginOK(name,password):
                packet = json.dumps({"p":ServerPackets["LoginWrong"]})
                self.sendDataTo(packet,index)
                saveLoginToDb(name,self.factory.clients[index][0].transport.client[0],0)
                self.closeConnection(index)
                
                return
            else:
                randomKey = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
                q = database.sendQuery("SELECT id FROM www_accounts WHERE username = %s", (name))
                id = database.cursor.fetchone()[0]
                serverPacket = json.dumps({"p":GameClientPackets["NewAuthentication"], "k":randomKey, 'ip':self.factory.clients[index][0].transport.client[0],'id':id,'n':name})
                self.factory.clients[index][1]=randomKey
                self.factory.parent.gameConn.sendData(serverPacket)
                
                #packet = json.dumps({"p":ServerPackets["PasswordOK"], "k":randomKey, 'ip':GAMESERVER_IP,'port':GAMESERVER_PORT})
                #self.sendDataTo(packet,index)
                #print "SENT DATA"
                saveLoginToDb(name,self.factory.clients[index][0].transport.client[0],1)
                #print "LOGIN OK", self.factory.clients[index][0].transport.client[0]
                #self.closeConnection(index)
    def sendDataTo(self,data,index):
        encodedData = base64.b64encode(data)
        self.factory.clients[index][0].sendLine(encodedData)
    def findClientIndex(self,protocol=None,key=None):
        for i, client in enumerate(self.factory.clients):
            if (protocol is not None and client[0]==protocol) or (key is not None and client[1]==key):
                return i
class clientServerFactory(Factory):
    protocol = clientServerProtocol
    def __init__(self,parent):
        self.clients = []
        self.parent=parent
    def buildProtocol(self, addr):
        p = self.protocol(self)
        p.factory = self
        return p
class gameProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
    
    def connectionMade(self):
        self.factory.parent.connectedToGameServer=True
    def lineReceived(self,data):
        decodedData = base64.b64decode(data)
        jsonData = json.loads(decodedData)
        packetType = jsonData["p"]
        if packetType == GameServerPackets['RequestAuthentication']:
            GameServerKey = RSA.importKey(jsonData["k"])
            pw = base64.b64encode(GameServerKey.encrypt(loginAuthKey,128)[0])
            packet = json.dumps({"p":GameClientPackets["SendAuthentication"], "k":pw})
            self.factory.parent.gameConn.sendData(packet)
        elif packetType == GameServerPackets["SendClientInfo"]:
            index = self.factory.parent.conn.findClientIndex(key=jsonData["k"])
            if jsonData["ok"]==True:
                self.factory.parent.conn.sendDataTo(json.dumps({"p":ServerPackets["PasswordOK"], "k":jsonData["k"], 'ip':GAMESERVER_IP,'port':GAMESERVER_PORT}),index)
                self.factory.parent.conn.closeConnection(index)
            else:
                self.factory.parent.conn.sendDataTo(json.dumps({"p":ServerPackets["Banned"], "d":jsonData["d"], 'r':jsonData["r"]}),index)
                self.factory.parent.conn.closeConnection(index)
    def sendData(self, data):
        encodedData = base64.b64encode(data)
        self.sendLine(encodedData)
class gameFactory(ClientFactory):
    def __init__(self, parent):
        self.protocol = p = gameProtocol(self)
        self.parent=parent
        
    def startedConnecting(self, connector):
        pass
    def buildProtocol(self, addr):
        return self.protocol
    def clientConnectionFailed(self, connector, reason):
        self.parent.connectedToGameServer=False
        reactor.callLater(1,self.parent.connectToGameServer)
    def clientConnectionLost(self, connector, reason):
        self.parent.connectedToGameServer=False
        print "CONNECTION LOST TO GAME SERVER"
        reactor.callLater(1,self.parent.connectToGameServer)
class TCPConnection():
    def __init__(self, protocol):
        self.protocol = protocol
    def sendData(self, data):
        self.protocol.sendData(data)
loginServer = LoginServer()
        