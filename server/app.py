#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

from flask import Flask, request
from flask_socketio import SocketIO, emit

from modules import *
from services import *

seed_everything(SEED)

app = Flask(__name__, template_folder=HTML_PATH, static_folder=HTML_PATH, static_url_path='/static')
app.register_blueprint(doc)
sio = SocketIO(app, logger=False, threaded=False)
env = Env(sio)


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
    if rid in env.games:
      rt = env.games[rid]
      rt.signal.set()
      if rt.game.me.keys().isdisjoint(env.conns.keys()):
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
  print('>> leave room :(', data)


handlers = {
  name: handler 
    for name, handler in globals().items() 
      if name.startswith(PREFIX_HANDLER) and isinstance(handler, Callable)
}
print('registered handlers:')
for name, func in handlers.items():
  event = name_func_to_event(name)
  print(f'  {event}')
  handler = make_handler(env, func)
  sio.on_event(event, handler)

emitters = {
  name: emitter 
    for name, emitter in globals().items() 
      if name.startswith(PREFIX_EMITTER) and isinstance(emitter, Callable)
}
print('registered emitters:')
for name, func in emitters.items():
  event = name_func_to_event(name)
  print(f'  {event}')


if __name__ == '__main__':
  try:
    warm_up()
    sio.run(app, host='0.0.0.0', port=PORT, debug=False, processes=1)
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
