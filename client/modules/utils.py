#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

import random
from typing import *

from modules.utils_server import *

rand_bit = lambda: random.randrange(2)


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
