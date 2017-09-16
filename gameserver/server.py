import time
import base64
import socket
import globalvars as g
import json
from packettypes import *
from objects import *
from datahandler import *
from constants import *
from gamelogic import *
from properties import *
from database import *
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import MD5
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver

dataHandler = None
current_milli_time = lambda: int(round(time.time() * 1000))

def startServer():
    global dataHandler
    dataHandler = DataHandler()
    loadGameData()
    g.loginServerIP = socket.gethostbyname(LOGINSERVERDOMAIN)
    factory = gameServerFactory()
    reactor.listenTCP(2727,factory)
    g.conn = factory.protocol(factory)
    tick = LoopingCall(serverLoop)
    tick.start(1./GAMETICK)
    reactor.run()
def loadGameData():
    g.lastTick = current_milli_time()
    setupDatabase()
    constructClothingPairs()
    constructAbilityList()
    constructMeneList()
    constructAchievementList()
    constructItemList()
    loadMaps()
    loadNPCs()
    loadGuilds()
    loadPlayersFromDb()
    loadIgnores()
    loadFriends()
    loadMutes()
    loadBans()
    loadReports()
    #setupDatabase()
    #loadMenes()
    #loadMaps()
    #loadNpcs()
    #loadGuilds()
class gameServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        
    def connectionMade(self):
        self.transport.setTcpNoDelay(True)
        self.factory.unauthClients.append(unauthorizedConnection(self,g.lastTick))
        unauthIndex=self.findUnauthClientIndex(self)
        if self.transport.client[0]==g.loginServerIP:
            packet = json.dumps({"p":LoginServerPackets.RequestAuthentication, "k":g.publickey})
            self.sendDataToUnauth(packet,unauthIndex)
        else:
            self.factory.unauthClients[unauthIndex].packet.append({"p":ServerPackets.RequestAuth})
            #packet = json.dumps({"p":ServerPackets.RequestAuth})
            #self.sendDataToUnauth(packet,unauthIndex)
    def lineReceived(self,data):
        decodedData = base64.b64decode(data)
        unauthIndex = self.findUnauthClientIndex(self)
        if self == g.loginServer:
            dataHandler.handleLoginServerData(decodedData)
        elif unauthIndex is not None:
            dataHandler.handleUnauthData(unauthIndex,decodedData)
        else:
            dataHandler.handleData(self.findPlayerID(self),decodedData)
    def closeUnauthConnection(self,index):
        self.factory.unauthClients[index].connection.transport.loseConnection()
        del self.factory.unauthClients[index]
    def connectionLost(self,reason):
        clientIndex=self.findUnauthClientIndex(self)
        if clientIndex != None:
            self.closeUnauthConnection(clientIndex)
        elif self == g.loginServer:
            g.loginServer.transport.loseConnection()
            g.loginServer=None
        else:
            ID = self.findPlayerID(self)
            if ID is not None:
                handlePlayerDisconnect(self.findPlayerID(self))
    def sendDataToLoginServer(self,data):
        encodedData = base64.b64encode(data)
        g.loginServer.sendLine(encodedData)
    def sendDataToUnauth(self,data,index):
        encodedData = base64.b64encode(data)
        self.factory.unauthClients[index].connection.sendLine(encodedData)
    def sendData(self,data,id):
        encodedData = base64.b64encode(data)
        Players[id].connection.sendLine(encodedData)
    def findUnauthClientIndex(self,protocol=None):
        for i in range(len(self.factory.unauthClients)):
            if self.factory.unauthClients[i].connection == protocol:
                return i
        return None
    def findPlayerID(self,protocol):
        for id in OnlinePlayers:
            if protocol == Players[id].connection:
                return id
class gameServerFactory(Factory):
    protocol = gameServerProtocol
    def __init__(self):
        self.unauthClients = []
    def buildProtocol(self, addr):
        p = self.protocol(self)
        p.factory = self
        return p
tmr10=0
tmr1=0
def serverLoop():
    
    global tmr10,tmr1
    g.lastTick = current_milli_time()
    if g.lastTick > tmr10:
        kickUnauthClients()
        tmr10 = g.lastTick+1000*10
    if g.lastTick>tmr1:
        updateDatabase()
        tmr1=g.lastTick+1000*5
    checkNPCMoves()
    checkPlayerMoves()
    checkMatches()
    for i in range(len(g.conn.factory.unauthClients)):
        if len(g.conn.factory.unauthClients[i].packet)==0:
            pass
        elif len(g.conn.factory.unauthClients[i].packet)==1:
            g.conn.factory.unauthClients[i].connection.sendDataToUnauth(json.dumps(g.conn.factory.unauthClients[i].packet[0]),i)
            g.conn.factory.unauthClients[i].packet[:]=[]
        else:
            g.conn.factory.unauthClients[i].connection.sendDataToUnauth(json.dumps(g.conn.factory.unauthClients[i].packet),i)
            g.conn.factory.unauthClients[i].packet[:]=[]
    for id in OnlinePlayers:
        for packet in Players[id].tmpPlayer.packet:
            if packet["p"]==ServerPackets.LatencyTick:
                packet["t"]=int(time.time()*1000-Players[id].tmpPlayer.latencyTick)
        if len(Players[id].tmpPlayer.packet)==0:
            pass
        elif len(Players[id].tmpPlayer.packet)==1:
            Players[id].connection.sendData(json.dumps(Players[id].tmpPlayer.packet[0]),id)
            Players[id].tmpPlayer.packet[:]=[]
        else:
            Players[id].connection.sendData(json.dumps(Players[id].tmpPlayer.packet),id)
            Players[id].tmpPlayer.packet[:]=[]

startServer()