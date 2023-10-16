#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import os
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
