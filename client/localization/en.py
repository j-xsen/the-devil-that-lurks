# error codes
from communications.codes import GAME_DELETED, ALREADY_IN_GAME, GENERAL, LEFT_GAME, NO_HEART, CLIENT_LOG_OFF
from communications.codes import SERVER_KILLED_CONNECTION

LOCAL_EN = {
    GAME_DELETED: 'This game has ended!',
    ALREADY_IN_GAME: 'You were already in a game! We went ahead and removed you.',
    GENERAL: 'You have been kicked from this game.',
    LEFT_GAME: 'You have left this game.',
    NO_HEART: 'Server assumed you were dead.',
    CLIENT_LOG_OFF: 'You logged off.',
    SERVER_KILLED_CONNECTION: 'Lost connection to the server!',
    -1: 'Debug',
    -2: 'Failed to connect!'
}
