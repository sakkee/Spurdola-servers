import globalvars as g
from objects import *
from database import *
from packettypes import *
from messages import *
import random
import re

def sendDataToAdmins(data):
    for ID in OnlinePlayers:
        if getPlayerAccess(ID)>0:
            sendDataToPlayer(data,ID)
def sendDataToPlayer(data,ID):
    Players[ID].tmpPlayer.packet.append(data)
def sendDataToMap(data,mapID, ignore=False, ID=None):
    #print "DATA",data
    for charID in Maps[mapID].players:
        if ignore and ID is not None and ID in getPlayerIgnores(charID):
            pass
        else:
            sendDataToPlayer(data,charID)
def sendDataToMatch(data,matchID):
    sendDataToPlayer(data,Matches[matchID].playerID)
def sendFightTriggerToMap(ID,fighting):
    #plrIndex = getPlayerListIndex(index=index)
    if fighting:
        Players[ID].tmpPlayer.nextMoveDir = -1
        Players[ID].tmpPlayer.movePath[:] = []
        Players[ID].tmpPlayer.moving=False
        sendDataToMap({"p": ServerPackets.PlayerMoveStop, "n":Players[ID].name, "x":Players[ID].x,"y":Players[ID].y,'d':Players[ID].dir},getPlayerMap(ID))
    sendDataToMap({"p": ServerPackets.SendFightTriggerToMap, "n":getPlayerName(ID),'s':fighting},getPlayerMap(ID))
def sendFightToPlayer(ID):
    matchID = getPlayerMatch(ID)
    if matchID is None:
        print "WTFF HAPPENED??"
        return
    
    #list=[]
    #list.append({"p": ServerPackets.StartFight, 'turn': match.turn, 'mn':getPlayerDefaultMene(plrIndex=plrIndex).name})
    animationList=[]
    try:
        animationList.append(Abilities[Matches[matchID].npcMene.attack1].animation)
        animationList.append(Abilities[Matches[matchID].npcMene.attack2].animation)
        animationList.append(Abilities[Matches[matchID].npcMene.attack3].animation)
        animationList.append(Abilities[Matches[matchID].npcMene.attack4].animation)
    except Exception, e:
        pass
    menepacket = {"n":Matches[matchID].npcMene.name,"hp":Matches[matchID].npcMene.hp,"l":Matches[matchID].npcMene.level,"sp":Matches[matchID].npcMene.spriteName, 'a':animationList}
    sendDataToPlayer({"p": ServerPackets.StartFight, 'turn': Matches[matchID].turn, 'i':Matches[matchID].playerMene.playerMeneID,'m':menepacket},ID)
    #packet = json.dumps(list)
    #g.conn.sendDataTo(packet,plrIndex=plrIndex)
def sendDataToParty(data,pID,ignore=False, ID=None,exceptThisID=None):
    for memberID in Parties[pID].members:
        if ignore and ID is not None and getPlayerIgnore(memberID,ID):
            pass
        elif exceptThisID is not None and exceptThisID==memberID:
            pass
        else:
            sendDataToPlayer(data,memberID)
            #Players[memberID].packet.append(data)
def sendDataToGuild(data,gID,ignore=False, ID=None):
    for gMember in Guilds[gID].members:
        if gMember.online:
            if ignore and ID is not None and ID in getPlayerIgnores(gMember.charID):
                pass
            else:
                sendDataToPlayer(data,gMember.charID)
                #Players[gMember.charID].packet.append(data)
def sendJoinedGuild(ID,gID):
    sendDataToGuild({"p": ServerPackets.SendJoinedGuild, "n":getPlayerName(ID)},gID)
    sendRefreshNameText(getPlayerName(ID),getPlayerMap(ID),Guilds[gID].name)
    
def sendLeftGuild(ID,gID):
    sendDataToGuild({"p": ServerPackets.SendLeaveGuild, "n":getPlayerName(ID)},gID)
    sendRefreshNameText(getPlayerName(ID),getPlayerMap(ID),None)
def sendRefreshNameText(name, map, guildName=None):
    sendDataToMap({"p": ServerPackets.SendRefreshName, "n":name, "g":guildName},map)
def sendRealMove(name,direction,x,y,mapID):
    sendDataToMap({"p": ServerPackets.PlayerMoveReal, "n":name, "x":x,"y":y, 'd':direction},mapID)
def sendGuildmembersToPlayer(ID):
    gID = Players[ID].guildID
    if gID is None:
        sendDataToPlayer({"p": ServerPackets.SendGuildmembers, "gname":None,'m':[]},ID)
        #Players[ID].packet.append({"p": ServerPackets.SendGuildmembers, "gname":None,'m':[]})
    else:
        returnList=[]
        for member in Guilds[gID].members:
            if member.online==False:
                returnList.append([Players[member.charID].name,member.guildAccess,0])
            else:
                returnList.append([Players[member.charID].name,member.guildAccess,1])
        sendDataToPlayer({"p": ServerPackets.SendGuildmembers, "gname":Guilds[gID].name, 'm':returnList},ID)
        #Players[ID].packet.append({"p": ServerPackets.SendGuildmembers, "gname":Guilds[gID].name, 'm':returnList})
def sendMenesToPlayer(ID):
    meneList=[]
    plrMenes = getPlayerMenes(ID)
    changingMene=0
    changedMeneID=None
    for mene in plrMenes:
        if mene.inventoryType==MENE_INVENTORYTYPE_DEFAULT and mene.hp==0:
            changingMene=1
    
    for mene in plrMenes:
        if changingMene==1 and mene.inventoryType==MENE_INVENTORYTYPE_CARRYING and mene.hp>0:
            mene.inventoryType=MENE_INVENTORYTYPE_DEFAULT
            changingMene=2
            changedMeneID=mene.playerMeneID
        elif changingMene>0 and mene.inventoryType==MENE_INVENTORYTYPE_DEFAULT and changedMeneID!=mene.playerMeneID:
            mene.inventoryType=MENE_INVENTORYTYPE_CARRYING
            
        
        defaultMene = getMene(mene.meneID)
        a1_1=None
        if defaultMene.attack1 is not None:
            a1_1 = Abilities[defaultMene.attack1].__dict__
        a2_1=None
        if defaultMene.attack2 is not None:
            a2_1 = Abilities[defaultMene.attack2].__dict__
        a3_1=None
        if defaultMene.attack3 is not None:
            a3_1 = Abilities[defaultMene.attack3].__dict__
        a4_1=None
        if defaultMene.attack4 is not None:
            a4_1 = Abilities[defaultMene.attack4].__dict__
        
        meneList.append({"i":mene.playerMeneID,
                         "n":mene.name,
                         "xp":mene.xp,
                         "l":mene.level,
                         "hp":mene.hp,
                         "hpmax":mene.hpmax,
                         "p":mene.power,
                         "de":mene.defense,
                         "s":mene.speed,
                         "a1":a1_1,
                         "a2":a2_1,
                         "a3":a3_1,
                         "a4":a4_1,
                         "sp":Menes[mene.meneID].spriteName,
                         "d":mene.inventoryType})
        
    sendDataToPlayer({"p":ServerPackets.SendMenes,"m":meneList},ID)
def sendCharToPlayer(ID):
    packet = {"p":ServerPackets.SendChar,"n":getPlayerName(ID),"h":getPlayerHat(ID),"f":getPlayerFace(ID),"s":getPlayerShirt(ID),"sh":getPlayerShoes(ID),"a":getPlayerAccess(ID),"x":getPlayerX(ID),"y":getPlayerY(ID),"dir":getPlayerDir(ID),"m":getMapName(getPlayerMap(ID)),'mo':getPlayerMoney(ID),'ES':getPlayerES(ID)}
    sendDataToPlayer(packet,ID)
    #Players[ID].packet.append(packet)
    
def isEligible(ID):
    if Players[ID].tmpPlayer.fighting is not None or Players[ID].tmpPlayer.creatingChar:
        return False
    return True
def sendMails(ID):
    mails=[]
    for id in Mails:
        if Mails[id].charID==ID:
            if isinstance(Mails[id].text,str):
                mails.append({'id':Mails[id].id,'t':unicode(Mails[id].text,'ISO-8859-1'),'s':getPlayerName(Mails[id].senderID)})
            else:
                mails.append({'id':Mails[id].id,'t':Mails[id].text,'s':getPlayerName(Mails[id].senderID)})
    sendDataToPlayer({'p':ServerPackets.SendMails,'m':mails},ID)
def handleMovement(direction,ID,path=False,send=True):
    if not isEligible(ID):
        return
    if path == False:
        Players[ID].tmpPlayer.movePath[:] = []
        Players[ID].tmpPlayer.movePathTmp[:] = []
        Players[ID].tmpPlayer.toStop = False
    mapID = Players[ID].map
    chg = posChange(direction)
    plrX = Players[ID].x
    plrY = Players[ID].y
    
    if plrX+chg[0]>=0 and plrY+chg[1]>=0 and plrX+chg[0]<Maps[mapID].width and plrY+chg[1]<Maps[mapID].height and Maps[mapID].tile[plrX+chg[0]][plrY+chg[1]].t is not TILE_TYPE_BLOCKED:
        if not Players[ID].tmpPlayer.moving:
            Players[ID].dir = direction
            Players[ID].tmpPlayer.moving=True
            Players[ID].tmpPlayer.lastMoveTime=g.lastTick
            Players[ID].x=plrX+chg[0]
            Players[ID].y=plrY+chg[1]
            if send:
                sendDataToMap({"p": ServerPackets.PlayerMove, "d": direction, "n":Players[ID].name},mapID)
        else:
            sendDataToMap({"p": ServerPackets.PlayerMoveNext, "d": direction, "n":Players[ID].name},mapID)
        Players[ID].tmpPlayer.nextMoveDir = direction
    elif Players[ID].dir != direction:
        Players[ID].dir = direction
        sendDataToMap({"p": ServerPackets.PlayerMoveStop, "n":Players[ID].name, "x":Players[ID].x,"y":Players[ID].y,'d':Players[ID].dir},mapID)
def changeGuildMemberOnlineStatus(charID,isOnline):
    gID = Players[charID].guildID
    if gID is None:
        return
    for member in Guilds[gID].members:
        if member.charID == charID:
            member.online=isOnline
            break
def healPlayerMenes(ID):
    for mene in Players[ID].menes:
        mene.hp=mene.hpmax
    #sendErrorMsg(ID,WARNING_MENES_HEALED)#
    sendDataToPlayer({"p":ServerPackets.HealMenes},ID)
def sendNPCsToPlayer(ID):
    ##TODO: To lower the server upload, maybe users should load the NPCs from files?
    
    map = Players[ID].map
    npcList = []
    for i in xrange(len(Maps[map].npcs)):
        npcList.append({
                "n": Maps[map].npcs[i].name,
                "h": Maps[map].npcs[i].hat,
                "f": Maps[map].npcs[i].face,
                "s": Maps[map].npcs[i].shirt,
                "sh": Maps[map].npcs[i].shoes,
                "x": Maps[map].npcs[i].x,
                "y": Maps[map].npcs[i].y,
                "d": Maps[map].npcs[i].dir,
                "te": Maps[map].npcs[i].text,
                "type": Maps[map].npcs[i].actionType
        })
    sendDataToPlayer({"p":ServerPackets.SendNpcsFromMap,'npcs':npcList},ID)
    
def sendCharsToPlayer(ID):
    charList = []
    mapID = getPlayerMap(ID)
    for charID in Maps[mapID].players:
        if charID != ID:
            charList.append({
                        "n": Players[charID].name,
                       "h": Players[charID].hat,
                       "f": Players[charID].face,
                       "s": Players[charID].shirt,
                       "sh": Players[charID].shoes,
                       "a": Players[charID].access,
                       "x": Players[charID].x,
                       "y": Players[charID].y,
                       "d": Players[charID].dir,
                       "g": getGuildName(getPlayerGuild(charID)),
                       "fi": isFighting(charID)
            })
    sendDataToPlayer({"p": ServerPackets.SendCharsFromMap,'pl':charList},ID)
    
def processNpcMatchAttack(attackerMene,enemyMene,attack,match):
    match.ready=False
    ability = Abilities[attack]
    RNG = random.random()
    power=0
    if RNG<=ability.missChance/100.0:
        attack_rng = ATTACK_RNG_MISS
    elif RNG>=(100-ability.critChance)/100.0:
        attack_rng = ATTACK_RNG_CRIT
    else:
        attack_rng = ATTACK_RNG_NORMAL
    modifier = attack_rng*random.uniform(0.85,1.0)
    if ability.targetFactor==ENEMY_TEAM:
        targetmene=enemyMene
        if ability.abilityType==ABILITY_TYPE_ATTACK:
            RNG = random.random()
            if RNG<=ability.missChance/100.0:
                attack_rng = ATTACK_RNG_MISS
            elif RNG>=(100-ability.critChance)/100.0:
                attack_rng = ATTACK_RNG_CRIT
            else:
                attack_rng = ATTACK_RNG_NORMAL
            modifier = attack_rng*random.uniform(0.80,1.0)
            damage = calculateDamage(attackerMene.level,attackerMene.power,enemyMene.defense,ability.power,modifier)
            power=damage
            enemyMene.hp-=damage
            if enemyMene.hp<0:
                enemyMene.hp=0
    elif ability.targetFactor==OWN_TEAM:
        if ability.abilityType==ABILITY_TYPE_HEAL:
            targetmene=attackerMene
            heal = calculateHeal(attackerMene.hpmax,ability.power,attack_rng)
            attackerMene.hp+=heal
            power=heal
            if attackerMene.hp>attackerMene.hpmax:
                attackerMene.hp=attackerMene.hpmax
    #print attackerMene,match.mene1,match.mene2
    if attackerMene==match.playerMene:
        #print "HAPPEEEND"
        match.turn=PLAYER_TWO_TURN
        attacker=1
        if ability.targetFactor==ENEMY_TEAM:
            targeted=2
        else:
            targeted=1
    else:
        match.turn=PLAYER_ONE_TURN
        attacker=2
        if ability.targetFactor==ENEMY_TEAM:
            targeted=1
        else:
            targeted=2
    sendDataToPlayer({"p": ServerPackets.SendAttack, "t":match.turn, "hp":targetmene.hp,"po":power,'sp':ability.animation,'rng':attack_rng,'n':ability.name,'ty':ability.abilityType,'ta':targeted,'c':attacker},match.playerID)
    if enemyMene.hp==0 and enemyMene==match.npcMene:
        if attackerMene.level<=MAX_LEVEL:
            xpGain = calculateXpGain(enemyMene.level,attackerMene.level)
            attackerMene.xp+=xpGain
            if attackerMene.xp>=calculateXpNeeded(attackerMene.level+1):
                meneStats = getMeneStats(level=attackerMene.level+1,meneID=attackerMene.meneID)
                attackerMene.level=getLevelByXp(attackerMene.xp)
                oldmax=attackerMene.hpmax
                attackerMene.hp+=meneStats["hp"]-oldmax
                attackerMene.hpmax=meneStats["hp"]
                attackerMene.speed=meneStats["speed"]
                attackerMene.defense=meneStats["defense"]
                attackerMene.power=meneStats["power"]
            sendDataToPlayer({"p": ServerPackets.XpReceived, "l":attackerMene.level,"xp":xpGain,"m":attackerMene.playerMeneID,"hp":attackerMene.hp,"hpmax":attackerMene.hpmax,"s":attackerMene.speed,"d":attackerMene.defense,"po":attackerMene.power},match.playerID)
        money = calculateMoneyReceived(enemyMene.level)
        print "MONEY",money
        addPlayerMoney(match.playerID,money)
        sendDataToPlayer({"p": ServerPackets.MoneyReceived, "m":money,"nm":getPlayerMoney(match.playerID)},match.playerID)
        match.status = MATCH_PLAYER_WON
        endMatch(match.playerID)
    elif enemyMene.hp==0 and enemyMene==match.playerMene:
        sendDataToPlayer({"p": ServerPackets.MeneDies, "m":match.playerMene.playerMeneID},match.playerID)
        if hasMenesAlive(match.playerID):
            #this is just a fail-safe, making a random mene default in case player disconnects
            marked = False
            for mene in getPlayerMenes(match.playerID):
                if mene.inventoryType != MENE_INVENTORYTYPE_DEFAULT and mene.hp>0 and not marked:
                    mene.inventoryType = MENE_INVENTORYTYPE_DEFAULT
                    marked=True
                elif mene.inventoryType == MENE_INVENTORYTYPE_DEFAULT:
                    mene.inventoryType = MENE_INVENTORYTYPE_CARRYING
            sendDataToPlayer({"p": ServerPackets.InitiateMeneSelect},match.playerID)
        else:
            match.status = MATCH_NPC_WON
            endMatch(match.playerID)
            mapID=getPlayerMap(match.playerID)
            playerTeleport(match.playerID,x=Maps[mapID].death[1],y=Maps[mapID].death[2],map=Maps[mapID].death[0])
            healPlayerMenes(match.playerID)
    match.nextAttack=g.lastTick+NPC_MENE_ATTACK_WAIT_TIME
    
def endMatch(ID):
    matchID = getPlayerMatch(ID)
    sendDataToPlayer({"p": ServerPackets.EndMatch,'result':Matches[matchID].status},ID)
    del Matches[matchID]
    Players[ID].tmpPlayer.fighting=None
    sendFightTriggerToMap(ID,False)
    
def processNpcMeneAttack(matchID):
    possibleAttacks = []
    if Matches[matchID].npcMene.attack1 is not None:
        possibleAttacks.append(Matches[matchID].npcMene.attack1)
    if Matches[matchID].npcMene.attack2 is not None:
        possibleAttacks.append(Matches[matchID].npcMene.attack2)
    if Matches[matchID].npcMene.attack3 is not None:
        possibleAttacks.append(Matches[matchID].npcMene.attack3)
    if Matches[matchID].npcMene.attack4 is not None:
        possibleAttacks.append(Matches[matchID].npcMene.attack4)
    choice=random.choice(possibleAttacks)
    processNpcMatchAttack(Matches[matchID].npcMene,Matches[matchID].playerMene,choice,Matches[matchID])
def sendIgnoresToPlayer(ID):
    ignores = []
    for c in Players[ID].ignoreList:
        ignores.append(getPlayerName(c))
    sendDataToPlayer({"p": ServerPackets.SendIgnores,'i':ignores},ID)
def sendFriendsToPlayer(ID):
    friends = []
    for c in Players[ID].friendList:
        if isPlayerOnlineID(c):
            friends.append([getPlayerName(c),1])
        else:
            friends.append([getPlayerName(c),0])
    sendDataToPlayer({"p": ServerPackets.SendFriends,'i':friends},ID)
def sendItemsToPlayer(ID):
    sendDataToPlayer({"p": ServerPackets.SendItems,'i':Items},ID)
def notificateFriends(ID,loggedIn=True):
    for charID in OnlinePlayers:
        if getPlayerFriend(charID,ID):
            if loggedIn:
                sendDataToPlayer({"p": ServerPackets.FriendLoggedIn,'n':[getPlayerName(ID)],'m':WARNING_FRIENDLOGGEDIN},charID)
            else:
                sendDataToPlayer({"p": ServerPackets.FriendLoggedOut,'n':[getPlayerName(ID)],'m':WARNING_FRIENDLOGGEDOUT},charID)
                
def sendUpdateProperties(ID):
    sendDataToPlayer({"p":ServerPackets.SendMoneyUpdate,"m":getPlayerMoney(ID),"es":getPlayerES(ID)},ID)
def notificateGuild(ID,loggedIn=True):
    gID = getPlayerGuild(ID)
    if gID is None:
        return
    for char in Guilds[gID].members:
        if char.online:
            charID=char.charID
            if loggedIn:
                sendDataToPlayer({"p": ServerPackets.GuildMemberLogged,'in':True, 'n':getPlayerName(ID)},charID)
            else:
                sendDataToPlayer({"p": ServerPackets.GuildMemberLogged,'in':False, 'n':getPlayerName(ID)},charID)
def sendLoginStuff(ID):
    for mute in Mutes:
        if mute.charID==ID:
            Players[ID].tmpPlayer.muted=mute.endingTime
    sendCharToPlayer(ID)
    
    changeGuildMemberOnlineStatus(ID,True)
    sendGuildmembersToPlayer(ID)
    sendNPCsToPlayer(ID)
    sendFriendsToPlayer(ID)
    sendCharsToPlayer(ID)
    sendPlayerToChars(ID)
    sendMenesToPlayer(ID)
    sendIgnoresToPlayer(ID)
    sendItemsToPlayer(ID)
    notificateFriends(ID)
    notificateGuild(ID)
    joinNewMap(ID)
    sendMails(ID)
    
    '''
    
    sendFriendsToPlayer(index)
    sendIgnoresToPlayer(index)
    sendMenesToPlayer(index)
    
    plrIndex = getPlayerListIndex(index=index)
    
    notificateGuild(getPlayerName(ID),getPlayerGuild(ID))
    packet=[]
    
    packet.append({"p": ServerPackets.SendPlayerConnect})
    packet.append({"n": getPlayerName(ID),
                   "h": getPlayerHat(ID),
                   "f": getPlayerFace(ID),
                   "s": getPlayerShirt(ID),
                   "sh": getPlayerShoes(ID),
                   "a": getPlayerAccess(ID),
                   "x": getPlayerX(ID),
                   "y": getPlayerY(ID),
                   "d": getPlayerDir(ID),
                   "g": getGuildName(getPlayerGuild(ID))
                   })
    g.conn.sendDataToMap(json.dumps(packet),getPlayerMap(ID),index=plrIndex)
    sendNotifications(index=index)
    '''
def sendPlayerToChars(ID):
    packet = {"p": ServerPackets.SendPlayerConnect,
                    "n": getPlayerName(ID),
                   "h": getPlayerHat(ID),
                   "f": getPlayerFace(ID),
                   "s": getPlayerShirt(ID),
                   "sh": getPlayerShoes(ID),
                   "a": getPlayerAccess(ID),
                   "x": getPlayerX(ID),
                   "y": getPlayerY(ID),
                   "d": getPlayerDir(ID),
                   "g": getGuildName(getPlayerGuild(ID))
                   }
    sendDataToMap(packet,getPlayerMap(ID))
def sendErrorMsg(ID=None,error=WARNING_EMPTY_MESSAGE,t=None):
    if t is not None:
        sendDataToPlayer({"p": ServerPackets.ErrorMsg, 'm': error,'t':t},ID)
        #Players[ID].packet.append({"p": ServerPackets.ErrorMsg, 'm': error,'t':t})
    else:
        sendDataToPlayer({"p": ServerPackets.ErrorMsg, 'm': error},ID)
def sendPlayerDisconnectToMap(ID):
    sendDataToMap({"p": ServerPackets.SendPlayerDisconnect, "n":Players[ID].name},getPlayerMap(ID))

def playerJoinsParty(ID,partyID):
    if partyID is None:
        return
    if len(Parties[partyID].members)==5:
        sendErrorMsg(ID,WARNING_PARTY_IS_FULL)
        return
    setPlayerParty(ID,partyID)
    Parties[partyID].members.append(ID)
    if len(Parties[partyID].members)==1:
        Parties[partyID].ownerID=ID
    sendDataToParty({"p":ServerPackets.SendPlayerJoinsParty,"n":getPlayerName(ID),"f":getPlayerFace(ID),'s':getPlayerShirt(ID),'sh':getPlayerShoes(ID),'h':getPlayerHat(ID),'o':getPlayerPartyAccess(ID),'j':True},partyID,exceptThisID=ID)
    for member in Parties[partyID].members:
        sendDataToPlayer({"p":ServerPackets.SendPlayerJoinsParty,"n":getPlayerName(member),"f":getPlayerFace(member),'s':getPlayerShirt(member),'sh':getPlayerShoes(member),'h':getPlayerHat(member),'o':getPlayerPartyAccess(member),'j':False},ID)
        if getPlayerMap(member)==getPlayerMap(ID):
            sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":getPlayerName(ID), "g":getGuildName(getPlayerGuild(ID))},member)
            sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":getPlayerName(member), "g":getGuildName(getPlayerGuild(member))},ID)
    #print "TODO: SEND NOTIFICATIONS TO PARTYMEMBERS"
    #print "TODO: SEND PARTYMEMBERS TO PLAYER"
def playerLeftParty(ID,kicked=False):
    partyID = getPlayerParty(ID)
    if partyID is None:
        return
    setPlayerParty(ID,None)
    if len (Parties[partyID].members)==1:
        del Parties[partyID]
        sendDataToPlayer({"p":ServerPackets.SendPlayerLeavesParty,"n":getPlayerName(ID),'o':None,'k':kicked},ID)
        
    else:
        if Parties[partyID].ownerID==ID:
            for memberID in Parties[partyID].members:
                if memberID!=ID:
                    Parties[partyID].ownerID=memberID
                
        sendDataToParty({"p":ServerPackets.SendPlayerLeavesParty,"n":getPlayerName(ID),'o':getPlayerName(Parties[partyID].ownerID),'k':kicked},partyID)
        del Parties[partyID].members[Parties[partyID].members.index(ID)]
        for memberID in Parties[partyID].members:
            if getPlayerMap(memberID)==getPlayerMap(ID):
                sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":getPlayerName(ID), "g":getGuildName(getPlayerGuild(ID))},memberID)
                sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":getPlayerName(memberID), "g":getGuildName(getPlayerGuild(memberID))},ID)
    #print "TODO: SEND NOTIFICATIONS TO PARTYMEMBERS"
    #print "TODO: SEND LEFTPARTY TO PLAYER"
def handlePlayerDisconnect(ID):
    Players[ID].connection.transport.loseConnection()
    Players[ID].connection=None
    if isFighting(ID):
        fightID = getPlayerMatch(ID)
        del Matches[fightID]
    del OnlinePlayers[OnlinePlayers.index(ID)]
    playerLeftParty(ID)
    if Players[ID].tmpPlayer.talkingTo is not None:
        Maps[getPlayerMap(ID)].npcs[getNpcListIndex(Players[ID].tmpPlayer.talkingTo,getPlayerMap(ID))].tmpPlayer.talkingTo=None
    Players[ID].tmpPlayer.packet[:]=[]
    Players[ID].tmpPlayer = None
    changeGuildMemberOnlineStatus(ID,False)
    leaveOldMap(ID)
    sendPlayerDisconnectToMap(ID)
    notificateFriends(ID,loggedIn=False)
    notificateGuild(ID,loggedIn=False)
    
    ###DO ALL DISCONNECT STUFF HERE###
def kickUnauthClients():
    for i in range(len(g.conn.factory.unauthClients)):
        if g.conn.factory.unauthClients[i].time + 1000*5 < g.lastTick:
            g.conn.closeUnauthConnection(i)
            


def playerTeleport(ID,x=None,y=None,map=None,newMapID=None):
    Players[ID].tmpPlayer.movePath[:] = []
    mapID = getPlayerMap(ID)
    
    if Players[ID].tmpPlayer.talkingTo is not None:
        if Maps[mapID].npcs[getNpcListIndex(Players[ID].tmpPlayer.talkingTo,mapID)].tmpPlayer.talkingTo == ID:
            Maps[mapID].npcs[getNpcListIndex(Players[ID].tmpPlayer.talkingTo,mapID)].tmpPlayer.talkingTo = None
        Players[ID].tmpPlayer.talkingTo = None
    Players[ID].tmpPlayer.nextMoveDir = -1
    sendDataToMap({"p": ServerPackets.PlayerTeleportLeave, 'n': getPlayerName(ID)},mapID)
    if x is None or y is None or (map is None and newMapID is None):
        tmpX=getPlayerX(ID)
        tmpY=getPlayerY(ID)
        x=Maps[mapID].tile[tmpX][tmpY].d2
        y=Maps[mapID].tile[tmpX][tmpY].d3
        map=Maps[mapID].tile[tmpX][tmpY].d1
    if newMapID is None:
        newMapID=getMapId(map)
    if newMapID is None:
        print "!!!!! map not found??mapID,x,y",mapID,x,y
        return
    leaveOldMap(ID)
    setPlayerX(ID,x)
    setPlayerY(ID,y)
    setPlayerMap(ID,newMapID)
    sendDataToPlayer({"p": ServerPackets.PlayerTeleportSelf, 'm': getMapName(newMapID),'x':x,'y':y},ID)
    sendCharsToPlayer(ID)
    sendNPCsToPlayer(ID)
    packet = {"p":ServerPackets.PlayerTeleportJoin,
       "n": getPlayerName(ID),
       "h": getPlayerHat(ID),
       "f": getPlayerFace(ID),
       "s": getPlayerShirt(ID),
       "sh": getPlayerShoes(ID),
       "a": getPlayerAccess(ID),
       "x": getPlayerX(ID),
       "y": getPlayerY(ID),
       "d": getPlayerDir(ID),
       "g": getGuildName(getPlayerGuild(ID))
       }
    sendDataToMap(packet,newMapID)
    joinNewMap(ID)
    
def changeFightMene(ID,meneID):
    matchID = getPlayerMatch(ID)
    Matches[matchID].ready=False
    Matches[matchID].playerMene=getPlayerMene(ID,meneID)
    Matches[matchID].turn=PLAYER_TWO_TURN
    Matches[matchID].nextAttack=g.lastTick+NPC_MENE_ATTACK_WAIT_TIME
    packet = {'p':ServerPackets.ChangeFightMene, 'player':PLAYER_ONE_TURN,'mene':meneID}
    sendDataToMatch(packet,matchID)
def checkFightTrigger(i,mapID):
    if Maps[mapID].menes==[]:
        return
    
    randomed=random.random()
    if randomed<=CHANCE_TO_ENCOUNTER:
        randomInteger=random.randint(0,Maps[mapID].meneEncounter)
        foundMene=None
        level=1
        for mene in Maps[mapID].menes:
            if mene.meneEncounter>=randomInteger:
                
                originalMene=getMene(id=mene.id)
                level = random.randint(mene.lvlMin,mene.lvlMax)
                meneStats = getMeneStats(level,mene.id,npc=True)
                foundMene=Menemon(level=level,power=meneStats["power"],defense=meneStats["defense"],speed=meneStats["speed"],hp=meneStats["hp"],hpmax=meneStats["hp"],name=originalMene.name,spriteName=originalMene.spriteName,attack1=originalMene.attack1,attack2=originalMene.attack2,attack3=originalMene.attack3,attack4=originalMene.attack4,id=originalMene.id)
                #foundMene=copy.copy(getMene(id=c[0]))
                #print "FOUNDMENE", foundMene.__dict__
                
                break
        
        Matches[g.lastMatchID]=NpcMatch(ID=g.lastMatchID,playerID=i,playerMene=getPlayerDefaultMene(i),npcMene=foundMene)
        Players[i].tmpPlayer.fighting=g.lastMatchID
        if Matches[g.lastMatchID].playerMene.speed>Matches[g.lastMatchID].npcMene.speed:
            Matches[g.lastMatchID].turn=PLAYER_ONE_TURN
        else:
            Matches[g.lastMatchID].turn=PLAYER_TWO_TURN
        g.lastMatchID+=1
        Players[i]
        sendFightToPlayer(i)
        sendFightTriggerToMap(i,True)
        Players[i].tmpPlayer.nextMoveDir = -1
        Players[i].tmpPlayer.movePath[:] = []
        #Players[i].tmpPlayer.moving=False
        Players[i].tmpPlayer.moved=False
        sendDataToMap({"p": ServerPackets.PlayerMoveStop, 'n': Players[i].name, "x":Players[i].x , "y":Players[i].y,'d':Players[i].dir},getPlayerMap(i))
        #Players[i].tmpPlayer.nextMoveDir = -1
        #Players[i].tmpPlayer.movePath[:] = []
        #Players[i].tmpPlayer.moved=False
        #Players[i].tmpPlayer.moving=False
        #sendDataToMap({"p": ServerPackets.PlayerMoveStop, 'n': Players[i].name, "x":Players[i].x , "y":Players[i].y,'d':Players[i].dir},getPlayerMap(i))
        return
def special_match(strg, search=re.compile(r'[^a-zA-Z0-9 -]').search):
    if bool(search(strg)):
        if strg==u'\xe4' or strg==u'\xc4' or strg==u'\xf6' or strg==u'\xd6' or strg==u"'":
            return True
        return False
    return True
def canMove(x,y,mapID,playerType=1):
    if x < 0 or y < 0 or x >= Maps[mapID].width or y>=Maps[mapID].height or Maps[mapID].tile[x][y].t==TILE_TYPE_BLOCKED:
        return False
    if playerType==1:
        if Maps[mapID].tile[x][y].t==TILE_TYPE_WARP or Maps[mapID].tile[x][y].t==TILE_TYPE_NPCAVOID:
            return False
    return True
def posChange(direction):
    if direction == DIR_DOWN:
        return [0,1]
    elif direction == DIR_LEFT:
        return [-1,0]
    elif direction == DIR_UP:
        return [0,-1]
    elif direction == DIR_RIGHT:
        return [1,0]
def distance(x1,y1,x2,y2):
    return abs(x2-x1)+abs(y2-y1)
def getDirectionFromOffset(offset):
    if abs(offset[0]) > abs(offset[1]):
        if offset[0] >= 0:
            return DIR_RIGHT
        else:
            return DIR_LEFT
    else:
        if offset[1] >= 0:
            return DIR_DOWN
        else:
            return DIR_UP
def checkPlayerOffset(destX,playerX,destY,playerY):
    return [destX-playerX,destY-playerY]
def clean_name(some_var):
    return ''.join(char for char in some_var if char.isalnum())
    
def checkMatches():
    for matchID in Matches.keys():
        if Matches[matchID].turn==PLAYER_TWO_TURN and Matches[matchID].nextAttack<g.lastTick and Matches[matchID].ready:
            #print Matches[matchID].nextAttack,g.lastTick
            #print "MATCHID ON", matchID
            processNpcMeneAttack(matchID)
def checkNPCMoves():
    for i in Maps:
        for j in xrange(len(Maps[i].npcs)):
            if Maps[i].npcs[j].walkingType != NPC_WALKTYPE_STOPPED:
                if Maps[i].npcs[j].tmpPlayer.moving:
                    if g.lastTick-Maps[i].npcs[j].tmpPlayer.lastMoveTime>=WALKSPEED:
                        Maps[i].npcs[j].tmpPlayer.moving=False
                        if Maps[i].npcs[j].tmpPlayer.nextDir is not None:
                            Maps[i].npcs[j].dir=Maps[i].npcs[j].tmpPlayer.nextDir
                            Maps[i].npcs[j].tmpPlayer.nextDir=None
                            sendDataToMap({"p": ServerPackets.SendNpcDir, "n":Maps[i].npcs[j].name, "d":Maps[i].npcs[j].dir},i)
                elif g.lastTick-Maps[i].npcs[j].tmpPlayer.lastMoveTime>=Maps[i].npcs[j].walkDelay:
                    if Maps[i].npcs[j].tmpPlayer.talkingTo is not None:
                        if Players[Maps[i].npcs[j].tmpPlayer.talkingTo].tmpPlayer.talkingTo != Maps[i].npcs[j].name or distance(Maps[i].npcs[j].x,Maps[i].npcs[j].y,getPlayerX(Maps[i].npcs[j].tmpPlayer.talkingTo),getPlayerY(Maps[i].npcs[j].tmpPlayer.talkingTo))>MAX_NPC_TALK_DISTANCE:
                            Maps[i].npcs[j].tmpPlayer.talkingTo = None
                        else:
                            Maps[i].npcs[j].walkDelay=NPC_TALK_DELAY
                            Maps[i].npcs[j].tmpPlayer.lastMoveTime=g.lastTick
                    if Maps[i].npcs[j].tmpPlayer.talkingTo is None:
                        choices=[DIR_DOWN,DIR_LEFT,DIR_UP,DIR_RIGHT]
                        posChg=[-1,-1]
                        dir=DIR_DOWN
                        while len(choices)>0:
                            dir=random.choice(choices)
                            posChg=posChange(dir)
                            if Maps[i].npcs[j].walkingType == NPC_WALKTYPE_RESTRICTED and Maps[i].npcs[j].radius==0:
                                break
                            if canMove(Maps[i].npcs[j].x+posChg[0],Maps[i].npcs[j].y+posChg[1],i,playerType=1):
                                if Maps[i].npcs[j].walkingType==NPC_WALKTYPE_RESTRICTED and abs(Maps[i].npcs[j].x+posChg[0]-Maps[i].npcs[j].originalX)<=Maps[i].npcs[j].radius and abs(Maps[i].npcs[j].y+posChg[1]-Maps[i].npcs[j].originalY)<=Maps[i].npcs[j].radius:
                                    break
                                elif Maps[i].npcs[j].walkingType==NPC_WALKTYPE_FREEWALK:
                                    break
                            choices.remove(dir)
                        if posChg!=[-1,-1]:
                            Maps[i].npcs[j].tmpPlayer.lastMoveTime=g.lastTick
                            Maps[i].npcs[j].dir=dir
                            if posChg!=[0,0]:
                                Maps[i].npcs[j].tmpPlayer.moving=True
                                Maps[i].npcs[j].x+=posChg[0]
                                Maps[i].npcs[j].y+=posChg[1]
                                sendDataToMap({"p": ServerPackets.SendNpcMove, "n":Maps[i].npcs[j].name, "x":Maps[i].npcs[j].x,"y":Maps[i].npcs[j].y, 'd':Maps[i].npcs[j].dir},i)
                            else:
                                sendDataToMap({"p": ServerPackets.SendNpcDir, "n":Maps[i].npcs[j].name, "d":Maps[i].npcs[j].dir},i)
                        Maps[i].npcs[j].walkDelay=random.randrange(NPC_WALK_DELAY_LOWERLIMIT,NPC_WALK_DELAY_UPPERLIMIT)
                        
def checkPlayerMoves():
    for i in OnlinePlayers:
        mapID = getPlayerMap(i)
        if Players[i].tmpPlayer.moving:
            #First step of the movement
            if Players[i].tmpPlayer.moved == False:
                if Players[i].tmpPlayer.toStop == True:
                    Players[i].tmpPlayer.nextMoveDir = -1
                    if Players[i].tmpPlayer.talkingTo is not None:
                        npcIndex = getNpcListIndex(Players[i].tmpPlayer.talkingTo,mapID)
                        dir = getDirectionFromOffset(checkPlayerOffset(Maps[mapID].npcs[npcIndex].x,Players[i].x,Maps[mapID].npcs[npcIndex].y,Players[i].y))
                        Players[i].dir=dir
                        Maps[mapID].npcs[npcIndex].dir=getDirectionFromOffset(checkPlayerOffset(Players[i].x,Maps[mapID].npcs[npcIndex].x,Players[i].y,Maps[mapID].npcs[npcIndex].y))
                        sendDataToMap({"p": ServerPackets.SendNpcDir, "n":Maps[mapID].npcs[npcIndex].name, "d":Maps[mapID].npcs[npcIndex].dir},mapID)
                    sendDataToMap({"p": ServerPackets.PlayerMoveStop, 'n': Players[i].name, "x":Players[i].x , "y":Players[i].y,'d':Players[i].dir},mapID)
                    Players[i].tmpPlayer.toStop = False
                Players[i].tmpPlayer.moved = True
            if g.lastTick-Players[i].tmpPlayer.lastMoveTime>=WALKSPEED:
                Players[i].tmpPlayer.moved = False
                Players[i].tmpPlayer.moving=False
                #TODO
                #print Maps[mapID].tile[Players[i].x][Players[i].y].t, TILE_TYPE_FIGHT
                if Maps[mapID].tile[getPlayerX(i)][getPlayerY(i)].t == TILE_TYPE_WARP:
                    playerTeleport(i)
                elif Maps[mapID].tile[Players[i].x][Players[i].y].t == TILE_TYPE_FIGHT:
                    checkFightTrigger(i,mapID)
                if Players[i].tmpPlayer.movePath != []:
                    chg = checkPlayerOffset(Players[i].tmpPlayer.movePath[0][0],Players[i].x,Players[i].tmpPlayer.movePath[0][1],Players[i].y)
                    Players[i].tmpPlayer.nextMoveDir = getDirectionFromOffset(chg)
                    del Players[i].tmpPlayer.movePath[0]
                    if len(Players[i].tmpPlayer.movePath)==0:
                        Players[i].tmpPlayer.toStop=True
                if Players[i].tmpPlayer.nextMoveDir != -1:
                    handleMovement(Players[i].tmpPlayer.nextMoveDir,i,send=False,path=True)
                    if Players[i].tmpPlayer.moving:
                        sendRealMove(Players[i].name,Players[i].dir,Players[i].x,Players[i].y,Players[i].map)
                Players[i].tmpPlayer.fightChecked=False
            elif g.lastTick-Players[i].tmpPlayer.lastMoveTime>=WALKSPEED/2 and not Players[i].tmpPlayer.fightChecked:
                if Maps[mapID].tile[getPlayerX(i)][getPlayerY(i)].t == TILE_TYPE_FIGHT:
                    checkFightTrigger(i,mapID)
                Players[i].tmpPlayer.fightChecked=True
        elif Players[i].tmpPlayer.moved == True:
            Players[i].tmpPlayer.moved = False