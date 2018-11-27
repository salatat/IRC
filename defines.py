NEW_CONN              = 1 << 0
LIST_ROOMS            = 1 << 1
CREATE_ROOM           = 1 << 2
JOIN_ROOM             = 1 << 3
LEAVE_ROOM            = 1 << 4
LIST_MEMBERS          = 1 << 5
MSG_ROOM              = 1 << 6
PRIV_MSG              = 1 << 7
DISCONNECT            = 1 << 8
ERR_CREATE_ROOM       = 1 << 9
ERR_JOIN_ROOM         = 1 << 10
ERR_LEAVE_ROOM        = 1 << 11
ERR_LIST_MEMBERS      = 1 << 12
ERR_MSG_ROOM          = 1 << 13
ERR_PRIV_MSG          = 1 << 14

SERVER_MSG            = 1 << 31

SRVR_LIST_ROOMS       = SERVER_MSG | LIST_ROOMS
SRVR_CREATE_ROOM      = SERVER_MSG | CREATE_ROOM
SRVR_JOIN_ROOM        = SERVER_MSG | JOIN_ROOM
SRVR_LEAVE_ROOM       = SERVER_MSG | LEAVE_ROOM
SRVR_LIST_MEMBERS     = SERVER_MSG | LIST_MEMBERS
SRVR_MSG_ROOM         = SERVER_MSG | MSG_ROOM
SRVR_DISCONNECT       = SERVER_MSG | DISCONNECT
SRVR_ERR_CREATE_ROOM  = SERVER_MSG | ERR_CREATE_ROOM
SRVR_ERR_JOIN_ROOM    = SERVER_MSG | ERR_JOIN_ROOM
SRVR_ERR_LEAVE_ROOM   = SERVER_MSG | ERR_LEAVE_ROOM
SRVR_ERR_LIST_MEMBERS = SERVER_MSG | ERR_LIST_MEMBERS
SRVR_ERR_MSG_ROOM     = SERVER_MSG | ERR_MSG_ROOM
SRVR_ERR_PRIV_MSG     = SERVER_MSG | ERR_PRIV_MSG

HOST                  = '127.0.0.1'
PORT                  = 51234