#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import math
from pathlib import Path
from time import time
from functools import partial
from typing import *

import numpy as np
from numpy import ndarray

from qvm import *

pi = np.pi
eps = 1e-8
rand  = lambda  : np.random.random ()   # random float
randn = lambda n: np.random.randint(n)  # random int
randb = lambda  :           randn  (2)  # random bit


def timer(fn):
  def wrapper(*args, **kwargs):
    start = time()
    r = fn(*args, **kwargs)
    end = time()
    print(f'[Timer]: {fn.__name__} took {end - start:.3f}s')
    return r
  return wrapper
