#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/17

import os
import uuid
from random import choice
from time import sleep, time_ns
from threading import Thread, Event
from functools import partial
from argparse import ArgumentParser
from traceback import print_exc
from typing import *

from socketio import Client
import curses as cs
from curses import wrapper
import keyboard as kb
from keyboard import KeyboardEvent

from modules.utils import *

KeyCode = str
Packet = Dict[str, Any]
Data = Dict[str, Any]

FPS = 30
MAX_LEN = 36
INDENT = 2

CHARS = '~!@#$%^&*()<>?:"\{\}|'
rand_char = lambda: choice(CHARS)

MOVE_U: KeyCode = 'w'
MOVE_D: KeyCode = 's'
MOVE_L: KeyCode = 'a'
MOVE_R: KeyCode = 'd'
MOVE_KEYS: List[KeyCode] = [MOVE_U, MOVE_D, MOVE_L, MOVE_R]
DIR_MAPPING = {
  ( 0,  0): None,
  (+1,  0): 0,
  (+1, +1): 1,
  ( 0, +1): 2,
  (-1, +1): 3,
  (-1,  0): 4,
  (-1, -1): 5,
  ( 0, -1): 6,
  (+1, -1): 7,
}

sio = Client()
stdscr = None

joined: bool = False
game: Game = None
keyholds: Set[KeyCode] = set()  # decide cur moving dir
moving: Set[str] = set()        # show rand_char animation
geo_fmt: type = Phi  # or Loc


def unpack_data(fn):
  def wrapper(pack:Packet):
    print(f'>> [{fn.__name__}]: {pack}')
    if not pack['ok']:
      ui_show_info('>> error: ' + pack['error'])
      return
    return fn(pack['data'])
  return wrapper

def has_game(fn):
  def wrapper(*args, **kwargs):
    global game
    if game is None:
      return
    return fn(*args, **kwargs)
  return wrapper

def has_stdscr(fn):
  def wrapper(*args, **kwargs):
    global stdscr
    if stdscr is None:
      return
    return fn(*args, **kwargs)
  return wrapper


@sio.event
def connect():
  ui_show_info('>> connection established :)')
  sleep(0.5)
  ui_show_info('x - start game, z - quit')

@sio.event
def disconnect():
  quit()

@sio.on('game:join')
@unpack_data
def game_join(data:Data):
  global joined
  joined = True
  ui_show_info('wait for another player...')

@sio.on('game:start')
@unpack_data
def game_start(data:Data):
  global game
  game = Game.from_dict(data)
  print(game)
  ui_show_info(f'You are {game.me}, walk with WASD')
  run_sched_task(is_quit, 1/FPS, task_sim_loc, game)

@sio.on('game:settle')
@unpack_data
def game_settle(data:Data):
  winner = data['winner']
  endTs = data['endTs']
  ui_show_info(f'>> winner: {winner}, endTs: {endTs}')

@sio.on('mov:start')
@unpack_data
def mov_start(data:Data):
  id = data['id']
  player = game.players[id]
  player.dir = data['dir']
  if 'spd' in data:
    player.spd = data['spd']
  moving.add(id)

@sio.on('mov:stop')
@unpack_data
def mov_stop(data:Data):
  id = data['id']
  player = game.players[id]
  player.dir = None
  loc = data['loc']
  player.loc = [(x + y) / 2 for x, y in zip(loc, player.loc)]
  if id in moving: moving.remove(id)

@sio.on('loc:sync')
@unpack_data
def loc_sync(data:Data):
  for id, loc in data.items():
    game.players[id].loc = loc

@sio.on('item:spawn')
def item_spawn(data:Data):
  ui_show_info(str(data))


def handle_input_z(evt:KeyboardEvent):
  if evt.event_type == kb.KEY_UP: return
  quit()

def handle_input_x(evt:KeyboardEvent):
  if evt.event_type == kb.KEY_UP: return
  if joined: return
  if game is not None: return
  sio.emit('game:join', {
    'rid': args.room, 
    'r': rand_bit(),
  })

@has_game
def handle_input_wasd(evt:KeyboardEvent):
  key = evt.name
  if evt.event_type == kb.KEY_DOWN:
    if key in keyholds: return
    keyholds.add(key)
  elif evt.event_type == kb.KEY_UP:
    if key not in keyholds: return
    keyholds.remove(key)

  horz, vert = 0, 0
  if MOVE_R in keyholds: horz += 1
  if MOVE_L in keyholds: horz -= 1
  if MOVE_U in keyholds: vert += 1
  if MOVE_D in keyholds: vert -= 1

  new_dir = DIR_MAPPING[(horz, vert)]
  old_dir = game.players[game.me].dir
  if all([new_dir, old_dir]) and new_dir == old_dir: return

  if new_dir is None:
    sio.emit('mov:stop', {})
  else:
    sio.emit('mov:start', {'dir': new_dir})

@dead_loop
def handle_input(is_quit:Event):
  while not is_quit.is_set():
    evt = kb.read_event()   # this will block
    key = evt.name

    if key == 'z':
      handle_input_z(evt)
    elif key == 'x':
      handle_input_x(evt)
    elif key in MOVE_KEYS:
      handle_input_wasd(evt)


def init_ui(stdscr):
  TITLE = 'Quantum Tour v0.1'
  os.system(f'TITLE {TITLE}')
  os.system(f'MODE CON COLS={36} LINES={10}')

  stdscr.addstr(0, 0, '------------------------------------')
  stdscr.addstr(1, 0, '     Quantum Tour (CUI version)     ')
  stdscr.addstr(2, 0, '------------------------------------')
  stdscr.addstr(3, 0, '  a: ???                            ')
  stdscr.addstr(4, 0, '  b: ???                            ')
  stdscr.addstr(5, 0, '------------------------------------')
  stdscr.addstr(6, 0, '                                    ')
  stdscr.addstr(7, 0, '------------------------------------')
  stdscr.refresh()

  if not 'test subwin':
    H, W = stdscr.getmaxyx()
    ncols, nlines = 9, 1
    uly, ulx = 15, 20
    win = cs.newwin(nlines, ncols, uly, ulx)
    win.border()

@has_stdscr
def ui_clr_ln(lineno:int):
  stdscr.addstr(lineno, 0, ' ' * MAX_LEN)

@has_stdscr
def ui_show_info(s:str, lineno:int=6):
  ui_clr_ln(lineno)
  stdscr.addstr(lineno, 0, (' ' * INDENT + s).ljust(MAX_LEN))
  stdscr.move(8, 0)
  stdscr.refresh()


@has_game
def task_update_ui():
  if geo_fmt is Phi:
    def draw(ch:str, role:str, lineno:int):
      loc = v_i2f(game.players[role].loc)
      phi = loc_to_phi(loc)
      sfx = f' {rand_char()}' if role in moving else ''
      ui_show_info(f'{ch}: {phi_str(phi)}{sfx}', lineno)
  elif geo_fmt is Loc:
    def draw(ch:str, role:str, lineno:int):
      loc = v_i2f(game.players[role].loc)
      sfx = f' {rand_char()}' if role in moving else ''
      ui_show_info(f'{ch}: {loc_str(loc)}{sfx}', lineno)
  else: raise ValueError

  draw('a', ALICE, 3)
  draw('b', BOB,   4)

def run_sched_task(is_quit:Event, interval:float, func:Callable, func_args:tuple=()):
  global game

  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      sleep(interval)
      if game is None: continue
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')
    quit()

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()


def quit():
  ui_show_info('>> goodbye~')
  is_quit.set()
  sio.disconnect()

def run(args, is_quit:Event, stdscr):
  globals()['stdscr'] = stdscr
  init_ui(stdscr)
  run_sched_task(is_quit, 1/FPS, task_update_ui)

  sio.connect(f'http://{args.host}:{args.port}', transports=['websocket'])
  Thread(target=handle_input, args=(is_quit,), daemon=True).start()
  sio.wait()


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('-H', '--host', default='127.0.0.1')
  parser.add_argument('-P', '--port', type=int, default=5000)
  parser.add_argument('-R', '--room', default='test')
  parser.add_argument('--uuid', default=uuid.uuid4())
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
    kb.send('ctrl+c')   # force notify `kb.read_event()`
