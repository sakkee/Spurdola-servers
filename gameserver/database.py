database=None
import time
import pymysql
from objects import *
from properties import *
from constants import *

def setupDatabase():
    global database
    database=Database()
class Database():
    def __init__(self):
        self.conn = pymysql.connect(host=DBIP,user=DBUSER,passwd=DBPW,db=DBNAME)
        self.cursor = self.conn.cursor()
        self.checkDatabase()
    def checkDatabase(self):
        if self.sendQuery("SHOW TABLES LIKE 'characters'") == 0:
            self.sendQuery("CREATE TABLE characters (id INTEGER PRIMARY KEY AUTO_INCREMENT, \
                                                 wwwID INTEGER, \
                                                 name VARCHAR(15), \
                                                 hat INTEGER, \
                                                 face INTEGER, \
                                                 shirt INTEGER, \
                                                 shoes INTEGER, \
                                                 access INTEGER, \
                                                 map INTEGER, \
                                                 x INTEGER, y INTEGER, \
                                                 direction INTEGER, \
                                                 guildID INTEGER,   \
                                                 guildAccess INTEGER,   \
                                                 money BIGINT,   \
                                                 ES INTEGER);")
        if self.sendQuery("SHOW TABLES LIKE 'user_achievements'") == 0:
            self.sendQuery("CREATE TABLE user_achievements (id INTEGER PRIMARY KEY AUTO_INCREMENT,   \
                                                            charID INTEGER, \
                                                            achievementID INTEGER,  \
                                                            timestamp BIGINT);")
        if self.sendQuery("SHOW TABLES LIKE 'user_menes'") == 0:
            self.sendQuery("CREATE TABLE user_menes (id INTEGER PRIMARY KEY AUTO_INCREMENT, \
                                                     charID INTEGER,    \
                                                     meneID INTEGER,    \
                                                     name VARCHAR(15),  \
                                                     level INTEGER, \
                                                     xp INTEGER,    \
                                                     hp INTEGER,    \
                                                     inventoryType TINYINT);")
        if self.sendQuery("SHOW TABLES LIKE 'guilds'") == 0:
            self.sendQuery("CREATE TABLE guilds (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                guildName VARCHAR(24));")
        if self.sendQuery("SHOW TABLES LIKE 'ignores'") == 0:
            self.sendQuery("CREATE TABLE ignores (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                charID INTEGER, \
                                ignoreID INTEGER);")
        if self.sendQuery("SHOW TABLES LIKE 'friends'") == 0:
            self.sendQuery("CREATE TABLE friends (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                charID INTEGER, \
                                friendID INTEGER);")
        if self.sendQuery("SHOW TABLES LIKE 'admincommands'") == 0:
            self.sendQuery("CREATE TABLE admincommands (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                adminID INTEGER, \
                                timedate DATETIME,  \
                                command VARCHAR(64),   \
                                targetID INTEGER,   \
                                length BIGINT,  \
                                msg TEXT);")
                                
        if self.sendQuery("SHOW TABLES LIKE 'mutes'") == 0:
            self.sendQuery("CREATE TABLE mutes (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                                 mutedID INTEGER, \
                                                 endingTime BIGINT, \
                                                 adminID INTEGER, \
                                                 reason VARCHAR(128));") 
        if self.sendQuery("SHOW TABLES LIKE 'bans'") == 0:
            self.sendQuery("CREATE TABLE bans (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                                 charID INTEGER, \
                                                 endingTime BIGINT, \
                                                 adminID INTEGER, \
                                                 reason VARCHAR(200), \
                                                 minutes INTEGER,   \
                                                 timedate DATETIME);") 
        if self.sendQuery("SHOW TABLES LIKE 'reports'") == 0:
            self.sendQuery("CREATE TABLE reports (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                charID INTEGER, \
                                reportText TEXT, \
                                timedate DATETIME);")
                                
        if self.sendQuery("SHOW TABLES LIKE 'mails'") == 0:
            self.sendQuery("CREATE TABLE mails (id INT(8) PRIMARY KEY AUTO_INCREMENT, \
                                charID INTEGER, \
                                mailText TEXT, \
                                senderID INTEGER,   \
                                timestamp BIGINT);")

    def saveChanges(self):
        self.conn.commit()
    def sendQuery(self, query, *args):
        try:
            return self.cursor.execute(query, *args)
        except Exception, e:
            print Exception, e

def getReportByCharID(charID):
    for report in Reports:
        if report.charID==charID:
            return report
    return None
def getReportText(ID):
    for report in Reports:
        if report.charID==ID:
            return report.text
    return None
def getFirstReport():
    if len(Reports)>0:
        return Reports[0]
    return None
def loadMails():
    q = database.sendQuery("SELECT * FROM mails")
    rows = database.cursor.fetchall()
    for row in rows:
        Mails[row[0]]=Mail(row[0],charID=row[1],text=row[2],senderID=row[3],timestamp=row[4])
def loadReports():
    q = database.sendQuery("SELECT * FROM reports")
    rows = database.cursor.fetchall()
    for row in rows:
        Reports.append(Report(charID=row[1],text=row[2]))
def loadBans():
    q = database.sendQuery("SELECT * FROM bans")
    rows = database.cursor.fetchall()
    for row in rows:
        if g.lastTick < row[2]:
            Bans.append(Ban(charID=row[1],endingTime=row[2],reason=row[4]))
  
def loadMutes():
    q = database.sendQuery("SELECT * FROM mutes")
    rows = database.cursor.fetchall()
    for row in rows:
        if g.lastTick < row[2]:
            Mutes.append(Mute(charID=row[1],endingTime=row[2],reason=row[4]))
def getPlayerBan(ID):
    for i in xrange(len(Bans)):
        if Bans[i].charID==ID and g.lastTick < Bans[i].endingTime:
            return i
    return None
def getGuildID(guildName):
    for id, guild in Guilds.iteritems():
        if guild.name.lower()==guildName.lower():
            return id
    return None
def loadGuilds():
    q = database.sendQuery("SELECT * FROM guilds")
    rows = database.cursor.fetchall()
    for row in rows:
        Guilds[row[0]]=Guild(name=unicode(row[1],'ISO-8859-1'),id=row[0])
def loadPlayersFromDb():
    q = database.sendQuery("SELECT * FROM characters")
    rows = database.cursor.fetchall()
    for row in rows:
        Players[row[0]]=Player(name=row[2],id=row[0],wwwID=row[1],hat=row[3],face=row[4],shirt=row[5],shoes=row[6],access=row[7],map=row[8],x=row[9],y=row[10],dir=row[11],guildID=row[12],guildAccess=row[13],money=row[14],ES=row[15])
        if row[12]!=None:
            Guilds[row[12]].members.append(GuildMember(charID=row[0],guildAccess=row[13]))
        q1 = database.sendQuery("SELECT * FROM user_achievements WHERE charID=%s",(row[0]))
        rows1=database.cursor.fetchall()
        for r1 in rows1:
            Players[row[0]].achievements.append(r1[2])
        q2 = database.sendQuery("SELECT * FROM user_menes WHERE charID=%s",(row[0]))
        rows2 = database.cursor.fetchall()
        for r2 in rows2:
            meneStats = getMeneStats(level=r2[4],meneID=r2[2])
            Players[row[0]].menes.append(PlayerMene(playerMeneID=r2[0],meneID=r2[2],name=unicode(r2[3],'ISO-8859-1'),level=r2[4],xp=r2[5],hp=r2[6],inventoryType=r2[7],hpmax=meneStats["hp"],power=meneStats["power"],defense=meneStats["defense"],speed=meneStats["speed"]))
def loadIgnores():
    q = database.sendQuery("SELECT * FROM ignores")
    rows = database.cursor.fetchall()
    for row in rows:
        Players[row[1]].ignoreList.append(row[2])
def loadFriends():
    q = database.sendQuery("SELECT * FROM friends")
    rows = database.cursor.fetchall()
    for row in rows:
        Players[row[1]].friendList.append(row[2])
     
def deleteReportFromDb(charID):
    query = database.sendQuery("DELETE FROM reports WHERE charID=%s;",\
                                                                (charID))    
def updateReportDb(charID,reportText,timedate):
    query = database.sendQuery("UPDATE reports SET reportText=%s, timedate=%s WHERE charID=%s;",\
                                                                (reportText, timedate,charID))                                                      
def insertReportToDb(charID,reportText,timedate):
    query = database.sendQuery("INSERT INTO reports (charID, reportText, timedate) VALUES (%s, %s, %s);",\
                                                                (charID, reportText,timedate))
def insertAchievementToDb(charID,achievementID,timestamp):
    query = database.sendQuery("INSERT INTO user_achievements (charID, achievementID, timestamp) VALUES (%s, %s, %s);",\
                                                                (charID, achievementID,timestamp))

def insertMeneToDb(meneID,charID,name,level,xp,hp,inventoryType):
    query = database.sendQuery("INSERT INTO user_menes (charID, meneID, name, level, xp, hp, inventoryType) VALUES (%s, %s, %s, %s, %s, %s, %s);",\
                                                                (charID, meneID,name,level,xp,hp,inventoryType))
    return database.cursor.lastrowid
def insertIgnoreToDb(charID,ignoreID):
    query = database.sendQuery("INSERT INTO ignores (charID, ignoreID) VALUES (%s, %s);",\
                                                                (charID, ignoreID))
def removeIgnoreFromDb(charID,ignoreID):
    query = database.sendQuery("DELETE FROM ignores WHERE charID=%s AND ignoreID=%s;",\
                                                                (charID, ignoreID))
                                                                
def insertFriendToDb(charID,friendID):
    query = database.sendQuery("INSERT INTO friends (charID, friendID) VALUES (%s, %s);",\
                                                                (charID, friendID))
def removeFriendFromDb(charID,friendID):
    query = database.sendQuery("DELETE FROM friends WHERE charID=%s AND friendID=%s;",\
                                                                (charID, friendID))
def getGuildMemberListIndex(charID,guildID):
    for i in xrange(len(Guilds[guildID].members)):
        if Guilds[guildID].members[i].charID==charID:
            return i
    return None
def isMeneDead(matchID):
    if Matches[matchID].playerMene.hp<=0 or Matches[matchID].npcMene.hp<=0:
        return True
    return False
def isPlayerOnline(name):
    for ID in OnlinePlayers:
        if Players[ID].name == name:
            return True
    return False
def isPlayerOnlineID(ID):
    if ID in OnlinePlayers:
        return True
    return False
def getPlayerOnlineId(name):
    for ID in OnlinePlayers:
        if Players[ID].name == name:
            return ID
    return None
def removeBanFromDb(charID,endingTime):
    query = database.sendQuery("DELETE FROM bans WHERE charID=%s AND endingTime>=%s;", (charID,endingTime))
def insertBanToDb(charID,endingTime,reason,adminID,minutes,timedate):
    query = database.sendQuery("INSERT INTO bans (charID, endingTime, adminID, reason, minutes, timedate) VALUES (%s, %s, %s, %s, %s, %s);", (charID,endingTime,adminID,reason,minutes,timedate))
def insertMuteToDb(charID,endingTime,reason,adminID):
    query = database.sendQuery("INSERT INTO mutes (mutedID, endingTime, adminID, reason) VALUES (%s, %s, %s, %s);", (charID,endingTime,adminID,reason))
def deleteMuteFromDb(charID):
    query = database.sendQuery("DELETE FROM mutes WHERE mutedID=%s;", (charID))
def insertAdminCommandToDb(adminID,timedate,command,targetID,length,msg):
    query = database.sendQuery("INSERT INTO admincommands (adminID, timedate, command, targetID, length, msg) VALUES (%s, %s, %s, %s, %s, %s);", (adminID,timedate,command,targetID,length,msg))
def saveAdminCommand(ID,command,target=None,length=None,msg=""):
    tmpTime = time.strftime('%Y-%m-%d %H:%M:%S')
    DatabaseSavings["admincommands"].append({"adminID":ID,"timedate":tmpTime,"command":command,"target":target,"length":length,"msg":msg})
    
def leaveGuild(charID):
    gID = Players[charID].guildID
    del Guilds[gID].members[getGuildMemberListIndex(charID,gID)]
    if len(Guilds[gID].members)==0:
        q = database.sendQuery("DELETE FROM guilds WHERE id=%s",(gID))
    setPlayerGuild(charID,None)
    setPlayerGuildAccess(charID,GUILD_MEMBER)
def createGuild(name,id):
    q = database.sendQuery("INSERT INTO guilds (guildName) VALUES (%s);",(name))
    guildID = database.cursor.lastrowid
    Guilds[guildID]=Guild(id=guildID,name=name)
    Guilds[guildID].members.append(GuildMember(charID=id,guildAccess=GUILD_OWNER,online=True))
    Players[id].guildID=guildID
    Players[id].guildAccess=GUILD_OWNER
def changeGuildMemberAccess(charID,gID,access):
    Players[charID].guildAccess=access
    Guilds[gID].members[getGuildMemberListIndex(charID,gID)].guildAccess=access
def insertPlayerToDb(wwwID,name):
    emptyPlayer = Player(wwwID=wwwID,name=name)
    query = database.sendQuery("INSERT INTO characters (wwwID, name, hat, face, shirt, shoes, access, map, x, y, direction) \
                                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", \
                                                     (wwwID,                \
                                                      name,     \
                                                      emptyPlayer.hat,      \
                                                      emptyPlayer.face,     \
                                                      emptyPlayer.shirt,    \
                                                      emptyPlayer.shoes,    \
                                                      emptyPlayer.access,   \
                                                      emptyPlayer.map,      \
                                                      emptyPlayer.x,        \
                                                      emptyPlayer.y,        \
                                                      emptyPlayer.dir))
    id = database.cursor.lastrowid
    database.saveChanges()
    emptyPlayer.id=id
    Players[id] = emptyPlayer
    return id
def getGuildName(gID):
    if gID is None:
        return None
    else:
        return Guilds[gID].name
def isFighting(ID):
    if Players[ID].tmpPlayer.fighting is not None:
        return True
    return False
def getPlayerId(wwwID=None,name=None,guildID=None):
    if wwwID is not None:
        for id in Players:
            if Players[id].wwwID==wwwID:
                return id
    elif guildID is not None and name is not None:
        for guildMember in Guilds[guildID].members:
            if getPlayerName(guildMember.charID) == name:
                return guildMember.charID
    elif name is not None:
        for id, player in Players.iteritems():
            if player.name==name:
                return id
    return None
    
def hasMenesAlive(ID):
    for mene in getPlayerMenes(ID):
        if mene.hp>0:
            return True
    return False
def playerHasMene(ID,meneID):
    for mene in getPlayerMenes(ID):
        if mene.meneID==meneID:
            return True
    return False
def getPlayerMene(ID,meneID):
    for mene in getPlayerMenes(ID):
        if mene.playerMeneID==meneID:
            return mene
    return None
def getPlayerMenes(ID):
    return Players[ID].menes
def getPlayerDefaultMene(ID):
    for mene in Players[ID].menes:
        if mene.inventoryType==1:
            return mene
    return None
def getPlayerMatch(ID):
    return Players[ID].tmpPlayer.fighting
def getMeneStats(level=1,meneID=None,npc=False):
    tmpMene = getMene(meneID)
    power = calculateStat(level,tmpMene.power,npc)
    defense = calculateStat(level,tmpMene.defense,npc)
    speed = calculateStat(level,tmpMene.speed,npc)
    hp = calculateHP(level,tmpMene.hp,npc)
    xp = calculateXpNeeded(level)
    return {"power":power,"defense":defense,"speed":speed,"hp":hp, "xp":xp}
def getNpcListIndex(npcName,mapID):
    for i in xrange(len(Maps[mapID].npcs)):
        if Maps[mapID].npcs[i].name==npcName:
            return i
    return None
def getPlayerName(id=None):
    if id is not None:
        return Players[id].name
        
def getPlayerMoney(ID):
    return Players[ID].money
def addPlayerMoney(ID,money):
    Players[ID].money+=money
def lowerPlayerMoney(ID,money):
    Players[ID].money-=money
    if Players[ID].money<0:
        Players[ID].money=0
def addPlayerES(ID):
    Players[ID].ES+=1
def lowerPlayerES(ID):
    if Players[ID].ES<=0:
        return
    Players[ID].ES-=1
def getPlayerES(ID):
    return Players[ID].ES
def getPlayerHat(id):
    return Players[id].hat
def setPlayerHat(id,hat):
    Players[id].hat=hat
def getPlayerShirt(id):
    return Players[id].shirt
def setPlayerShirt(id,shirt):
    Players[id].shirt=shirt
def getPlayerFace(id):
    return Players[id].face
def setPlayerFace(id,face):
    Players[id].face=face
def getPlayerShoes(id):
    return Players[id].shoes
def setPlayerShoes(id,shoes):
    Players[id].shoes=shoes
def getPlayerGuild(id):
    return Players[id].guildID
def setPlayerGuild(id,guildID):
    Players[id].guildID=guildID
def getPlayerGuildAccess(id):
    return Players[id].guildAccess
def setPlayerGuildAccess(id,guildAccess):
    Players[id].guildAccess=guildAccess
def getPlayerMap(id):
    return Players[id].map
def setPlayerMap(id,mapID):
    #leaveOldMap(id)
    Players[id].map=mapID
    #joinNewMap(id)
def joinNewMap(ID):
    mapID=getPlayerMap(ID)
    if ID not in Maps[mapID].players:
        Maps[mapID].players.append(ID)
def leaveOldMap(ID):
    mapID = getPlayerMap(ID)
    if ID in Maps[mapID].players:
        del Maps[mapID].players[Maps[mapID].players.index(ID)]
def getPlayerX(id):
    return Players[id].x
def setPlayerX(id,x):
    Players[id].x=x
def getPlayerY(id):
    return Players[id].y
def setPlayerY(id,y):
    Players[id].y=y
def getPlayerDir(id):
    return Players[id].dir
def setPlayerDir(id,dir):
    Players[id].dir=dir
def setPlayerParty(ID, partyID):
    Players[ID].tmpPlayer.partyID = partyID
def getPlayerParty(ID):
    return Players[ID].tmpPlayer.partyID
def getPlayerPartyAccess(ID):
    if Parties[Players[ID].tmpPlayer.partyID].ownerID==ID:
        return True
    return False
def getPlayerAccess(id):
    return Players[id].access
def setPlayerAccess(id,access):
    Players[id].access=access
def getPlayerIgnores(ID):
    return Players[ID].ignoreList
def getPlayerIgnore(charID,ignoreID):
    if ignoreID in Players[charID].ignoreList:
        return True
    return False
    
def getPlayerMuteReason(ID):
    return Mutes[getMuteListIndex(ID)].reason
def getMuteListIndex(charID):
    for i in xrange(len(Mutes)):
        if Mutes[i].charID==charID:
            return i
    return None
def setPlayerMute(charID,muted,minutes=None,reason=None,adminID=None):
    if muted:
        endingTime = minutes*60*1000+g.lastTick
        Players[charID].tmpPlayer.muted=endingTime
        Mutes.append(Mute(charID,endingTime,reason))
        savePlayerMute(charID,endingTime,reason,adminID)
    else:
        Players[charID].tmpPlayer.muted=None
        del Mutes[getMuteListIndex(charID)]
        removePlayerMute(charID)

def removePlayerBan(charID):
    DatabaseSavings["bans"].append({"charID":charID,'endingTime':g.lastTick,"queryType":"delete"})
    for ban in reversed(Bans):
        if ban.charID==charID and ban.endingTime>g.lastTick:
            Bans.remove(ban)
def savePlayerBan(charID,minutes,reason,ID):
    endingTime=minutes*60*1000+g.lastTick
    DatabaseSavings["bans"].append({"charID":ID,"minutes":minutes,"adminID":ID,"endingTime":endingTime,"reason":reason,'timedate':time.strftime('%Y-%m-%d %H:%M:%S'),"queryType":"insert"})
    Bans.append(Ban(charID=charID,endingTime=endingTime,reason=reason))
def setPlayerIgnore(ID,ignoreID):
    Players[ID].ignoreList.append(ignoreID)
    DatabaseSavings["ignores"].append({"charID":ID,"ignoreID":ignoreID,"queryType":"insert"})
def removePlayerIgnore(ID,ignoreID):
    del Players[ID].ignoreList[Players[ID].ignoreList.index(ignoreID)]
    DatabaseSavings["ignores"].append({"charID":ID,"ignoreID":ignoreID,"queryType":"delete"})
    
def setPlayerFriend(ID,friendID):
    Players[ID].friendList.append(friendID)
    DatabaseSavings["friends"].append({"charID":ID,"friendID":friendID,"queryType":"insert"})
def removePlayerFriend(ID,friendID):
    del Players[ID].friendList[Players[ID].friendList.index(friendID)]
    DatabaseSavings["friends"].append({"charID":ID,"friendID":friendID,"queryType":"delete"})
    
def getPlayerFriend(charID,friendID):
    if friendID in Players[charID].friendList:
        return True
    return False
def getMene(id=None,spriteName=None):
    if id is not None:
        return Menes[id]
    else:
        return Menes[getMeneId(spriteName=spriteName)]
def doesPlayerHaveMene(charID,meneID):
    for mene in Players[charID].menes:
        if mene.meneID == meneID:
            return True
    return False
    
def insertMailToDb(charID,senderID,message,timestamp):
    query = database.sendQuery("INSERT INTO mails (charID, mailText, senderID, timestamp) VALUES (%s, %s, %s, %s);", (charID,message,senderID,timestamp))
    return database.cursor.lastrowid
def deleteMailFromDb(mailID):
    query = database.sendQuery("DELETE FROM mails WHERE id=%s;", (mailID))

def deleteMail(mailID):
    DatabaseSavings["mails"].append({"mailID":mailID,"queryType":'delete'})
    del Mails[mailID]
def saveMail(receiveID,senderID,message):
    timestamp = g.lastTick
    ID = insertMailToDb(receiveID,senderID,message,timestamp)
    Mails[ID]=Mail(ID,charID=receiveID,text=message,senderID=senderID,timestamp=timestamp)
def markReportSolved(report):
    DatabaseSavings["reports"].append({"charID":report.charID,"queryType":"delete"})
    Reports.remove(report)
def saveReport(ID,text):
    if getReportText(ID) is None and text!="":
        DatabaseSavings["reports"].append({"charID":ID,"reportText":text,"timedate":time.strftime('%Y-%m-%d %H:%M:%S'),'queryType':'insert'})
        Reports.append(Report(charID=ID,text=text))
    elif text!="":
        DatabaseSavings["reports"].append({"charID":ID,"reportText":text,"timedate":time.strftime('%Y-%m-%d %H:%M:%S'),'queryType':'update'})
        for report in Reports:
            if report.charID==ID:
                report.text=text
    else:
        DatabaseSavings["reports"].append({"charID":ID,'queryType':'delete'})
        for report in reversed(Reports):
            if report.charID==ID:
                Reports.remove(report)
def removePlayerMute(charID):
    DatabaseSavings["mutes"].append({"charID":charID,"queryType":'delete'})
def savePlayerMute(charID,endingTime,reason,adminID):
    DatabaseSavings["mutes"].append({"charID":charID,"endingTime":endingTime,"reason":reason,"adminID":adminID,'queryType':'insert'})
    
def savePlayerMene(charID,meneID,name,level,inventoryType,meneStats):
    id = insertMeneToDb(meneID,charID,name,level,meneStats["xp"],meneStats["hp"],inventoryType)
    Players[charID].menes.append(PlayerMene(playerMeneID=id,meneID=meneID,name=name,level=level,xp=meneStats["xp"],hp=meneStats["hp"],hpmax=meneStats["hp"],inventoryType=inventoryType,power=meneStats["power"],defense=meneStats["defense"],speed=meneStats["speed"]))
def setPlayerAchievement(charID,achievementID):
    if achievementID not in Players[charID].achievements:
        Players[charID].achievements.append(achievementID)
        DatabaseSavings["achievements"].append({"charID":charID,"achievementID":achievementID,"timestamp":time.time()*1000,"queryType":"insert"})
def updateCharacterInDb(charID):
    query = database.sendQuery("""UPDATE characters SET hat=%s,
                                                  face=%s,
                                                  shirt=%s,
                                                  shoes=%s,
                                                  map=%s,
                                                  x=%s,
                                                  y=%s,
                                                  access=%s,
                                                  direction=%s,
                                                  guildID=%s,
                                                  guildAccess=%s,
                                                  money=%s,
                                                  ES=%s
                                                  WHERE id=%s;""", (getPlayerHat(charID),        \
                                                                       getPlayerFace(charID),     \
                                                                       getPlayerShirt(charID),    \
                                                                       getPlayerShoes(charID),    \
                                                                       getPlayerMap(charID),      \
                                                                       getPlayerX(charID),        \
                                                                       getPlayerY(charID),        \
                                                                       getPlayerAccess(charID),   \
                                                                       getPlayerDir(charID),      \
                                                                       getPlayerGuild(charID),    \
                                                                       getPlayerGuildAccess(charID),    \
                                                                       getPlayerMoney(charID),  \
                                                                       getPlayerES(charID), \
                                                                       charID))
   
    for mene in getPlayerMenes(charID):
        query = database.sendQuery("""UPDATE user_menes SET level=%s,
                                                            xp=%s,
                                                            hp=%s
                                                            WHERE id=%s;""", (mene.level,
                                                                                                mene.xp,
                                                                                                mene.hp,
                                                                                                mene.playerMeneID)
                                                            )
    
def updateDatabase():
    for charID in DatabaseSavings["players"]:
        updateCharacterInDb(charID)
    DatabaseSavings["players"][:]=[]
    for id in OnlinePlayers:
        DatabaseSavings["players"].append(id)
    for achievement in DatabaseSavings["achievements"]:
        insertAchievementToDb(achievement["charID"],achievement["achievementID"],achievement["timestamp"])
    DatabaseSavings["achievements"][:]=[]
    for ignore in DatabaseSavings["ignores"]:
        if ignore["queryType"]=="insert":
            insertIgnoreToDb(ignore["charID"],ignore["ignoreID"])
        elif ignore["queryType"]=='delete':
            removeIgnoreFromDb(ignore["charID"],ignore["ignoreID"])
    DatabaseSavings["ignores"][:]=[]
    for friend in DatabaseSavings["friends"]:
        if friend["queryType"]=="insert":
            insertFriendToDb(friend["charID"],friend["friendID"])
        elif friend["queryType"]=='delete':
            removeFriendFromDb(friend["charID"],friend["friendID"])
    DatabaseSavings["friends"][:]=[]
    for mute in DatabaseSavings["mutes"]:
        if mute["queryType"]=='insert':
            insertMuteToDb(mute["charID"],mute["endingTime"],mute["reason"],mute["adminID"])
        elif mute["queryType"]=='delete':
            deleteMuteFromDb(mute["charID"])
    DatabaseSavings["mutes"][:]=[]
    for admincommand in DatabaseSavings["admincommands"]:
        insertAdminCommandToDb(admincommand["adminID"],admincommand["timedate"],admincommand["command"],admincommand["target"],admincommand["length"],admincommand["msg"])
    DatabaseSavings["admincommands"][:]=[]
    for ban in DatabaseSavings["bans"]:
        if ban["queryType"]=='insert':
            insertBanToDb(ban["charID"],ban["endingTime"],ban["reason"],ban["adminID"],ban["minutes"],ban["timedate"])
        elif ban['queryType']=='delete':
            removeBanFromDb(ban["charID"],ban["endingTime"])
    DatabaseSavings["bans"][:]=[]
    for report in DatabaseSavings["reports"]:
        if report["queryType"]=='insert':
            insertReportToDb(report["charID"],report["reportText"],report["timedate"])
        elif report["queryType"]=='update':
            updateReportDb(report["charID"],report["reportText"],report["timedate"])
        elif report["queryType"]=='delete':
            deleteReportFromDb(report["charID"])
    DatabaseSavings["reports"][:]=[]
    for mail in DatabaseSavings["mails"]:
        if mail["queryType"]=='delete':
            deleteMailFromDb(mail["mailID"])
    DatabaseSavings["mails"][:]=[]
    database.saveChanges()







    DatabaseSavings["mails"][:]=[]
    