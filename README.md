# Spurdola (servers)

## About
Spurdola is a (unfinished) Pyglet-based multiplayer RPG game that utilizes twisted. The Python version used is 2.7. 

The server repository includes
- Game server
- Update server
- Login server
- Website (for registering accounts and downloading the game)

The coding style is not very pretty.

This repository is about the server-side of the game. The client-side has its own repository [own repository](https://github.com/sakkee/Spurdola-client).

## Installation
The servers can be hosted on different hosts. Note that the login server and the website utilize the same database.

### Website
The website uses PHP5 and MySQL. The Spurdola.zip is for simple downloading the (client) version of the game.

1. Create a MySQL database with a table www_accounts, the table should have the following fields: id (INT, primary key, auto_increment), username (varchar), password (varchar)
2. Change the domain names in the files
3. Update the fields in inc/registration.php

### Login server
Following libraries are needed:
- Crypto
- twisted
- bcrypt
- pymysql

Update the database variables (to match with the website's database)

Running:

```
python server.py
```

Please note:

- `loginAuthKey` variable should be the same as in the game server's globalvars.py file for authorization. 

- `GAME_VERSION` variable should be updated whenever an update is rolled to the client side (and it should match with the client version's `GAME_VERSION`)

- If hosted on the same server with the game server and/or update server, the port should be unique.

- You can run multiple python servers in linux by using `screen` terminal command



### Game server

Following libraries are needed:
- twisted
- Crypto
- pymysql

1. Create a MySQL database
2. Define the database variables and `LOGINSERVERDOMAIN` in constants.py
3. Define the `loginAuthKey` in globalvars.py (should match with the login server's variable)

Running:

```
python server.py
```

Please note:

- If hosted on the same server with the login server and/or update server, the port should be unique.


### Update server

The contents of the update server should include:
- Up-to-date DATA folder of the client game
- Compiled Spurdola.exe, MapCreator.exe and NpcCreator.exe

Following libraries are needed:
- twisted

Running:
```
python updater.py
```
