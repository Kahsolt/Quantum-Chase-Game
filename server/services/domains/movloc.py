#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from modules.xtele import teleport, Loc, loc2phi
from services.packets import *

from .item import *


def handle_mov_start(payload:Payload, g:Game) -> HandlerRet:
  try:
    check_payload(payload, [('dir', int)])
    assert 0 <= payload['dir'] <= 7
  except Exception as e: return resp_error(e.args[0])

  id, player = get_me(g)

  _dir: int = payload['dir']
  _spd: int = payload.get('spd')

  player.dir = _dir
  if _spd is not None:
    player.spd = _spd

  payload['id'] = id
  return resp_ok(payload), Recp.ROOM


def handle_mov_stop(payload:Payload, g:Game) -> HandlerRet:
  id, player = get_me(g)

  player.dir = None

  payload['id'] = id
  payload['loc'] = player.loc
  return resp_ok(payload), Recp.ROOM


def handle_loc_query(payload:Payload, g:Game) -> HandlerRet:
  try:
    check_payload(payload, [('photon', int)])
    assert payload['photon'] > 0
  except Exception as e: return resp_error(e.args[0])

  id, player = get_me(g)

  try: item_cost(player, ItemType.PHOTON, ItemId.PHOTON, payload['photon'])
  except Exception as e: return resp_error(e.args[0])

  loc = g.players[ALICE if id == BOB else BOB].loc
  freq = teleport(loc2phi(loc))

  return resp_ok({'freq': freq}), Recp.ONE


def handle_loc_sync(payload:Payload, g:Game) -> HandlerRet:
  resp: Dict[Role, Loc] = {}
  for id, player in g.players.items():
    resp[id] = player.loc

  return resp_ok(resp), Recp.ONE


''' utils '''

def task_loc_sim(game:Game):
  if game is None: return
  for id, player in game.players.items():
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
    r = 1 / max(abs(tht - pi_2), pi_256)
    psi_n = psi + (R * spd / FPS) * r
    if psi_n <   0: psi_n += pi2
    if psi_n > pi2: psi_n -= pi2
    player.loc = v_f2i([tht_n, psi_n])
