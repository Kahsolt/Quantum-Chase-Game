#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import os
import psutil
import random
from pathlib import Path
from traceback import format_exc, print_exc
from typing import *

import numpy as np
from numpy import ndarray
try:
  from autograd.numpy.numpy_boxes import ArrayBox
except ImportError:
  ArrayBox = object

BASE_PATH = Path(__file__).parent.parent.absolute()

pi = np.pi

SEED = 42
SHOTS = 1000


def timer(fn):
  def wrapper(*args, **kwargs):
    from time import time
    start = time()
    r = fn(*args, **kwargs)
    end = time()
    print(f'[Timer]: {fn.__name__} took {end - start:.3f}s')
    return r
  return wrapper


def seed_everything(seed:int):
  random.seed(seed)
  np.random.seed(seed)


def mem_info() -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
  import gc ; gc.collect()

  pid = os.getpid()
  loadavg = psutil.getloadavg()
  p = psutil.Process(pid)
  meminfo = p.memory_full_info()
  rss = meminfo.rss / 2**20, 
  vms = meminfo.vms / 2**20
  mem_usage = p.memory_percent()

  return loadavg, (rss, vms, mem_usage)
