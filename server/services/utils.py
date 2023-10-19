#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import os
import psutil
import uuid
import random
from copy import copy, deepcopy
from enum import Enum
from time import time, sleep
from pathlib import Path
from threading import Thread, Event
from traceback import format_exc, print_exc
from typing import *

import numpy as np
from flask import request
from flask_socketio import SocketIO

from services.models.playerdata import *
from services.models.staticdata import *

BASE_PATH = Path(__file__).parent.parent.absolute()
HTML_PATH = BASE_PATH / 'html'
PORT = os.environ.get('PORT', 5000)

FPS = 30
SEED = 42

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
  # sid => rid|None
  conns: Dict[str, Optional[str]] = field(default_factory=dict)
  # rid => sid => r
  waits: Dict[str, Dict[str, int]] = field(default_factory=dict)
  # rid => game
  games: Dict[str, Game] = field(default_factory=dict)
  # rid => Event, is_stop movloc simulating
  signals: Dict[str, Event] = field(default_factory=dict)

HandlerRet = Union[
  Tuple[Resp, Recp],      # sucess
  Resp,                   # error
]
Handler = Callable[[Payload, Union[Env, Game]], HandlerRet]

PREFIX_HANDLER = 'handle_'
PREFIX_EMITTER = 'emit_'


def null_decorator(fn):
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper

dead_loop = null_decorator

def seed_everything(seed:int):
  random.seed(seed)
  np.random.seed(seed)

def now_ts() -> int:
  return int(time())


def mem_info() -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
  pid = os.getpid()
  loadavg = psutil.getloadavg()
  p = psutil.Process(pid)
  meminfo = p.memory_full_info()
  rss = meminfo.rss / 2**20
  vms = meminfo.vms / 2**20
  mem_usage = p.memory_percent()

  return loadavg, (rss, vms, mem_usage)


def run_sched_task(is_quit:Event, interval:float, func:Callable, func_args:tuple=()):
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      sleep(interval)
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()


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
