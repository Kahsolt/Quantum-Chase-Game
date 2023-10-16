#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

from flask import Flask
from flask_socketio import SocketIO, send, emit
from flask_socketio import join_room, leave_room

from modules import *
from services import *

seed_everything(SEED)

app = Flask(__name__, template_folder=HTML_PATH, static_folder=HTML_PATH, static_url_path='/static')
app.register_blueprint(doc)
socketio = SocketIO(app, logger=True)


@socketio.on('connect')
def on_connect(auth):
  emit('connect', {'data': 'client connected'})

@socketio.on('disconnect')
def on_disconnect():
  print('client disconnected')

@socketio.on_error()
def on_error(e):
  print(e)

@socketio.on_error_default
def on_error_default(e):
  print(e)

@socketio.on('message')
def on_message(data):
  print('received message: ' + data)
  send(data)

@socketio.on('json')
def on_json(json):
  print('received json: ' + str(json))
  send(json, json=True)

@socketio.on('join')
def on_join(data):
  username = data['username']
  room = data['room']
  join_room(room)
  send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
  username = data['username']
  room = data['room']
  leave_room(room)
  send(username + ' has left the room.', to=room)

@socketio.on('my event')
def on_my_event(json):
  emit('my response', json)


def my_function_handler(data):
  ret = {'data': sum(data['data'])}
  emit('my response', ret)

socketio.on_event('my function', my_function_handler)


if __name__ == '__main__':
  try:
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True)
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
