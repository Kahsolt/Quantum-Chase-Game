#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import inspect

from flask import Flask, request
from flask_socketio import SocketIO, emit

from modules import *
from services import *

seed_everything(SEED)

app = Flask(__name__, template_folder=HTML_PATH, static_folder=HTML_PATH, static_url_path='/static')
app.register_blueprint(doc)
sio = SocketIO(app, logger=False, threaded=False)
env = Env()


@sio.on('connect')
def on_connect(auth):
  emit('connect', {'data': 'client connected'})
  sid = request.sid
  if sid not in env.conns:
    env.conns[sid] = None

@sio.on('disconnect')
def on_disconnect():
  sid = request.sid
  if sid in env.conns:
    rid = env.conns[sid]
    del env.conns[sid]
    if rid in env.signals:
      env.signals[rid].set()
      del env.signals[rid]
    if rid in env.games:
      if env.games[rid].me.keys().isdisjoint(env.conns.keys()):
        del env.games[rid]
    if rid in env.waits:
      if env.waits[rid].keys().isdisjoint(env.conns.keys()):
        del env.waits[rid]

@sio.on_error_default
def on_error_default(e):
  print(e)

@sio.on('join')
def on_join(data):
  print('>> join room :)', data)

@sio.on('leave')
def on_leave(data):
  print('>> leave room :)', data)


def is_handler_no_game(func:Callable):
  sig = inspect.signature(func)
  for k, v in sig.parameters.items():
    if v.annotation is Game: return False
  return True

def name_func_to_event(name:str) -> str:
  stem = None
  if name.startswith(PREFIX_HANDLER): stem = name[len(PREFIX_HANDLER):]
  if name.startswith(PREFIX_EMITTER): stem = name[len(PREFIX_EMITTER):]
  if stem is None: raise ValueError(f'unknown name: {name}')
  return stem.replace('_', ':')

def make_handler(func:Handler) -> Callable[[Payload, Union[Env, Game]], None]:
  def wrapper(payload:Payload):
    evt = name_func_to_event(func.__name__)
    sid = request.sid
    rid = env.conns.get(sid)
    print(f'[{evt}] sid: {sid}, rid: {rid}')
    print(f'payload: {payload}')
    if is_handler_no_game(func):
      ret = func(payload, env)
    else:
      g = env.games.get(rid)
      ret = func(payload, g)
    if isinstance(ret, tuple):
      resp, recp = ret
    else:
      resp, recp = ret, Recp.ONE
    print(f'resp: <{recp.value}> {resp}')
    if   recp == Recp.ALL:  sio.emit(evt, resp)
    elif recp == Recp.ROOM: sio.emit(evt, resp, to=rid)
    elif recp == Recp.ONE:  sio.emit(evt, resp, to=sid)
  return wrapper


handlers = {
  name: handler 
    for name, handler in globals().items() 
      if name.startswith(PREFIX_HANDLER) and isinstance(handler, Callable)
}
print('registered handlers:')
for name, func in handlers.items():
  event = name_func_to_event(name)
  print(f'  {event}')
  handler = make_handler(func)
  sio.on_event(event, handler)

print('registered emitters:')
emitters = {
  name: emitter 
    for name, emitter in globals().items() 
      if name.startswith(PREFIX_EMITTER) and isinstance(handler, Callable)
}
for name, func in emitters.items():
  event = name_func_to_event(name)
  print(f'  {event}')


if __name__ == '__main__':
  try:
    sio.run(app, host='0.0.0.0', port=PORT, debug=False, processes=1)
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
