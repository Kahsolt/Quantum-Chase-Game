#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from services.utils import *
from modules.qbloch import Loc


def handle_mov_change(payload:Payload, g:Game) -> HandlerRet:
  try: check_payload(payload, [('id', str), ('dir', float)])
  except Exception as e: return resp_error(e.args[0])

  _id: str = payload['id']
  id = g.me[request.sid]
  if _id != id: return resp_error(f'{_id} != {id}, who you are?')
  player = g.players[id]

  _dir: float = payload['dir']
  _spd: float = payload.get('spd')

  player.dir = _dir
  if _spd is not None:
    player.spd = _spd

  return resp_ok(payload), Recp.ROOM


def handle_mov_stop(payload:Payload, g:Game) -> HandlerRet:
  try: check_payload(payload, [('id', str)])
  except Exception as e: return resp_error(e.args[0])

  _id: str = payload['id']
  id = g.me[request.sid]
  if _id != id: return resp_error(f'{_id} != {id}, who you are?')
  player = g.players[id]

  player.dir = None
  payload['loc'] = player.loc

  return resp_ok(payload), Recp.ROOM


def handle_loc_sync(payload:Payload, g:Game) -> HandlerRet:
  resp: Dict[Role, Loc] = {}
  for id, player in g.players.items():
    resp[id] = player.loc

  return resp_ok(resp), Recp.ONE


''' utils '''

pi2 = pi * 2
pi_2 = pi / 2
pi_256 = pi / 256

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
