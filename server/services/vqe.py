#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/24

from services.item import *
from services.utils import *
from modules.qbloch import Loc, loc2phi
from modules.xtele import teleport


def handle_vqe_ham(payload:Payload, g:Game) -> HandlerRet:
  try:
    check_payload(payload, [('dir', float)])
    assert 0 <= payload['dir'] <= pi2
  except Exception as e: return resp_error(e.args[0])

  player = get_player(g)

  _dir: float = payload['dir']
  _spd: float = payload.get('spd')

  player.dir = _dir
  if _spd is not None:
    player.spd = _spd

  return resp_ok(payload), Recp.ROOM


def handle_vqe_solve(payload:Payload, g:Game) -> HandlerRet:
  player = get_player(g)

  player.dir = None
  payload['loc'] = player.loc

  return resp_ok(payload), Recp.ROOM


def emit_vqe_phase():
  pass
