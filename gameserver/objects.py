class unauthorizedConnection():
    def __init__(self,connection,time):
        self.connection=connection
        self.time=time
        self.packet=[]
        
class authToken():
    def __init__(self,token,ip,username,wwwID):
        self.token=token
        self.ip=ip
        self.username=username
        self.wwwID=wwwID
class Achievement():
    def __init__(self,id=None,name=None,info=None):
        self.id=id
        self.name=name
        self.info=info
class Menemon():
    def __init__(self,id=None,name=None,hp=1,hpmax=1,xp=0,level=1,power=1,defense=1,speed=1,spriteName=None,attack1=None,attack2=None,attack3=None,attack4=None):
        self.id=id
        self.name=name
        self.hp=hp
        self.power=power
        self.defense=defense
        self.speed=speed
        self.spriteName=spriteName
        self.attack1=attack1
        self.attack2=attack2
        self.attack3=attack3
        self.attack4=attack4
        self.hpmax=hpmax
        self.xp=xp
        self.level=level
class PlayerMene():
    def __init__(self,meneID=None,name=None,hp=1,hpmax=1,xp=1,level=1,power=1,defense=1,speed=1,playerMeneID=None,inventoryType=1):
        self.meneID=meneID
        self.name=name
        self.hp=hp
        self.hpmax=hpmax
        self.xp=xp
        self.level=level
        self.power=power
        self.defense=defense
        self.speed=speed
        self.playerMeneID=playerMeneID
        self.inventoryType=inventoryType
class Ability():
    def __init__(self,id=None,name="",infotext="",length=1,targetType=1,missChance=0,critChance=10,targetFactor=0,abilityType=0,power=1,spriteName="",animation=""):
        self.id=id
        self.name=name
        self.infotext=infotext
        self.length=length
        self.targetType=targetType
        self.missChance=missChance
        self.critChance=critChance
        self.targetFactor=targetFactor
        self.abilityType=abilityType
        self.power=power
        self.spriteName=spriteName
        self.animation=animation
class MapMene():
    def __init__(self,id,probability,lvlMin,lvlMax,meneEncounter):
        self.id=id
        self.probability=probability
        self.lvlMin=lvlMin
        self.lvlMax=lvlMax
        self.meneEncounter=meneEncounter
class Mute():
    def __init__(self,charID,endingTime,reason):
        self.charID=charID
        self.endingTime=endingTime
        self.reason=reason
class MapClass():
    def __init__(self):
        self.id=None
        self.name = ""
        self.width = 15
        self.height = 11
        self.tile = []
        self.npcs=[]
        self.song=""
        self.menes=[]
        self.players=[]
        self.death=["",0,0]
        self.meneEncounter=0
class TmpPlayer():
    def __init__(self):
        self.moving = False
        self.lastMoveTime = 0
        self.nextMoveDir=-1
        self.moved = False
        self.movePath = []
        self.movePathTmp = []
        self.toStop = False
        self.lastMsgTimes = []
        self.nextDir=None
        self.talkingTo=None
        self.creatingChar=False
        self.namingMeneID=None
        self.namingMeneLevel=1
        self.muted=None
        self.fightChecked=False
        #guildID,inviterCharID
        self.guildInvitePending=[None,None]
        self.fighting=None
        self.latencyTick=0
        self.partyID=None
        self.partyInvitePending=[None,None]
        self.packet=[]
class Player():
    def __init__(self,name="",id=None,wwwID=None,hat=1,face=0,shirt=0,shoes=0,access=0,map=1,x=2,y=2,dir=0,guildID=None,guildAccess=0,money=0,ES=0):
        self.id=id
        self.wwwID=wwwID
        self.name = name
        self.hat = hat
        self.face = face
        self.shirt = shirt
        self.shoes=shoes
        self.access = access
        self.map = map
        self.x = x       
        self.y = y         
        self.dir = dir
        self.friendList = []
        self.ignoreList = []
        self.menes = []
        self.guildID=guildID
        self.guildAccess=guildAccess
        self.connection=None
        self.achievements=[]
        self.tmpPlayer = None
        self.money=money
        self.ES=ES
class TileClass():
    def __init__(self):
        #self.l1 = None
        #self.l2 = None
        #self.l3 = None
        #self.f = None
        self.t = 0
        self.d1 = None
        self.d2 = 0
        self.d3 = 0
class NPCClass():
    def __init__(self,name=None,hat=1,face=0,shoes=0,shirt=0,sprite=0,dir=1,x=0,y=0,map=None,walkingType=0,radius=0,text=None,walkDelay=5000,actionType=0):
        self.name = name
        self.hat = hat
        self.face=face
        self.shoes=shoes
        self.shirt = shirt
        self.sprite=sprite
        self.dir = dir
        self.x=x
        self.y=y
        self.originalX=x
        self.originalY=y
        self.map=map
        self.walkingType=walkingType
        self.radius=radius
        self.text=text
        self.actionType=actionType
        self.walkDelay=walkDelay
        self.tmpPlayer = TmpPlayer()
class Guild():
    def __init__(self,name="",id=None):
        self.name=name
        self.id=id
        self.members=[]
class Ban():
    def __init__(self,charID=None,endingTime=None,reason=None):
        self.charID=charID
        self.endingTime=endingTime
        self.reason=reason
class Report():
    def __init__(self,charID=None,text=None):
        self.charID=charID
        self.text=text
        self.adminID=None
        self.solved=0
class Mail():
    def __init__(self,ID,charID=None,text=None,senderID=None,timestamp=None):
        self.id=ID
        self.charID=charID
        self.text=text
        self.senderID=senderID
        self.timestamp=timestamp
class GuildMember():
    def __init__(self,charID=None,guildAccess=0,online=False):
        self.charID=charID
        self.guildAccess=guildAccess
        self.online=online
class Party():
    def __init__(self,ownerID=None):
        self.ownerID=ownerID
        self.members=[]
class NpcMatch():
    def __init__(self,ID=None,playerID=None,playerMene=None,npcMene=None):
        self.ID=ID
        self.playerID=playerID
        self.playerMene=playerMene
        self.npcMene=npcMene
        self.turn=1
        self.ready=False
        self.nextAttack=0
        self.status=1
        
authTokens = []
Maps = {}
Menes = {}
Abilities = {}
Players = {}
Achievements = {}
Guilds = {}
Mutes=[]
Bans = []
Reports=[]
Mails={}
Parties={}
Matches = {}
Items = {}
DatabaseSavings = {"players":[],"achievements":[],"guilds":[], "ignores":[],"friends":[],"admincommands":[],"mutes":[],"bans":[],"reports":[],"mails":[]}
ClothingPairs=[]
OnlinePlayers=[]