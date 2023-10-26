#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/26

from dataclasses import dataclass, field
from threading import Event
from enum import Enum

from flask import request
from flask_socketio import SocketIO, emit

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

@dataclass
class Env:
  # ctx
  sio: SocketIO
  # sid => rid|None
  conns: Dict[str, Optional[str]] = field(default_factory=dict)
  # rid => sid => r
  waits: Dict[str, Dict[str, int]] = field(default_factory=dict)
  # rid => game
  games: Dict[str, Game] = field(default_factory=dict)
  # rid => Event, stop signal for all thread workers of a Game
  signals: Dict[str, Event] = field(default_factory=dict)
  # rid => List[SpawnItem]
  spawns: Dict[str, List['SpawnItem']] = field(default_factory=dict)

HandlerRet = Union[Tuple[Resp, Recp], Resp]
Handler = Callable[[Payload, Union[Env, Game]], HandlerRet]

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
    if wrong_type: errors.append('wrong type: ' + ','.join(wrong_type))
    raise ValueError(', '.join(errors))


def get_me(g:Game) -> Tuple[int, Player]:
  id = g.me[request.sid]
  return id, g.players[id]
