from Crypto.PublicKey import RSA
from Crypto import Random

conn = None

loginServer = None
loginServerIP = None #gets the IP on launch, used to authenticate the login server
loginAuthKey = '' #The auth key for loginserver
KEY_LENGTH = 2048
random_gen = Random.new().read
privatekey = RSA.generate(KEY_LENGTH,random_gen)
publickey = privatekey.publickey().exportKey()
possibleLoginServer=None

lastTick=0

lastPartyID=0
lastMatchID=0

dataFolder='data'