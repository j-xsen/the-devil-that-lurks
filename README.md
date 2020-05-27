![logo](https://raw.githubusercontent.com/jaxsenh/the-devil-that-lurks/master/client/img/png/logo.png "logo")

Hello! First of all, thank you for checking out my game! Before downloading, please note that this is early in development. Not all gameplay features have been implemented nor any visual appeal, though that'll probably be beyond obvious beyond launch. If you find any issues that are like in need of immediate fixing, or you just wanna chat, you can email me at [jaxsenhoneycutt@gmail.com](mailto:jaxsenhoneycutt@gmail.com "jaxsenhoneycutt(@)gmail.com")

# How to Play
## Requirements
- [Python 3.8](https://www.python.org/downloads/ "Python 3.8")
- [Panda3D](https://www.panda3d.org/download/ "Panda3d")

## Running the Game
1. Launch the server by running `server/base.py`.
2. Launch the client by running `client/base.py`.

Currently, the game defaults to running off a `localhost` server. If you desire to change this, change the value of `ip_address` in the function `connect()` of `client/base.py`.

# How the Codebase Works
Pretty self-explanatory, the source for the server can be found in the `server` folder, and the client source can be found in the `client` folder.

## Client
`base.py` is the base of the client, as the name describes. `father.py` is a child of `base.py` that holds all levels and enables a communication between the server and the client. Base receives the server's message and uses Father to direct it correctly. Father also has essential functions like `write` and `set_active_level`. Children of the Father object have access to said Father object so they can access these essential functions.

## Server
The server operates mainly through `base.py`. Through this, it creates games (`objects/game.py`), which holds players (`objects/player.py`) and AI (`objects/ai.py`).

## Adding Messages
Adding a new message is pretty simple. First, you need to choose a message code. All of these are defined in both `client/codes.py` and `server/codes.py`. These are currently limited from 0 - 255 due to how the messages are sent.

### Client Functionality
#### Send
Sending a message to the server is made pretty simple through the use of the `father.py` object. Father has a function called `write` that is able to send a message for you. It takes one parameter of a PyDatagram. All PyDatagrams are defined via functions in `communicator.py`. Further information on constructing PyDatagrams can be found in the [Panda3D manual](https://docs.panda3d.org/1.10/python/programming/networking/datagram-protocol/transmitting-data#sending-a-message "Panda3D manual").

#### Receive
Messages from the server are sent to the `base.py` function `tsk_reader`. After some code, the message code is stored in the variable `msg_id`. You can then use this variable to check if it matches a message code as stored in `codes.py`. If your message contains more data, that can be retrieved by iterator.get*whatever bit type*(). This is explained much better in the actual [Panda3D documentation](https://docs.panda3d.org/1.10/python/programming/networking/datagram-protocol/transmitting-data#receiving-a-message "Panda3D documentation").

### Server Functionality
#### Send
In the game object, there's a few helpers built to make communication with clients easier: `message_player`, `message_all_players`, and `message_killer`. All of these take the parameter of `dg`, which is a PyDatagram. All of these are defined via functions in `communicator.py`. Further information on constructing PyDatagrams can be found in the [Panda3D manual](https://docs.panda3d.org/1.10/python/programming/networking/datagram-protocol/transmitting-data#sending-a-message "Panda3D manual").

#### Receive
In `base.py`, there's a function, `tsk_reader_polling`, that is called every time the server is sent a message from a client. After a bit of work, the message code is stored in the variable `msg_id`. This can be used to compare to whatever code you desire and add functionality. If your message contains more data, that can be retrieved by iterator.get*whatever bit type*(). This is explained much better in the actual [Panda3D documentation](https://docs.panda3d.org/1.10/python/programming/networking/datagram-protocol/transmitting-data#receiving-a-message "Panda3D documentation"). Of note, most iterator.get() functions are in a try block to try to prevent anyone from sending an invalid packet of data and causing the entire server to crash. These instances are logged, however.
