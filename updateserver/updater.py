from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
import os
import hashlib
import time
import json
import base64
import copy
import sys
from numbers import Number
from collections import Set, Mapping, deque
dataHandler = None
originalList={}
lists=[{}]
secondList= {'data':None}
currTick = None
conn=None
current_milli_time = lambda: int(round(time.time() * 1000)) #print current_milli_time()
ignores=['updater.py','updater.pyc', "README.txt"]
currentList=0
#secondRound=['default','theme']
ServerPackets = {
"SendHashes":1,
"SendFileInfo":2,
"DownloadFinished":3,
"DownloadSize":4
}
ClientPackets = {
    "SendHashes":1,
    "Received":2,
    "Validating":3
}
counting=0

try: # Python 2
    zero_depth_bases = (basestring, Number, xrange, bytearray)
    iteritems = 'iteritems'
except NameError: # Python 3
    zero_depth_bases = (str, bytes, Number, range, bytearray)
    iteritems = 'items'

def getsize(obj_0):
    """Recursively iterate to sum size of object & members."""
    def inner(obj, _seen_ids = set()):
        obj_id = id(obj)
        if obj_id in _seen_ids:
            return 0
        _seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, zero_depth_bases):
            pass # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, Set, deque)):
            size += sum(inner(i) for i in obj)
        elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
            size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, '__dict__'):
            size += inner(vars(obj))
        if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
            size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
        return size
    return inner(obj_0)
def removeEmptyDicts(dic):
    def removeEmpties(dic2, keys):
        for k, v in dic2.iteritems():
            if isinstance(v, basestring):
                pass
            elif isinstance(v,dict):
                if len(v)==0:
                    asd=keys+[k]
                    del reduce(lambda a,b:a[b],asd[:-1],dic)[asd[-1]]
                else:
                    removeEmpties(v,keys+[k])
    n=0
    while n < 10:
        removeEmpties(copy.deepcopy(dic),[])
        n+=1
def read_bytes_from_file(file, chunk_size = 8000):
    """ Read bytes from a file in chunks. """
    
    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if chunk:
                    yield chunk
            else:
                break
def startServer():
    global dataHandler, currTick
    currTick = current_milli_time()
    factory = gameServerFactory()
    reactor.listenTCP(2728,factory)
    conn = factory.protocol(factory)
    loadData()
    #dataHandler = DataHandler()
    #loadGameData()
   
    #tick = LoopingCall(serverLoop)
    #tick.start(1./GAMETICK)
    reactor.run()
def setDictValue(dict,args, value):
    if args[0] not in dict:
        dict[args[0]]={}
    if len(args)>1:
        setDictValue(dict[args[0]], args[1:], value)
    else:
        dict[args[0]]=value
def getDictValue(dict, args):
    if args[0] not in dict:
        dict[args[0]]={}
    if len(args)>1:
        return getDictValue(dict[args[0]], args[1:])
    else:
        return dict[args[0]]
def loadData():
    def checkFiles(argument,first=False):
        global counting, lists, currentList
        for f1 in os.listdir(argument):
            if f1  not in ignores:
                counting+=sys.getsizeof(f1)
                if os.path.isdir(argument+'/'+f1):
                    if not first:
                        args=argument.split('/')[1:]+[f1]
                        setDictValue(lists[currentList],args,{})
                        nothing = getDictValue(lists[currentList],args)
                        #dict[f1]={}
                        #checkFiles(argument+'/'+f1,dict[f1])
                        checkFiles(argument+'/'+f1)
                    else:
                        lists[currentList][f1]={}
                        #dict[f1]={}
                        checkFiles(f1)
                else:
                    if len(argument)>1:
                        args=argument.split('/')[1:]+[f1]
                    else:
                        args=[f1]
                    #print lists[currentList]
                    #print hashlib.md5(open(argument+'/'+f1,'rb').read()).hexdigest()[:4]
                    setDictValue(lists[currentList],args,hashlib.md5(open(argument+'/'+f1,'rb').read()).hexdigest()[:4])
                    #dict[f1]=hashlib.md5(open(argument+'/'+f1,'rb').read()).hexdigest()[:4]
                    #counting+=sys.getsizeof(f1)+sys.getsizeof(dict[f1])
                    counting+=sys.getsizeof(f1)+sys.getsizeof(getDictValue(lists[currentList],args))
                    if counting>50000:
                        currentList+=1
                        lists.append({})
                        counting=0
                    #print counting
                    #print argument
        #return dict
    #global originalList
    #global secondList
    checkFiles(".")
    #print lists[1]
    #secondList["data"]={'theme':originalList["data"]["theme"],'themes':originalList["data"]["themes"]}
    #del originalList["data"]["theme"]
    #del originalList["data"]["themes"]
    #print getsize(originalList)
    #secondList = checkFiles(".",secondList,[],2)
def getFilePath(args):
    filepath = ''
    a=0
    for i in args:
        if a==0:
            filepath=i
        else:
            filepath+='/'+i
        a+=1
    return filepath
class gameServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append([self,0,{},0,0])
        #print originalList
        global lists
        packet = json.dumps([{"p": ServerPackets["SendHashes"], 'd':lists[0], 'r':2,'c':1,'v':0}])
        self.sendDataTo(packet,self.findClientIndex(self))
    def connectionLost(self,reason):
        index=self.findClientIndex(self)
        self.factory.clients[index][0].transport.loseConnection()
        del self.factory.clients[index]
    def sendFiles(self,index,dic,keys):
        for k, v in dic.iteritems():
            if isinstance(v, dict):
                self.sendFiles(index,v,keys+[k])
            elif not self.factory.clients[index][1]:
                self.factory.clients[index][1]=True
                asd=keys+[k]
                self.setLineMode()
                packet = json.dumps([{"p":ServerPackets["SendFileInfo"],"d":asd,"h":v}])
                #self.setRawMode()
                self.sendDataTo(packet,index)
                self.setRawMode()
                filepath = getFilePath(asd)
                try:
                    for bytes in read_bytes_from_file(filepath):
                        self.factory.clients[index][0].transport.write(bytes)
                except Exception, e:
                    print str(e)
                self.factory.clients[index][0].transport.write('\r\n')
                self.setLineMode()
                del reduce(lambda a, b: a[b], asd[:-1],  self.factory.clients[index][2])[asd[-1]]
                #print "DELETED, BREAKING"
                break
    def checkFileSizes(self,index):
        def iterateFileSizes(dic,keys):
            for k, v in dic.iteritems():
                if isinstance(v, dict):
                    iterateFileSizes(v,keys+[k])
                else:
                    self.factory.clients[index][3]+=os.path.getsize(getFilePath(keys+[k]))
        iterateFileSizes(self.factory.clients[index][2],[])
        packet = json.dumps([{"p":ServerPackets["DownloadSize"], 'd':self.factory.clients[index][3]}])
        self.sendDataTo(packet,index)
        #print self.factory.clients[index][3]
    def lineReceived(self,data):
        
        decodedData = base64.b64decode(data)
        index=self.findClientIndex(self)
        jsonData = json.loads(decodedData)
        packetType=jsonData[0]["p"]
        global lists, currentList
        if packetType==ClientPackets["SendHashes"]:
            
            self.factory.clients[index][2]=jsonData[0]["d"]
            self.checkFileSizes(index)
            self.sendFiles(index,jsonData[0]["d"],[])
        elif packetType == ClientPackets["Received"]:
            self.factory.clients[index][1]=False
            #print "RECEIVED!!!"
            self.sendFiles(index,self.factory.clients[index][2],[])
            #print self.factory.clients[index][2]
            #self.setLineMode()
            #print jsonData
            removeEmptyDicts(self.factory.clients[index][2])
            global currentList
            if len(self.factory.clients[index][2])==0 and self.factory.clients[index][4]==currentList:
                packet = json.dumps([{"p":ServerPackets["DownloadFinished"]}])
                #print "NYTTTTT"
                self.sendDataTo(packet,index)
            
            elif len(self.factory.clients[index][2])==0 and self.factory.clients[index][4]<currentList:
                self.factory.clients[index][4]+=1
                packet = json.dumps([{"p": ServerPackets["SendHashes"], 'd':lists[self.factory.clients[index][4]],'r':2,'c':2,'v':0}])
                self.sendDataTo(packet,index)
        elif packetType==ClientPackets["Validating"]:
            packet = json.dumps([{"p": ServerPackets["SendHashes"], 'd':lists[self.factory.clients[index][4]],'r':2,'c':1,'v':1}])
            self.sendDataTo(packet,index)
        #dataHandler.handleData(self.findClientIndex(self),decodedData)
    def sendDataTo(self,data,index):
        encodedData = base64.b64encode(data)
        self.factory.clients[index][0].sendLine(encodedData)
        #print data
    def findClientIndex(self,protocol):
        for i, client in enumerate(self.factory.clients):
            if client[0]==protocol:
                return i
class gameServerFactory(Factory):
    protocol = gameServerProtocol
    def __init__(self):
        self.clients = []
    def buildProtocol(self, addr):
        p = self.protocol(self)
        p.factory = self
        return p
startServer()