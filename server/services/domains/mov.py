#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from services.models import *
from services.packets import *


''' handlers & emitters '''

def handle_mov_start(payload:Payload, rt:Runtime) -> HandlerRet:
  try:
    check_payload(payload, [('dir', int)])
    assert 0 <= payload['dir'] <= 7
  except Exception as e: return resp_error(e.args[0])

  g = rt.game
  id, player = get_me(g)

  _dir: int = payload['dir']
  _spd: int = payload.get('spd')

  player.dir = _dir
  if _spd is not None:
    player.spd = _spd

  payload['id'] = id
  return resp_ok(payload), Recp.ROOM


def handle_mov_stop(payload:Payload, rt:Runtime) -> HandlerRet:
  g = rt.game
  id, player = get_me(g)

  player.dir = None

  resp = mk_payload_loc(g, id)
  return resp_ok(resp), Recp.ROOM


''' tasks '''

def task_mov_sim(rt:Runtime):
  for id, player in rt.game.players.items():
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
