#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

import random
from math import sin, cos, acos, atan2
from time import time
from pathlib import Path
from traceback import print_exc
from typing import *

from panda3d.core import Vec2, Vec3

from modules.utils_server import *

BASE_PATH = Path(__file__).parent.parent.absolute()

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

GATE_NAME_MAPPING = {
  'SX': 'X2P',
  'SY': 'Y2P',
}

clip = lambda x, vmin, vmax: max(vmin, min(x, vmax))
rand_bit = lambda: random.randrange(2)

EntglPhi = Tuple[complex, complex, complex, complex]


def null_decorator(fn):
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper

dead_loop = null_decorator

def now_ts() -> int:    # milliseconds
  return int(time() * 10**3)


class ValueWindow:

  def __init__(self, len:int=100):
    self.v = []
    self.len = len
  
  def add(self, v):
    self.v.append(v)
    if len(self.v) > self.len:
      self.v = self.v[-self.len:]

  @property
  def mean(self):
    return sum(self.v) / len(self.v) if self.v else 0


def pos_to_rot(pos:Vec3) -> Vec2:
  v = pos.normalized()
  x, y, z = v.x, v.y, v.z
  tht = acos(z) 
  psi = atan2(y, x)
  return Vec2(tht, psi)

def rot_to_pos(rot:Vec2) -> Vec3:
  tht, psi = rot
  x = sin(tht) * cos(psi)
  y = sin(tht) * sin(psi)
  z = cos(tht)
  return Vec3(x, y, z)


def loc_str(loc:Loc) -> str:
  tht, psi = loc
  return f'({tht:.4f}, {psi:.4f})'

def phi_str(phi:Phi) -> str:
  c0, c1 = phi
  a = c0.real
  c, d = c1.real, c1.imag
  if c < 0:
    c, d = -c, -d
    sign = '-'
  else:
    sign = '+'
  return f'{a:.3f}|0> {sign} ({c:.3f}{d:+.3f}i)|1>'

def entgl_phi_str(phi:EntglPhi) -> str:
  a, b, c, d = [abs(e)**2 for e in phi]
  return f'{a:.3f}|00> + {b:.3f}|01> + {c:.3f}|10> + {d:.3f}|11>'


def loc_dist(x:Loc, y:Loc) -> float:
  a, b = x
  c, d = y
  return ((a - c) ** 2 + (b - d) ** 2) ** 0.5
