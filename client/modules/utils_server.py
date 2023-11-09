#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from typing import *

import numpy as np

# src: server/services/shared
from modules.shared import *

# src: server/services/utils.py
pi     = np.pi
pi2    = pi * 2
pi_2   = pi / 2
pi_4   = pi / 4
pi_256 = pi / 256


# src: server/modules/qbloch.py
Loc = Tuple[float, float]
Phi = Tuple[complex, complex]

def loc_to_phi(loc:Loc) -> Phi:
  ''' |phi> = cos(θ/2)|0> + e^(iφ)sin(θ/2)|1> '''
  tht, psi = loc
  return np.cos(tht / 2), np.exp(psi*1j) * np.sin(tht / 2)


# src: server/services/movloc.py
def task_sim_loc(g:Game):
  if g is None: return
  for id, player in g.players.items():
    dir = player.dir
    if dir is None: continue
    dir_f = dir * pi_4             # enum => angle
    spd = v_i2f(player.spd)        # rescale
    tht, psi = v_i2f(player.loc)   # rescale

    U, R = np.sin(dir_f), np.cos(dir_f)
    # 纬度角速度均匀，值截断 [0, pi]
    tht_n = tht - U * spd / FPS
    if tht_n <  0: tht_n = 0
    if tht_n > pi: tht_n = pi
    # 经度角速度等比放缩，值循环 [0, 2*pi]
    #r = 1 / max(abs(tht - pi_2), pi_256)
    r = 1   # 也依角速度均匀
    psi_n = psi + (R * spd / FPS) * r
    if psi_n <   0: psi_n += pi2
    if psi_n > pi2: psi_n -= pi2
    player.loc = v_f2i([tht_n, psi_n])
