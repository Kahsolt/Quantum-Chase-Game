#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

import random
from math import sin, cos, acos, atan2
from pathlib import Path
from traceback import print_exc
from typing import *

from panda3d.core import Vec2, Vec3

from modules.utils_server import *

BASE_PATH = Path(__file__).parent.parent.absolute()

rand_bit = lambda: random.randrange(2)
get_rival = lambda role: 'Alice' if role == 'Bob' else 'Bob'

NO_MOVE = Vec2(0, 0)

def pos_to_rot(pos:Vec3) -> Vec2:
  v = pos.normalized()
  x, y, z = v.x, v.y, v.z
  tht = acos(z) 
  psi = atan2(y, x)
  return Vec2(tht, psi)

def rot_to_pos(rot:Vec2) -> Vec3:
  tht, psi = rot.x, rot.y
  x = sin(tht) * cos(psi)
  y = sin(tht) * sin(psi)
  z = cos(tht)
  return Vec3(x, y, z)


def null_decorator(fn):
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper

dead_loop = null_decorator


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
