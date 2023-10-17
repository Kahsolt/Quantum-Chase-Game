#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/17

from time import sleep, time_ns
from threading import Thread, Event
from functools import partial
from argparse import ArgumentParser
from traceback import print_exc
from typing import *

from socketio import Client
import curses as cs
from curses import wrapper

from modules.playerdata import *

FPS = 10

KeyCode = int
KeyCodes = List[KeyCode]
MOVE_U: KeyCodes = [ord('w'), cs.KEY_UP]
MOVE_D: KeyCodes = [ord('s'), cs.KEY_DOWN]
MOVE_L: KeyCodes = [ord('a'), cs.KEY_LEFT]
MOVE_R: KeyCodes = [ord('d'), cs.KEY_RIGHT]
MOVE_KEYS: KeyCodes = MOVE_U + MOVE_D + MOVE_L + MOVE_R

sio = Client()
doc: Game = None


@sio.event
def connect():
  print('connection established')

@sio.event
def disconnect():
  print('disconnected from server')

@sio.on('move/change')
def my_response(data):
  id = data['me']
  mov = data['mov']
  print('', data)


def handle_input(is_quit:Event, stdscr):
  while not is_quit.is_set():
    sleep(1 / FPS)

    c: int = stdscr.getch()
    stdscr.addstr(1, 3, "Hello GitHub.")
    stdscr.addstr(2, 3, "Key: %d" % c)
    stdscr.refresh()

    if c in MOVE_KEYS:
      move = [233, 1.0]
      sio.emit('move/change', {'id': doc.me, 'move': move})
    elif c == ord('s'):
      global doc
      resp = sio.emit('game/init', {})
      doc = JSONWizard.from_dict(resp['data'])

      sio.emit('game/start', {'data': 'trigger my event'})
    elif c == ord('q'):
      sio.disconnect()
      break


def init_ui(stdscr):
  ncols, nlines = 9, 1
  uly, ulx = 15, 20
  win = cs.newwin(nlines, ncols, uly, ulx)
  win.border()
  stdscr.refresh()

def update_ui(is_quit:Event, stdscr):
  while not is_quit.is_set():
    sleep(1 / FPS)
    if doc is None: continue


def run(args, is_quit, stdscr):
  init_ui(stdscr)
  Thread(target=update_ui, args=(is_quit, stdscr), daemon=True).start()

  sio.connect(f'ws://{args.host}:{args.port}')
  Thread(target=handle_input, args=(is_quit, stdscr), daemon=True).start()
  sio.wait()


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('-H', '--host', default='127.0.0.1')
  parser.add_argument('-P', '--port', type=int, default=5000)
  args = parser.parse_args()

  is_quit = Event()
  try:
    wrapper(partial(run, args, is_quit))
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
  finally:
    is_quit.set()
