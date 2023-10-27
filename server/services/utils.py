#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import os
import psutil
import random
from time import time
from pathlib import Path
from traceback import format_exc, print_exc
from typing import *

import numpy as np

BASE_PATH = Path(__file__).parent.parent.absolute()
HTML_PATH = BASE_PATH / 'html'
PORT = os.environ.get('PORT', 5000)

FPS = 30
SEED = 42

number = Union[int, float]

pi = np.pi
pi2 = pi * 2
pi_2 = pi / 2
pi_4 = pi / 4
pi_256 = pi / 256

# NOTE: DO NOT send float numbers through network
N_PREC = 5
v_i2f = lambda v: [v_i2f(e) for e in v] if isinstance(v, (list, tuple)) else (v / 10**N_PREC)
v_f2i = lambda v: [v_f2i(e) for e in v] if isinstance(v, (list, tuple)) else round(v * 10**N_PREC)


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
