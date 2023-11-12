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

SEED = 42

pi     = np.pi
pi2    = pi * 2
pi_2   = pi / 2
pi_4   = pi / 4
pi_256 = pi / 256


def seed_everything(seed:int):
  random.seed(seed)
  np.random.seed(seed)

def now_ts() -> int:    # milliseconds
  return int(time() * 10**3)


def mem_info() -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
  pid = os.getpid()
  loadavg = psutil.getloadavg()
  p = psutil.Process(pid)
  meminfo = p.memory_full_info()
  rss = meminfo.rss / 2**20
  vms = meminfo.vms / 2**20
  mem_usage = p.memory_percent()

  return loadavg, (rss, vms, mem_usage)
