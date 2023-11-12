#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/26

import gc
import inspect
from enum import Enum

from flask import request
from flask_socketio import SocketIO, emit

from services.runtime import Env, Runtime
from services.shared import *
from services.utils import *

'''
{
  'ok': bool
  'data': dict|list
  'error': str
  'ts': timestamp
}
'''
DataDict = Dict[str, Any]
DataList = List[Any]
Data = Union[DataDict, DataList]
Response = Dict[str, Any]
Payload = Dict[str, Any]

class Recp(Enum):
  ''' response recipient '''
  ALL  = 'all'   # broadcast all
  ROOM = 'room'  # broadcast game room
  ONE  = 'one'   # only to the sender

HandlerRet = Union[
  Response,                 # Recp defaults to ONE
  Tuple[Response, Recp],
]
Handler = Callable[[Payload, Union[Env, Runtime]], HandlerRet]
Handled = Callable[[Payload, Union[Env, Runtime]], None]

PREFIX_HANDLER = 'handle_'
PREFIX_EMITTER = 'emit_'

resp_error_count = 0


def name_func_to_event(name:str) -> str:
  stem = None
  if name.startswith(PREFIX_HANDLER): stem = name[len(PREFIX_HANDLER):]
  if name.startswith(PREFIX_EMITTER): stem = name[len(PREFIX_EMITTER):]
  if stem is None: raise ValueError(f'unknown name: {name}')
  return stem.replace('_', ':')

def _is_handler_no_rt(func:Callable):
  sig = inspect.signature(func)
  for k, v in sig.parameters.items():
    if v.annotation is Runtime: return False
  return True

def make_handler(env:Env, func:Handler) -> Handled:
  def wrapper(payload:Payload):
    evt = name_func_to_event(func.__name__)
    sid = request.sid
    rid = env.conns.get(sid)
    print(f'[{evt}] sid: {sid}, rid: {rid}')
    print(f'payload: {payload}')
    if _is_handler_no_rt(func):
      ret = func(payload, env)
    else:
      rt = env.games.get(rid)
      ret = func(payload, rt)
    if ret is None:
      return
    elif isinstance(ret, tuple):
      resp, recp = ret
    else:
      resp, recp = ret, Recp.ONE
    check_response(resp)
    print(f'resp: <{recp.value}> {resp}')
    if   recp == Recp.ALL:  env.sio.emit(evt, resp)
    elif recp == Recp.ROOM: env.sio.emit(evt, resp, to=rid)
    elif recp == Recp.ONE:  env.sio.emit(evt, resp, to=sid)
  return wrapper


def resp_error(err:str) -> Response:
  global resp_error_count
  resp_error_count += 1
  if resp_error_count >= 100:
    gc.collect()
    resp_error_count = 0

  return {
    'ok': False,
    'error': err,
    'ts': now_ts(),
  }

def resp_ok(data:Data=None) -> Response:
  return {
    'ok': True,
    'data': data,
    'ts': now_ts(),
  }


def check_payload(payload:Payload, keys:List[Union[str, Tuple[str, type]]]):
  keys_missing: List[str] = []
  type_wrong:   List[str] = []
  for key in keys:
    key, typ = key if isinstance(key, tuple) else (key, object)
    if key.endswith('?'):
      key = key[:-1]
      if key in payload and not payload[key] is None and not isinstance(payload[key], typ):
          type_wrong.append(key)
    else:
      if key not in payload:
        keys_missing.append(key)
      if not isinstance(payload[key], typ):
        type_wrong.append(key)
  if keys_missing or type_wrong:
    errors = []
    if keys_missing: errors.append('missing keys: ' + ', '.join(keys_missing))
    if type_wrong:   errors.append('wrong types: '  + ', '.join(type_wrong))
    raise ValueError('; '.join(errors))

def check_response(resp:Response):
  assert 'ok' in resp, 'response missing "ok"'
  assert 'ts' in resp, 'response missing "ts"'
  if resp['ok']: assert 'data'  in resp, 'response missing "data"'
  else:          assert 'error' in resp, 'response missing "error"'


def x_rt(rt:Runtime) -> Tuple[Role, Player, Game]:
  ''' extract most-frequnetly used objects from runtime :) '''
  g = rt.game
  id = g.me[request.sid]
  return id, g.players[id], g

def get_rival(me:Role) -> Role:
  if me == BOB:   return ALICE
  if me == ALICE: return BOB
  raise ValueError(f'>> unknown role: {me}')


def mk_payload_loc(g:Game, id:Role=None) -> DataDict:
  if id is None:
    return { id: g.players[id].loc for id in g.players }
  else:
    return { id: g.players[id].loc }
