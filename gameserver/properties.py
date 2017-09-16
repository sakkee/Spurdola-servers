#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from constants import *
from objects import *
import os
import globalvars as g
import json
import random

mapIds = {
    'Start':0,
    'Road Two':1,
    'Gaubs 1': 2,
    'Manual Breathing': 3
}
def constructItemList():
    Items['es'] = {'id':'es','name':'ES Energy Drink','info':'Use to catch a mene :DD','cost':1,'sprite':'es'}
def constructClothingPairs():
    ClothingPairs.append({'hat':1,'shirt':1,'type':'exclude'})
    ClothingPairs.append({'hat':2,'shirt':1,'type':'exclude'})
    ClothingPairs.append({'hat':3,'shirt':1,'type':'exclude'})
def constructAchievementList():
    Achievements[0]=Achievement(id=0,name='Create Character',info='Player has created a character.')
    #Achievements[1]=Achievement(id=1,name="Name Your Mene",info='Player has named a mene.')
def constructMeneList():
    Menes[0]=Menemon(id=0,name="Uusi Mene",hp=68,power=75,defense=70,speed=66,spriteName="uusimene",attack1=getAbilityId("Basic Attack"),attack2=getAbilityId("Basic Heal"))
    Menes[1]=Menemon(id=1,name="Le American Bear",hp=72,power=64,defense=79,speed=61,spriteName="americanbear",attack1=getAbilityId("Basic Attack"),attack2=getAbilityId("Basic Heal"))
    Menes[2]=Menemon(id=2,name=unicode("Lörs lärä",'ISO-8859-1'),hp=45,power=96,defense=45,speed=79,spriteName="lorslara",attack1=getAbilityId("Ketsub :D"),attack2=getAbilityId("Ketsub :D"),attack3=getAbilityId("Ketsub :D"),attack4=getAbilityId("Ketsub :D"))
    Menes[3]=Menemon(id=3,name="Squad Lider",hp=65,power=77,defense=67,speed=75,spriteName="squadlider",attack1=getAbilityId("Scratch"),attack2=getAbilityId("Basic Heal"))
    Menes[4]=Menemon(id=4,name="Le Mongol Bear",hp=55,power=94,defense=49,speed=76,spriteName="mongolbear",attack1=getAbilityId("Basic Attack"),attack2=getAbilityId("Basic Heal"))
    Menes[5]=Menemon(id=5,name="Suomi",hp=62,power=62,defense=75,speed=66,spriteName="mongol",attack1=getAbilityId("Basic Attack"),attack2=getAbilityId("Basic Heal"))
    
def constructAbilityList():
    #abilityList = []
    #length (rounds): 0 buff, 1 instant attack, 2+ DoT/HoT
    #targetType (N(targets)): 1+ targets
    #missChance (%)
    #critChance (%)
    #targetFactor: enemy team, my team, everybody
    #power: base power IF ability type damage, % else
    #abilityType: attack, heal, buff,...
    Abilities[0] = Ability(id=0,name="Basic Attack",infotext="Deals damage to enemy darged :DDD.",length=1,targetType=1,missChance=5,critChance=15,targetFactor=ENEMY_TEAM,abilityType=ABILITY_TYPE_ATTACK,power=50,spriteName='basic_attack',animation='blood1')
    Abilities[1] = Ability(id=1,name="Basic Heal",infotext="Heals a friendly homo for 25 % HP.",length=1,targetType=1,missChance=0,critChance=10,targetFactor=OWN_TEAM,abilityType=ABILITY_TYPE_HEAL,power=25,spriteName='basic_heal',animation='heal1')
    Abilities[2] = Ability(id=2,name="Ketsub :D",infotext="Spills getsub on enemy and deals damage :D",length=1,targetType=1,missChance=15,critChance=30,targetFactor=ENEMY_TEAM,abilityType=ABILITY_TYPE_ATTACK,power=68,spriteName='ketchup',animation='lorslara1')
    Abilities[3] = Ability(id=3,name="Scratch",infotext="Sgratch the enemy :D",length=1,targetType=1,missChance=10,critChance=20,targetFactor=ENEMY_TEAM,abilityType=ABILITY_TYPE_ATTACK,power=70,spriteName='scratch',animation='blood1')

    #return abilityList
    
def calculateHP(level,hp,npc=False):
    if npc:
        return int(((hp*2*level)/100.0+level+10)*NPC_STAT_LOWER)
    else:
        return int((hp*2*level)/100.0+level+10)
def calculateStat(level,stat,npc=False):
    if npc:
        return int(((stat*2*level/100.0)+5)*NPC_STAT_LOWER)
    else:
        return int((stat*2*level/100)+5)
def calculateHeal(defenderMeneHpMax,abilityPower,attack_rng):
    return int(defenderMeneHpMax*(abilityPower/100.0)*attack_rng)
def calculateDamage(attackerLevel,attackerPower,targetDefense,abilityPower,rng):
    modifier = rng*random.uniform(0.80,1.0)
    return int(((2*attackerLevel+10)/250.0*(attackerPower/float(targetDefense))*abilityPower)*modifier)
    
def calculateMoneyReceived(enemyLevel):
    #baseMoney = enemyLevel*3
    return random.randint(0,enemyLevel*5)
    #return int(baseMoney+random.randint(int(-baseMoney*0.5),int(baseMoney*0.5)))
def getLevelByXp(xp):
    return int(xp**(1.0/2.999999999)) #ebin
def calculateXpNeeded(level):
    return level**3
    
def calculateXpGain(enemyMeneLevel,playerMeneLevel):
    #print (50*enemyMeneLevel)/(7*(playerMeneLevel/float(enemyMeneLevel))), print playerMeneLevel/float(enemyMeneLevel), print 7*(playerMeneLevel/float(enemyMeneLevel)), print 50*enemyMeneLevel
    #print (50*enemyMeneLevel)/(7*playerMeneLevel*((playerMeneLevel+5)/float(enemyMeneLevel+5))), (7*playerMeneLevel*((playerMeneLevel+5)/float(enemyMeneLevel+5)))
    return int((50*enemyMeneLevel)/7.0)
    #return int((50*enemyMeneLevel)/(7*playerMeneLevel*((playerMeneLevel+5)/float(enemyMeneLevel+5))))
def getAchievementId(achievementName=None):
    if achievementName is not None:
        for id, achievement in Achievements.iteritems():
            if achievement.name==achievementName:
                return id
    return None
def getAbilityId(abilityName=None):
    if abilityName is not None:
        for id, ability in Abilities.iteritems():
            if ability.name==abilityName:
                return id
    return None
def getMapName(mapID):
    for map, id in mapIds.iteritems():
        if id==mapID:
            return map
    return None
def getMapId(mapName):
    return mapIds[mapName]
def getMeneId(spriteName=None):
    if spriteName is not None:
        for id, mene in Menes.iteritems():
            if mene.spriteName==spriteName:
                return id
    return None
def loadNPC(filename):
    with open(g.dataFolder+ '/npc/' + filename,'r') as fp:
        npc=json.load(fp)
    for c in npc["m"]:
        mapID = getMapId(str(c[0]))
        newNPC = NPCClass(name=filename[:-4],hat=npc["h"],dir=c[3],shirt=npc["s"],shoes=npc["sh"],face=npc["fa"],text=npc["te"],radius=npc["r"],walkingType=npc["t"],x=c[1],y=c[2],actionType=npc["type"],map=mapID)
        Maps[mapID].npcs.append(newNPC)
        
def loadNPCs():
    for filename in os.listdir(g.dataFolder+'/npc/'):
        loadNPC(filename)
def loadMaps():
    for filename in os.listdir(g.dataFolder + '/maps/'):
        loadMap(filename)
def loadMap(filename):
    if filename=='tmp':
        return
    with open(g.dataFolder+ '/maps/' + filename,'r') as fp:
        tmpMap=json.load(fp)
        
    newMap = MapClass()
    newMap.name = filename.split(".")[0]
    newMap.width = tmpMap["width"]
    newMap.height = tmpMap["height"]
    newMap.song = tmpMap["song"]
    newMap.death[:]=tmpMap["death"]
    for i in range(len(tmpMap["menes"])):
        probability = tmpMap["menes"][i][1]
        if probability == SHOWUP_NORMAL:
            newMap.meneEncounter+=SHOWUP_NORMAL
        elif probability == SHOWUP_UNCOMMON:
            newMap.meneEncounter+=SHOWUP_UNCOMMON
        elif probability == SHOWUP_RARE:
            newMap.meneEncounter+=SHOWUP_RARE
        newMap.menes.append(MapMene(getMeneId(spriteName=tmpMap["menes"][i][0]),probability,tmpMap["menes"][i][2],tmpMap["menes"][i][3],newMap.meneEncounter))
    newMap.tile = [[TileClass() for i in range(tmpMap["height"])] for i in range(tmpMap["width"])]
    tmpTiles = []
    for x in range(tmpMap["width"]):
        tmpTilesW=[]
        for y in range(tmpMap["height"]):
            tmpTile = TileClass()
            #tmpTile.l1 = tmpMap['tile'][x][y]["l1"]
            #tmpTile.l2 = tmpMap['tile'][x][y]["l2"]
            #tmpTile.l3 = tmpMap['tile'][x][y]["l3"]
            #tmpTile.f = tmpMap['tile'][x][y]["f"]
            tmpTile.t = tmpMap['tile'][x][y]["t"]
            tmpTile.d1 = tmpMap['tile'][x][y]["d1"]
            tmpTile.d2= tmpMap['tile'][x][y]["d2"]
            tmpTile.d3 = tmpMap['tile'][x][y]["d3"]
            tmpTilesW.append(tmpTile)
        tmpTiles.append(tmpTilesW)
    newMap.tile = tmpTiles
    
    
    
    mapID = getMapId(newMap.name)
    newMap.id=mapID
    #newMap.walls=walls
    Maps[mapID]=newMap