import globalvars as g
from packettypes import *
import json
import time
import base64
from objects import *
from database import *
from properties import *
from constants import *
from gamelogic import *
from messages import *

class DataHandler():
    def handleUnauthData(self,index,data):
        jsonData = json.loads(data)
        packetType = jsonData["p"]
        if g.conn.factory.unauthClients[index].connection.transport.client[0]==g.loginServerIP and packetType == LoginClientPackets.SendAuthentication and g.loginServer is None:
            if g.loginAuthKey == g.privatekey.decrypt(base64.b64decode(jsonData["k"])):
                g.loginServer=g.conn.factory.unauthClients[index].connection
                del g.conn.factory.unauthClients[index]
        elif packetType == ClientPackets.Login:
            self.handleLogin(index,jsonData["k"])
            
    
    def handleLoginServerData(self,data):
        jsonData = json.loads(data)
        packetType = jsonData["p"]
        if packetType == LoginClientPackets.NewAuthentication:
            ID = getPlayerId(wwwID=jsonData["id"])
            banIndex = getPlayerBan(ID)
            if banIndex is None:
                if ID in OnlinePlayers:
                    handlePlayerDisconnect(ID)
                authTokens.append(authToken(jsonData["k"],jsonData["ip"],jsonData["n"],jsonData["id"])) 
                g.conn.sendDataToLoginServer(json.dumps({"p":LoginServerPackets.SendClientInfo, 'k':jsonData["k"],'ok':True}))
            else:
                reason = Bans[banIndex].reason
                if isinstance(reason,str):
                    reason = unicode(Bans[banIndex].reason,'ISO-8859-1')
                g.conn.sendDataToLoginServer(json.dumps({"p":LoginServerPackets.SendClientInfo, 'k':jsonData["k"],'ok':False,'d':(Bans[banIndex].endingTime-g.lastTick)/60./1000.,'r':reason}))
    
    def handleData(self, ID, data):
        if ID is None:
            print "ID IS NONE -- WHY???"
            return
        jsonData = json.loads(data)
        packetType = jsonData["p"]
        if packetType == ClientPackets.SendCreateChar:
            self.handleCreateChar(ID,jsonData["sh"],jsonData['s'],jsonData['f'],jsonData['h'])
        elif packetType == ClientPackets.SendMeneNameConfirm:
            self.handleNameMene(ID,jsonData["n"])
        elif packetType == ClientPackets.LatencyTick:
            self.handleLatencyTick(ID)
        elif packetType == ClientPackets.CreateGuild:
            self.handleCreateGuild(ID,jsonData["guildname"])
        elif packetType == ClientPackets.LeaveGuild:
            self.handleLeaveGuild(ID)
        elif packetType == ClientPackets.SendMove:
            self.handleMove(ID,jsonData["d"])
        elif packetType == ClientPackets.StopMove:
            self.stopMove(ID)
        elif packetType == ClientPackets.SendFaceTarget:
            self.handleFaceTarget(ID,jsonData["x"],jsonData["y"])
        elif packetType == ClientPackets.PlayerMovePath:
            self.handleMovePath(ID,jsonData["pa"])
        elif packetType == ClientPackets.StopTalkWithNPC:
            self.handleStopTalkWithNPC(ID,jsonData["n"])
        elif packetType == ClientPackets.TalkWithNPC:
            self.handleTalkWithNpc(ID,jsonData["n"])
        elif packetType == ClientPackets.SendMessage:
            self.handleChatMessage(ID,jsonData["m"])
        elif packetType == ClientPackets.RespondGuildInvite:
            self.respondGuildInvite(ID,jsonData["r"])
        elif packetType == ClientPackets.GetReport:
            self.handleGetReport(ID,jsonData["a"])
        elif packetType == ClientPackets.SendReport:
            self.handleSendReport(ID,jsonData["r"])
        elif packetType == ClientPackets.SolveReport:
            self.handleSolveReport(ID,jsonData['id'],jsonData['text'],jsonData["r"])
        elif packetType == ClientPackets.DeleteMail:
            self.handleDeleteMail(ID,jsonData["id"])
        elif packetType == ClientPackets.RespondPartyInvite:
            self.respondPartyInvite(ID,jsonData["r"])
        elif packetType == ClientPackets.SendFightReady:
            self.handleFightReady(ID)
        elif packetType == ClientPackets.SendAttack:
            self.handleSendAttack(ID,jsonData["id"])
        elif packetType == ClientPackets.SendHealMenes:
            self.handleSendHealMenes(ID)
        elif packetType == ClientPackets.SendBuyItem:
            self.handleSendBuyItem(ID,jsonData["i"])
        elif packetType == ClientPackets.ThrowES:
            self.handleThrowES(ID)
        elif packetType == ClientPackets.ChangeDefaultMene:
            self.handleChangeDefaultMene(ID,jsonData["id"])
        elif packetType == ClientPackets.SendLeaveMatch:
            self.handleSendLeaveMatch(ID)
        else:
            print "HACKING ATTEMPT??"
            
    def handleSendLeaveMatch(self,ID):
        if not isFighting(ID):
            return
        matchID = getPlayerMatch(ID)
        if matchID is None:
            return
        if Matches[matchID].status!=MATCH_IN_PROGRESS:
            return
        if not Matches[matchID].turn==PLAYER_ONE_TURN:
            return
        Matches[matchID].status=MATCH_PLAYER_LEFT
        endMatch(ID)
    def handleChangeDefaultMene(self,ID,meneID):
        if isFighting(ID) and Matches[getPlayerMatch(ID)].turn!=PLAYER_ONE_TURN:
            return
        found = False
        for mene in getPlayerMenes(ID):
            if mene.playerMeneID==meneID and mene.hp>0:
                found = True
                mene.inventoryType = MENE_INVENTORYTYPE_DEFAULT
        if found:
            for mene in getPlayerMenes(ID):
                if mene.playerMeneID!=meneID:
                    mene.inventoryType = MENE_INVENTORYTYPE_CARRYING
            if isFighting(ID):
                changeFightMene(ID,meneID)
        #for mene in getPlayerMenes(ID):
        #    print mene.name,mene.inventoryType
    def handleThrowES(self,ID):
        if getPlayerES(ID)<1:
            return
        if not isFighting(ID):
            return
        matchID = getPlayerMatch(ID)
        if matchID is None:
            return
        if Matches[matchID].status!=MATCH_IN_PROGRESS:
            return
        
        if not Matches[matchID].turn==PLAYER_ONE_TURN:
            return
        if playerHasMene(ID,Matches[matchID].npcMene.id):
            return
        a = ((3*Matches[matchID].npcMene.hpmax-2*Matches[matchID].npcMene.hp)*100.0)/(3.0*Matches[matchID].npcMene.hpmax*100)
        b=1#b = a**2
        r = random.random()
        c = r<b
        attempts=1
        if c:
            attempts=4
        elif b>0.33 and b<=0.66:
            attempts=2
        elif b>0.66:
            attempts=3
        #print a, b, r, c 
        sendDataToPlayer({"p":ServerPackets.ThrowES,"s":c,'a':attempts},ID)
        Matches[matchID].turn=PLAYER_TWO_TURN
        Matches[matchID].nextAttack=g.lastTick+3500+1500*attempts+3000+1000
        lowerPlayerES(ID)
        sendUpdateProperties(ID)
        if c:
            Matches[matchID].status = MATCH_MENE_CAUGHT
            Players[ID].tmpPlayer.namingMeneID=Matches[matchID].npcMene.id
            Players[ID].tmpPlayer.namingMeneLevel=Matches[matchID].npcMene.level
            endMatch(ID)
        #print Matches[matchID].nextAttack-g.lastTick
        #print Matches[matchID].nextAttack,g.lastTick
        #b = 1048560 / ((16711680.0/a)**0.5)**0.5
        #print "b ON", b
        #for i in range(4):
        #    print "random", random.randint(0,65535)
        
    def handleSendBuyItem(self,ID,item):
        npcIndex = getNpcListIndex(Players[ID].tmpPlayer.talkingTo,getPlayerMap(ID))
        if npcIndex is None:
            return
        if Maps[getPlayerMap(ID)].npcs[npcIndex].actionType != NPC_ACTIONTYPE_SHOP:
            return
        if item not in Items:
            return
        if Items[item]["cost"] > getPlayerMoney(ID):
            return
        addPlayerES(ID)
        lowerPlayerMoney(ID,Items[item]["cost"])
        sendUpdateProperties(ID)
    def handleSendHealMenes(self,ID):
        npcIndex = getNpcListIndex(Players[ID].tmpPlayer.talkingTo,getPlayerMap(ID))
        if Maps[getPlayerMap(ID)].npcs[npcIndex].actionType != NPC_ACTIONTYPE_HEAL:
            return
        healPlayerMenes(ID)
    def handleSendAttack(self,ID,abilityID):
        if not isFighting(ID):
            return
        matchID = getPlayerMatch(ID)
        if not Matches[matchID].turn==PLAYER_ONE_TURN:
            return
        tmpMene = getMene(id=Matches[matchID].playerMene.meneID)
        if abilityID not in (tmpMene.attack1,tmpMene.attack2,tmpMene.attack3,tmpMene.attack4):
            return
        if not Matches[matchID].ready:
            return
        if isMeneDead(matchID):
            return
        processNpcMatchAttack(Matches[matchID].playerMene,Matches[matchID].npcMene,abilityID,Matches[matchID])
    def handleFightReady(self,ID):
        if not isFighting(ID):
            return
        matchID = getPlayerMatch(ID)
        Matches[matchID].ready=True
        #if Matches[matchID].turn==PLAYER_TWO_TURN:
        #    processNpcMeneAttack(matchID)
    def handleDeleteMail(self,ID,mailID):
        if Mails[mailID].charID!=ID:
            return
        deleteMail(mailID)
    def handleSolveReport(self,ID,charID,text,remove):
        if getPlayerAccess(ID)==0:
            return
        report = getReportByCharID(charID)
        if report is None:
            return
        
        markReportSolved(report)
        if not remove:
            saveMail(charID,ID,text)
            sendMails(charID)
        saveAdminCommand(ID,"solvereport",msg=text,target=charID)
    def handleSendReport(self,ID,reportText,rid=None):
        if rid!=None:
            return
            #self.handleSolveReport(ID,rid,"Your ticket has been deleted.")
            
        else:
            if getReportText(ID) is None and reportText!="":
                sendDataToAdmins({"p": ServerPackets.ErrorMsg, 'm': WARNING_NEW_REPORT})
            saveReport(ID,reportText)
    def handleGetReport(self,ID,adminWindow):
        if adminWindow and getPlayerAccess(ID)>0:
            report = getFirstReport()
            if report is None:
                packet = {"p": ServerPackets.SendGetReport, 't': '', 'n':None,'id':None}
            else:
                packet = {"p": ServerPackets.SendGetReport, 't': report.text, 'n':getPlayerName(report.charID),'id':report.charID}
            
        elif not adminWindow:
            text = getReportText(ID)
            if text is None:
                text=""
            packet = {"p": ServerPackets.SendGetReport, 't': text, 'n':0, 'id':None}
        sendDataToPlayer(packet,ID)
    def respondPartyInvite(self,ID,response):
        if Players[ID].tmpPlayer.partyInvitePending==[None,None]:
            return
        if not response:
            sendErrorMsg(Players[ID].tmpPlayer.partyInvitePending[1],WARNING_PLAYER_REFUSED_INVITE,[getPlayerName(ID)])
        else:
            partyID = Players[ID].tmpPlayer.partyInvitePending[0]
            if partyID in Parties:
                playerJoinsParty(ID,partyID)
        Players[ID].tmpPlayer.guildInvitePending=[None,None]
    def respondGuildInvite(self,ID,response):
        if Players[ID].tmpPlayer.guildInvitePending==[None,None]:
            return
        
        if not response:
            sendErrorMsg(Players[ID].tmpPlayer.guildInvitePending[1],WARNING_PLAYER_REFUSED_INVITE,[getPlayerName(ID)])
        else:
            if getGuildName(Players[ID].tmpPlayer.guildInvitePending[0]) is not None:
                gID = Players[ID].tmpPlayer.guildInvitePending[0]
                Guilds[gID].members.append(GuildMember(charID=ID,guildAccess=GUILD_MEMBER,online=True))
                Players[ID].guildID=gID
                sendGuildmembersToPlayer(ID)
                sendJoinedGuild(ID,gID)
        Players[ID].tmpPlayer.guildInvitePending=[None,None]
        
    def handleChatMessage(self,ID,text):
        Players[ID].tmpPlayer.lastMsgTimes.append(g.lastTick)
        i=0
        while g.lastTick - Players[ID].tmpPlayer.lastMsgTimes[i] > CHATSPAMLIMIT_TIME:
            del Players[ID].tmpPlayer.lastMsgTimes[i]
        if len(Players[ID].tmpPlayer.lastMsgTimes)>CHATSPAMLIMIT:
            sendErrorMsg(ID,WARNING_CHATSPAM)
            del Players[ID].tmpPlayer.lastMsgTimes[-1]
            return
        newText = ''.join( c for c in text if  c not in BANNEDCHATCHARS )
        if len(newText)==0:
            return
        elif len(newText)>MAX_CHAT_INPUT:
            newText = newText[:MAX_CHAT_INPUT]
        if newText[0]=='/':
            helpText = newText[1:].split()
            if len(helpText)>0:
                if helpText[0]=='help':
                    sendErrorMsg(ID,WARNING_HELPFUNCTIONS)
                elif helpText[0]=='kick':
                    partyID=getPlayerParty(ID)
                    if partyID is None:
                        sendErrorMsg(ID,WARNING_NOT_PARTYOWNER)
                        return
                    if partyID is not None and not getPlayerPartyAccess(ID):
                        sendErrorMsg(ID,WARNING_NOT_PARTYOWNER)
                        return
                    if len(helpText)==1:
                        sendErrorMsg(ID,WARNING_HELP)
                        return
                    kickName = clean_name(helpText[1]).title()
                    charID = getPlayerOnlineId(name=kickName)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[kickName])
                        return
                    if getPlayerParty(charID)!=partyID:
                        return
                    playerLeftParty(charID,kicked=True)
                    
                elif helpText[0]=='leaveparty':
                    partyID = getPlayerParty(ID)
                    if partyID is None:
                        return
                    playerLeftParty(ID)
                    
                elif helpText[0]=='invite':
                    if len(helpText)==1:
                        sendErrorMsg(ID,WARNING_WRONG_INVITE)
                        return
                    partyID = getPlayerParty(ID)
                    partyCreated=False
                    if partyID is not None and not getPlayerPartyAccess(ID):
                        sendErrorMsg(ID,WARNING_NOT_PARTYOWNER)
                        return
                    inviteName = clean_name(helpText[1]).title()
                    charID = getPlayerOnlineId(name=inviteName)
                    
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[inviteName])
                        return
                    elif charID == ID:
                        sendErrorMsg(ID,WARNING_CANT_PARTYINVITE_SELF,[inviteName])
                        return
                    elif getPlayerIgnore(charID,ID):
                        sendErrorMsg(ID,WARNING_IGNORING,[inviteName])
                        return
                    elif getPlayerParty(charID) is not None:
                        sendErrorMsg(ID,WARNING_ALREADY_IN_PARTY,[inviteName])
                        return
                    if partyID is None:
                        partyCreated=True
                        Parties[g.lastPartyID]=Party(ownerID=ID)
                        Parties[g.lastPartyID].members.append(ID)
                        setPlayerParty(ID,g.lastPartyID)
                        partyID=g.lastPartyID
                        g.lastPartyID+=1
                    elif len(Parties[partyID].members)==MAX_PARTY_SIZE:
                        sendErrorMsg(ID,WARNING_PARTY_FULL)
                        return
                    Players[charID].tmpPlayer.partyInvitePending[0]=partyID
                    Players[charID].tmpPlayer.partyInvitePending[1]=ID
                    sendDataToPlayer({"p": ServerPackets.SendPartyInvite, 'e': WARNING_WANTS_TO_INVITE_YOU_PARTY, 't':[getPlayerName(ID)]},charID)
                    if partyCreated:
                        sendDataToPlayer({"p":ServerPackets.SendPlayerJoinsParty,"n":getPlayerName(ID),"f":getPlayerFace(ID),'s':getPlayerShirt(ID),'sh':getPlayerShoes(ID),'h':getPlayerHat(ID),'o':getPlayerPartyAccess(ID),'j':False},ID)
                        sendErrorMsg(ID,WARNING_PARTY_CREATED)
                    sendErrorMsg(ID,WARNING_PARTY_INVITE_SENT,[inviteName])
                elif helpText[0]=='ignore' and len(helpText)>1:
                    ignoreName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=ignoreName)
                    if charID == ID:
                        sendErrorMsg(ID,WARNING_CANT_IGNORE_SELF,[ignoreName])
                    elif charID is not None:
                        if not getPlayerIgnore(ID,charID):
                            setPlayerIgnore(ID,charID)
                            sendDataToPlayer({"p": ServerPackets.SendIgnores,'i':[ignoreName]},ID)
                            sendErrorMsg(ID,WARNING_IGNORED,[ignoreName])
                        else:
                            removePlayerIgnore(ID,charID)
                            sendDataToPlayer({"p": ServerPackets.RemoveIgnore,'i':ignoreName},ID)
                            sendErrorMsg(ID,WARNING_UNIGNORED,[ignoreName])
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[ignoreName])
                elif helpText[0]=='unignore' and len(helpText)>1:
                    ignoreName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=ignoreName)
                    if charID == ID:
                        sendErrorMsg(ID,WARNING_CANT_IGNORE_SELF,[ignoreName])
                    elif charID is not None:
                        if not getPlayerIgnore(ID,charID):
                            sendErrorMsg(ID,WARNING_IGNORING_NOT,[ignoreName])
                        else:
                            removePlayerIgnore(ID,charID)
                            sendDataToPlayer({"p": ServerPackets.RemoveIgnore,'i':ignoreName},ID)
                            sendErrorMsg(ID,WARNING_UNIGNORED,[ignoreName])
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[ignoreName])
                elif len(helpText)>1 and (helpText[0]=='friend' or helpText[0]=='addfriend' or helpText[0]=='add'):
                    friendName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=friendName)
                    if charID == ID:
                        sendErrorMsg(ID,WARNING_CANT_FRIEND_SELF,[friendName])
                    elif charID is not None:
                        if not getPlayerFriend(ID,charID):
                            setPlayerFriend(ID,charID)
                            online=0
                            if isPlayerOnlineID(charID):
                                online=1
                            sendDataToPlayer({"p": ServerPackets.SendFriends,'i':[[friendName,online]]},ID)
                            sendErrorMsg(ID,WARNING_FRIENDED,[friendName])
                            if getPlayerMap(charID)==getPlayerMap(ID):
                                sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":friendName, "g":getGuildName(getPlayerGuild(charID))},ID)
                        else:
                            removePlayerFriend(ID,charID)
                            sendDataToPlayer({"p": ServerPackets.RemoveFriend,'i':friendName},ID)
                            sendErrorMsg(ID,WARNING_UNFRIENDED,[friendName])
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[friendName])
                elif len(helpText)>1 and helpText[0]=='unfriend':
                    friendName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=friendName)
                    if charID == ID:
                        sendErrorMsg(ID,WARNING_CANT_UNFRIEND_SELF,[friendName])
                    elif charID is not None:
                        if not getPlayerFriend(ID,charID):
                            sendErrorMsg(ID,WARNING_NOT_FRIENDS,[friendName])
                        else:
                            removePlayerFriend(ID,charID)
                            sendDataToPlayer({"p": ServerPackets.RemoveFriend,'i':friendName},ID)
                            sendErrorMsg(ID,WARNING_UNFRIENDED,[friendName])
                            if getPlayerMap(charID)==getPlayerMap(ID):
                                sendDataToPlayer({"p": ServerPackets.SendRefreshName, "n":friendName, "g":getGuildName(getPlayerGuild(charID))},ID)
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[friendName])
                elif helpText[0]=='w' and len(helpText)>2:
                    whisperName = clean_name(helpText[1]).title()
                    charID = getPlayerOnlineId(name=whisperName)
                    if charID is not None:
                        if getPlayerIgnore(charID,ID):
                            sendErrorMsg(ID,WARNING_IGNORING,[whisperName])
                        else:
                            packet = {"p": ServerPackets.PlayerWhisper, 'n': Players[ID].name,'o':whisperName, 'm':newText.split(' ',2)[2]}
                            if ID != charID:
                                sendDataToPlayer(packet,charID)
                            sendDataToPlayer(packet,ID)
                        
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[whisperName])
                elif helpText[0]=='guildinvite' and len(helpText)>1:
                    inviteName = clean_name(helpText[1]).title()
                    charID = getPlayerOnlineId(name=inviteName)
                    if charID is not None:
                        gID = getPlayerGuild(charID)
                        if getPlayerIgnore(charID,ID):
                            sendErrorMsg(ID,WARNING_IGNORING,[inviteName])
                            return
                        if gID is not None:
                            sendErrorMsg(ID,WARNING_THE_PLAYER_ALREADY_IN_GUILD,[inviteName])
                            return
                        else:
                            playerGID = getPlayerGuild(ID)
                            if playerGID is None:
                                sendErrorMsg(ID,WARNING_YOU_ARE_NOT_IN_A_GUILD)
                                return
                            if getPlayerGuildAccess(ID) < GUILD_MODERATOR:
                                sendErrorMsg(ID,WARNING_YOU_DONT_HAVE_ACCESS_TO_DO_THAT)
                                return
                            Players[charID].tmpPlayer.guildInvitePending=[playerGID,ID]
                            sendDataToPlayer({"p": ServerPackets.SendGuildInvite, 'e': WARNING_WANTS_TO_INVITE_YOU, 't':[getPlayerName(ID),getGuildName(playerGID)]},charID)
                            sendErrorMsg(ID,WARNING_GUILD_INVITE_SENT,[inviteName])
                    else:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[inviteName])
                        return
                elif helpText[0]=='guildkick' and len(helpText)>1:
                    gID = getPlayerGuild(ID)
                    if gID is None:
                        sendErrorMsg(ID,WARNING_YOU_ARE_NOT_IN_A_GUILD)
                        return
                    kickName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=kickName,guildID=getPlayerGuild(ID))
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[kickName])
                        return
                    
                    if gID != getPlayerGuild(charID):
                        sendErrorMsg(ID,WARNING_CHAR_NOT_IN_SAME_GUILD,[kickName])
                        return
                    if getPlayerGuildAccess(ID) < GUILD_MODERATOR or getPlayerGuildAccess(ID)<=getPlayerGuildAccess(charID):
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    sendDataToGuild({"p": ServerPackets.GuildMemberKicked, 'n':kickName,'k':getPlayerName(ID)},gID)
                    leaveGuild(charID)
                    setPlayerGuild(charID,None)
                    if isPlayerOnlineID(charID):
                        sendRefreshNameText(getPlayerName(charID), getPlayerMap(charID))
                elif helpText[0]=='g' and len(helpText)>1:
                    gID = getPlayerGuild(ID)
                    if gID is None:
                        sendErrorMsg(ID,WARNING_YOU_ARE_NOT_IN_A_GUILD)
                        return
                    sendDataToGuild({"p": ServerPackets.PlayerGuildMsg, 'n': Players[ID].name, 'm':newText.split(' ',1)[1]},gID,ignore=True,ID=ID)
                elif helpText[0]=='p' and len(helpText)>1:
                    pID = getPlayerParty(ID)
                    if pID is None:
                        sendErrorMsg(ID,WARNING_YOU_ARE_NOT_IN_A_PARTY)
                        return
                    sendDataToParty({"p": ServerPackets.PlayerPartyMsg, 'n': Players[ID].name, 'm':newText.split(' ',1)[1]},pID,ignore=True,ID=ID)
                elif helpText[0]=='guilddemote' and len(helpText)>1:
                    demoteName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=demoteName,guildID=getPlayerGuild(ID))
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[demoteName])
                        return
                    gID = getPlayerGuild(charID)
                    if gID is None or gID != getPlayerGuild(ID):
                        sendErrorMsg(ID,WARNING_CHAR_NOT_IN_SAME_GUILD,[promoteName])
                        return
                    if getPlayerGuildAccess(ID) != GUILD_OWNER or getPlayerGuildAccess(ID)<=getPlayerGuildAccess(charID) or getPlayerGuildAccess(charID)==GUILD_MEMBER:
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    changeGuildMemberAccess(charID,gID,getPlayerGuildAccess(charID)-1)
                    packet = {"p": ServerPackets.GuildMemberPromoted, 's':False,'n':demoteName,'a':getPlayerGuildAccess(charID),'r':getPlayerName(ID)}
                    sendDataToGuild(packet,gID)
                elif helpText[0]=='guildpromote' and len(helpText)>1:
                    promoteName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=promoteName,guildID=getPlayerGuild(ID))
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[promoteName])
                        return
                    gID = getPlayerGuild(charID)
                    if gID is None or gID != getPlayerGuild(ID):
                        sendErrorMsg(ID,WARNING_CHAR_NOT_IN_SAME_GUILD,[promoteName])
                        return
                    if getPlayerGuildAccess(ID) != GUILD_OWNER or getPlayerGuildAccess(ID)<=getPlayerGuildAccess(charID):
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    changeGuildMemberAccess(charID,gID,getPlayerGuildAccess(charID)+1)
                    packet = {"p": ServerPackets.GuildMemberPromoted, 's':True,'n':promoteName,'a':getPlayerGuildAccess(charID),'r':getPlayerName(ID)}
                    sendDataToGuild(packet,gID)
                    if getPlayerGuildAccess(charID)==GUILD_OWNER:
                        changeGuildMemberAccess(ID,gID,getPlayerGuildAccess(ID)-1)
                        packet2 = {"p": ServerPackets.GuildMemberPromoted, 's':False,'n':getPlayerName(ID),'a':getPlayerGuildAccess(ID),'r':getPlayerName(ID)}
                        sendDataToGuild(packet2,gID)
                elif helpText[0]=='adminsay' and len(helpText)>1:
                    if getPlayerAccess(ID)>0:
                        sendDataToMap({"p": ServerPackets.PlayerChatMsg, 'n': getPlayerName(ID), 'm':newText.split(' ',1)[1], 'a':getPlayerAccess(ID)},getPlayerMap(ID))
                        saveAdminCommand(ID,helpText[0],msg=newText.split(' ',1)[1])
                    else:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                elif helpText[0]=='teleport':
                    if getPlayerAccess(ID)==0:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                        return
                    if len(helpText)<=2:
                        sendErrorMsg(ID,WARNING_WRONG_TELEPORT)
                        return
                    target = helpText[2].split(',')
                    if len(target)==1:
                        targetName = clean_name(target[0]).title()
                        charID = getPlayerId(name=targetName)
                        if charID is None:
                            sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[targetName])
                            return
                        try:
                            teleportedName = clean_name(helpText[1]).title()
                            teleportedCharID=getPlayerId(name=teleportedName)
                            if teleportedCharID is None:
                                sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[teleportedName])
                                return
                            playerTeleport(teleportedCharID,x=getPlayerX(charID),y=getPlayerY(charID),newMapID=getPlayerMap(charID))
                        except Exception, e:
                            print Exception, e, "TELEPORT"
                        saveAdminCommand(ID,helpText[0],msg=' '.join(target))
                    elif len(target)==3 and len(target[0])>1:
                        try:
                            mapID = getMapId(target[0])
                            if canMove(int(target[1]),int(target[2]),mapID,playerType=0):
                                playerTeleport(ID,x=int(target[1]),y=int(target[2]),newMapID=mapID)
                            else:
                                sendErrorMsg(ID,WARNING_WRONG_TELEPORT)
                        except Exception, e:
                            print Exception, e, "TELEPORT"
                        saveAdminCommand(ID,helpText[0],msg=' '.join(target))
                    else:
                        sendErrorMsg(index,WARNING_NOT_ADMIN)
                elif helpText[0]=='mute':
                    if getPlayerAccess(ID)<1:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                        return
                    if len(helpText)<=3:
                        sendErrorMsg(ID,WARNING_WRONG_MUTE)
                        return
                    mutedName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=mutedName)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[mutedName])
                        return
                    try:
                        minutes = int(helpText[2])
                        if minutes>MAX_MUTE_TIME_IN_MINUTES:
                            minutes=MAX_MUTE_TIME_IN_MINUTES
                        elif minutes<0:
                            minutes=1
                        reason=' '.join(helpText[3:])
                        setPlayerMute(charID,True,minutes,reason,ID)
                        sendErrorMsg(ID,WARNING_IS_NOW_MUTED,[mutedName])
                        sendErrorMsg(t=[getPlayerName(ID), str(minutes),reason],error=WARNING_MUTED_YOU,ID=charID)
                        saveAdminCommand(ID,helpText[0],target=charID,length=minutes,msg=reason)
                    except Exception, e:
                        sendErrorMsg(ID,WARNING_WRONG_MUTE)
                        
                elif helpText[0]=='unmute':
                    if getPlayerAccess(ID)==0:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                        return
                    if len(helpText)==1:
                        sendErrorMsg(ID,WARNING_WRONG_UNMUTE)
                        return
                    mutedName = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=mutedName)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[mutedName])
                        return
                    try:
                        setPlayerMute(charID,False)
                        sendErrorMsg(ID,WARNING_IS_NOW_UNMUTED,[mutedName])
                        sendErrorMsg(charID,WARNING_UNMUTED,t=[getPlayerName(ID)])
                        saveAdminCommand(ID,helpText[0],target=charID)
                    except Exception, e: 
                        print Exception, e, "UNMUTE"
                        sendErrorMsg(ID,WARNING_WRONG_UNMUTE)
                elif helpText[0]=='ban':
                    if getPlayerAccess(ID)==0:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                        return
                    if len(helpText)<4:
                        sendErrorMsg(ID,WARNING_WRONG_BAN)
                        return
                    name = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=name)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[name])
                        return
                    try:
                        minutes=int(helpText[2])
                        reason = ' '.join(helpText[3:])
                        sendErrorMsg(ID,WARNING_IS_NOW_BANNED,[name])
                        savePlayerBan(charID,minutes,reason,ID)
                        saveAdminCommand(ID,helpText[0],target=charID,length=minutes,msg=reason)
                        if charID in OnlinePlayers:
                            sendDataToPlayer({"p": ServerPackets.Banned, "d":minutes,"r":reason},charID)
                    except:
                        sendErrorMsg(ID,WARNING_WRONG_BAN)
                        return
                    
                elif helpText[0]=='unban':
                    if getPlayerAccess(ID)==0:
                        sendErrorMsg(ID,WARNING_NOT_ADMIN)
                        return
                    if len(helpText)==0:
                        sendErrorMsg(ID,WARNING_WRONG_UNBAN)
                        return
                    name = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=name)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[name])
                        return
                    banIndex = getPlayerBan(charID)
                    if banIndex is None:
                        sendErrorMsg(ID,WARNING_IS_NOT_BANNED,[name])
                        return
                    removePlayerBan(charID)
                    sendErrorMsg(ID,WARNING_IS_NOW_UNBANNED,[name])
                    saveAdminCommand(ID,helpText[0],target=charID)
                elif helpText[0]=='adminpromote' and len(helpText)==2:
                    if getPlayerAccess(ID)!=ADMIN_CREATOR:
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    name = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=name)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[name])
                        return
                    if getPlayerAccess(charID)>=ADMIN_CREATOR-1:
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    setPlayerAccess(charID,getPlayerAccess(charID)+1)
                elif helpText[0]=='admindemote' and len(helpText)==2:
                    if getPlayerAccess(ID)!=ADMIN_CREATOR:
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    name = clean_name(helpText[1]).title()
                    charID = getPlayerId(name=name)
                    if charID is None:
                        sendErrorMsg(ID,WARNING_CHAR_NOT_FOUND,[name])
                        return
                    if getPlayerAccess(charID)==0 or getPlayerAccess(charID)==ADMIN_CREATOR:
                        sendErrorMsg(ID,WARNING_NOT_ACCESS)
                        return
                    setPlayerAccess(charID,getPlayerAccess(charID)-1)
                
                else:
                    sendErrorMsg(ID,WARNING_HELP)
                
            else:
                sendErrorMsg(ID,WARNING_HELP)
        else:
            if Players[ID].tmpPlayer.muted is not None:
                seconds = (Players[ID].tmpPlayer.muted-g.lastTick)/1000
                if seconds<=0:
                    setPlayerMute(ID,False)
                    sendDataToMap({"p": ServerPackets.PlayerChatMsg, 'n': Players[ID].name, 'm':newText},getPlayerMap(ID),ignore=True,ID=ID)
                else:
                    sendErrorMsg(t=[getPlayerMuteReason(ID),str(seconds)],error=WARNING_YOU_ARE_MUTED,ID=ID)
            else:
                sendDataToMap({"p": ServerPackets.PlayerChatMsg, 'n': Players[ID].name, 'm':newText},getPlayerMap(ID),ignore=True,ID=ID)
    def handleTalkWithNpc(self,ID,npcName):
        mapID=getPlayerMap(ID)
        npcIndex=getNpcListIndex(npcName,mapID)
        dist = distance(getPlayerX(ID),getPlayerY(ID),Maps[mapID].npcs[npcIndex].x,Maps[mapID].npcs[npcIndex].y)
        Players[ID].tmpPlayer.talkingTo=npcName
        if dist<=MAX_NPC_TALK_DISTANCE:
            Maps[mapID].npcs[npcIndex].tmpPlayer.talkingTo=ID
            dir = getDirectionFromOffset(checkPlayerOffset(getPlayerX(ID),Maps[mapID].npcs[npcIndex].x,getPlayerY(ID),Maps[mapID].npcs[npcIndex].y))
            self.handleFaceTarget(ID,Maps[mapID].npcs[npcIndex].x,Maps[mapID].npcs[npcIndex].y)
            if not Maps[mapID].npcs[npcIndex].tmpPlayer.moving:
                Maps[mapID].npcs[npcIndex].dir=dir
                sendDataToMap({"p": ServerPackets.SendNpcDir, "n":Maps[mapID].npcs[npcIndex].name, "d":Maps[mapID].npcs[npcIndex].dir},mapID)
            else:
                Maps[mapID].npcs[npcIndex].tmpPlayer.nextDir=dir
        #else:
        #    Players[SendNpcDir].tmpPlayer.movePathTmp = [Maps[mapID].npcs[npcIndex].x,Maps[mapIndex].npcs[npcIndex].y] #
    def handleStopTalkWithNPC(self,ID,npcName):
        mapID=getPlayerMap(ID)
        npcIndex=getNpcListIndex(npcName,mapID)
        if Maps[mapID].npcs[npcIndex].tmpPlayer.talkingTo == ID:
            Maps[mapID].npcs[npcIndex].tmpPlayer.talkingTo = None
            Maps[mapID].npcs[npcIndex].tmpPlayer.nextDir=None
        Players[ID].tmpPlayer.talkingTo=None#
    def handleMovePath(self,ID,path):
        mapID = getPlayerMap(ID)
        for step in path:
            if Maps[mapID].tile[step[0]][step[1]].t==TILE_TYPE_BLOCKED:
                return
        Players[ID].tmpPlayer.movePath=path
        sendDataToMap({"p": ServerPackets.PlayerMovePath, 'n':getPlayerName(ID),"pa":list(path)},mapID)
        if len(path)>0:
            chg = checkPlayerOffset(path[0][0],Players[ID].x,path[0][1],Players[ID].y)
            dir = getDirectionFromOffset(chg)
            if Players[ID].tmpPlayer.moving:
                Players[ID].tmpPlayer.nextMoveDir = dir
            else:
                handleMovement(dir,ID,path=True)
                del Players[ID].tmpPlayer.movePath[0]
                if len(Players[ID].tmpPlayer.movePath)==0:
                    Players[ID].tmpPlayer.toStop = True
                else:
                    Players[ID].tmpPlayer.toStop = False
    def handleFaceTarget(self,ID,x,y):
        if not isEligible(ID):
            return
        if not Players[ID].tmpPlayer.moving:
            direction = getDirectionFromOffset(checkPlayerOffset(x,Players[ID].x,y,Players[ID].y))
            if direction != Players[ID].dir:
                Players[ID].dir = direction
                sendDataToMap({"p": ServerPackets.PlayerDirection, 'd': Players[ID].dir, 'n':Players[ID].name},getPlayerMap(ID))
    def stopMove(self,ID):
        if not isEligible(ID):
            return
        Players[ID].tmpPlayer.nextMoveDir = -1
        Players[ID].tmpPlayer.movePath[:] = []
        sendDataToMap({"p": ServerPackets.PlayerMoveStop, 'n': Players[ID].name, "x":Players[ID].x , "y":Players[ID].y,'d':Players[ID].dir},getPlayerMap(ID))
    def handleMove(self,ID,direction):
        handleMovement(direction,ID)
    def handleLeaveGuild(self,ID):
        gID = getPlayerGuild(ID)
        access=getPlayerGuildAccess(ID)
        if gID is not None:
            sendLeftGuild(ID,gID)
            leaveGuild(ID)
            Players[ID].guildID=None
            if len(Guilds[gID].members)==0:
                del Guilds[gID]
                return
            if access==GUILD_OWNER:
                newOwnerID=None
                for member in Guilds[gID].members:
                    if member.guildAccess==GUILD_MODERATOR:
                        newOwnerID=member.charID
                if newOwnerID==None:
                    newOwnerID = Guilds[gID].members[0].charID
                Players[newOwnerID].guildAccess=GUILD_OWNER
                for member in Guilds[gID].members:
                    if member.charID==newOwnerID:
                        member.guildAccess=GUILD_OWNER
                sendDataToGuild({"p": ServerPackets.GuildMemberPromoted, 's':True,'n':getPlayerName(newOwnerID),'a':getPlayerGuildAccess(newOwnerID),'r':getPlayerName(newOwnerID)},gID)
    def handleCreateGuild(self, ID,guildName):
        if Players[ID].guildID != None:
            sendErrorMsg(ID,WARNING_PLAYER_ALREADY_IN_GUILD)
            return
        gnameTmp = ''.join(char for char in guildName if special_match(char))
        guildname = " ".join(gnameTmp.split()).lstrip().rstrip()
        if len(guildname)<3 or len(guildname)>24:
            sendErrorMsg(ID,WARNING_INVALID_GUILD_NAME,[guildname])
            return
        guildID = getGuildID(guildname)
        if guildID is None:
            createGuild(guildname,ID)
            sendGuildmembersToPlayer(ID)
            guildID = getGuildID(guildname)
            sendJoinedGuild(ID,guildID)
        else:
            sendErrorMsg(ID,WARNING_GUILD_NAME_EXISTS,[guildname])
    def handleLatencyTick(self,ID):
        Players[ID].tmpPlayer.latencyTick = time.time()*1000
        sendDataToPlayer({"p":ServerPackets.LatencyTick},ID)
        #Players[ID].packet.append({"p":ServerPackets.LatencyTick})
    def handleNameMene(self, ID,name):
        if doesPlayerHaveMene(ID,Players[ID].tmpPlayer.namingMeneID):
            Players[ID].tmpPlayer.namingMeneID=None
            return
        if Players[ID].tmpPlayer.namingMeneID is None:
            return
        realName = ''.join(char for char in name if special_match(char))
        if len(realName)==0 and len(realName)<13:
            return
        Players[ID].tmpPlayer.creatingChar=False
        if len(Players[ID].menes)==0:
            savePlayerMene(ID,Players[ID].tmpPlayer.namingMeneID,realName,Players[ID].tmpPlayer.namingMeneLevel,MENE_INVENTORYTYPE_DEFAULT,getMeneStats(Players[ID].tmpPlayer.namingMeneLevel,Players[ID].tmpPlayer.namingMeneID))
            Players[ID].tmpPlayer.namingMeneID =None
            Players[ID].tmpPlayer.namingMeneLevel=1
            sendLoginStuff(ID)
        else:
            savePlayerMene(ID,Players[ID].tmpPlayer.namingMeneID,realName,Players[ID].tmpPlayer.namingMeneLevel,MENE_INVENTORYTYPE_CARRYING,getMeneStats(Players[ID].tmpPlayer.namingMeneLevel,Players[ID].tmpPlayer.namingMeneID))
            Players[ID].tmpPlayer.namingMeneID =None
            Players[ID].tmpPlayer.namingMeneLevel=1
            sendMenesToPlayer(ID)
        
        
    def handleCreateChar(self, ID,shirt,shoes,face,hat):
        if shirt>MAX_SHIRT:
            shirt=MAX_SHIRT
        if shoes>MAX_SHOES:
            shoes=MAX_SHOES
        if face>MAX_FACE:
            face=MAX_FACE
        if hat>MAX_HAT:
            hat=MAX_HAT
        setPlayerShirt(ID,shirt)
        setPlayerShoes(ID,shoes)
        setPlayerFace(ID,face)
        setPlayerHat(ID,hat)
        setPlayerMap(ID,getMapId(DEFAULT_MAP))
        setPlayerX(ID,DEFAULT_X)
        setPlayerY(ID,DEFAULT_Y)
        mene=getMene(spriteName=DEFAULT_MENE)
        Players[ID].tmpPlayer.namingMeneID =mene.id
        Players[ID].tmpPlayer.namingMeneLevel=1
        sendDataToPlayer({"p": ServerPackets.CreateMeneInit,'s':mene.spriteName},ID)
        setPlayerAchievement(ID,getAchievementId("Create Character"))
    def handleLogin(self,unauthIndex,key):
        for i in range(len(authTokens)):
            if authTokens[i].token == key and authTokens[i].ip == g.conn.factory.unauthClients[unauthIndex].connection.transport.client[0]:
                ID = getPlayerId(wwwID =authTokens[i].wwwID)
                if ID is not None:
                    #Character exists
                    Players[ID].connection=g.conn.factory.unauthClients[unauthIndex].connection
                    Players[ID].tmpPlayer = TmpPlayer()
                    OnlinePlayers.append(ID)
                    if ID not in DatabaseSavings["players"]:
                        DatabaseSavings["players"].append(ID)
                    if not getAchievementId("Create Character") in Players[ID].achievements:
                        sendDataToPlayer({"p": ServerPackets.CreateCharInit,"n":getPlayerName(ID),'c':ClothingPairs},ID)
                        Players[ID].tmpPlayer.creatingChar=True
                    elif len(Players[ID].menes)==0:
                        mene=getMene(spriteName=DEFAULT_MENE)
                        Players[ID].tmpPlayer.namingMeneID =mene.id
                        Players[ID].tmpPlayer.namingMeneLevel=1
                        sendDataToPlayer({"p": ServerPackets.CreateMeneInit,'s':mene.spriteName},ID)
                        Players[ID].tmpPlayer.creatingChar=True
                    else:
                        
                        sendLoginStuff(ID)
                else:
                    #First-Timer
                    ID = insertPlayerToDb(authTokens[i].wwwID,authTokens[i].username)
                    Players[ID].connection=g.conn.factory.unauthClients[unauthIndex].connection
                    Players[ID].tmpPlayer = TmpPlayer()
                    OnlinePlayers.append(ID)
                    DatabaseSavings["players"].append(ID)
                    sendDataToPlayer({"p": ServerPackets.CreateCharInit,"n":getPlayerName(ID),'c':ClothingPairs},ID)
                    Players[ID].tmpPlayer.creatingChar=True
                    
                del g.conn.factory.unauthClients[unauthIndex]
                del authTokens[i]
                return