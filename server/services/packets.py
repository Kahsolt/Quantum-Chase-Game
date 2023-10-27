#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/26

from enum import Enum

from flask import request
from flask_socketio import SocketIO, emit

from services.models import Role, ALICE, BOB
from services.models import Game, Player
from services.runtime import Env, Runtime
from services.utils import *


'''
{
  // some stuff
}
'''
Payload = Dict[str, Any]
'''
{
  'ok': bool
  'data': list|dict
  'error': str
  'ts': timestamp
}
'''
Resp = Dict[str, Any]

class Recp(Enum):
  ''' response recipient '''
  ALL  = 'all'   # broadcast
  ROOM = 'room'  # game room
  ONE  = 'one'   # p2p

HandlerRet = Union[Tuple[Resp, Recp], Resp]
Handler = Callable[[Payload, Union[Env, Runtime]], HandlerRet]
Handled = Callable[[Payload, Union[Env, Runtime]], None]

PREFIX_HANDLER = 'handle_'
PREFIX_EMITTER = 'emit_'


def resp_ok(data:Union[dict, list]=None) -> Resp:
  return {
    'ok': True,
    'data': data,
    'ts': now_ts(),
  }


def resp_error(err:str) -> Resp:
  import gc ; gc.collect()
  return {
    'ok': False,
    'error': err,
    'ts': now_ts(),
  }


def check_payload(payload:Payload, keys:List[Union[str, Tuple[str, type]]]):
  keys_missing: List[str] = []
  wrong_type: List[str] = []
  for key in keys:
    key, typ = key if isinstance(key, tuple) else (key, object)
    if key not in payload:
      keys_missing.append(key)
    if not isinstance(payload[key], typ):
      wrong_type.append(key)
  if keys_missing or wrong_type:
    errors = []
    if keys_missing: errors.append('missing keys: ' + ','.join(keys_missing))
    if wrong_type: errors.append('wrong type keys: ' + ','.join(wrong_type))
    raise ValueError(', '.join(errors))


def get_me(g:Game) -> Tuple[int, Player]:
  id = g.me[request.sid]
  return id, g.players[id]


def get_rival(me:Role) -> Role:
  return ALICE if me == BOB else ALICE


def mk_payload_loc(g:Game, id:str=None) -> Resp:
  if id is None:
    return { id: g.players[id].loc for id in g.players }
  else:
    return {
      'id': id,
      'loc': g.players[id].loc,
    }
