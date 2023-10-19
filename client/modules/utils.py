#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

import random
from typing import *

import numpy as np

from modules.playerdata import *

Loc = Tuple[float, float]
Phi = Tuple[complex, complex]

pi = np.pi
pi2 = pi * 2
pi_2 = pi / 2
pi_256 = pi / 256

rand_bit = lambda: random.randrange(2)

FPS = 30
ALICE = 'Alice'
BOB = 'Bob'

def null_decorator(fn):
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper

dead_loop = null_decorator


def loc_to_phi(loc:Loc) -> Phi:
  ''' |phi> = cos(θ/2)|0> + e^(iφ)sin(θ/2)|1> '''
  tht, psi = loc
  return np.cos(tht / 2), np.exp(psi*1j) * np.sin(tht / 2)

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


def task_sim_loc(game:Game):
  if game is None: return
  for id, player in game.players.items():
    dir = player.dir
    if dir is None: continue
    spd = player.spd
    tht, psi = player.loc

    U, R = np.sin(dir), np.cos(dir)
    # 纬度角速度均匀，值截断 [0, pi]
    tht_n = tht - U * spd / FPS
    if tht_n <  0: tht_n = 0
    if tht_n > pi: tht_n = pi
    # 经度角速度等比放缩，值循环 [0, 2*pi]
    r = 1 / max(abs(tht - pi_2), pi_256)
    psi_n = psi + (R * spd / FPS) * r
    if psi_n <   0: psi_n += pi2
    if psi_n > pi2: psi_n -= pi2
    player.loc = [tht_n, psi_n]
