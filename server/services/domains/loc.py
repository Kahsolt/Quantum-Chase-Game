#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from modules.qcloud import HttpConnectionError
from modules.xtele import teleport, loc2phi, Loc
from services.handler import *
from services.domains.item import item_cost, emit_item_cost


''' handlers & emitters '''

def handle_loc_query(payload:Payload, rt:Runtime) -> HandlerRet:
  if rt.is_entangled(): return resp_error('invalid operation when entangled')

  try:
    check_payload(payload, [('photons', int), ('basis', str)])
    assert payload['photons'] > 0
    assert payload['basis'] in ['Z', 'X']
    assert payload['basis'] == 'Z', 'only support basis Z measure so far'
  except Exception as e: return resp_error(e.args[0])

  _photons: int = payload['photons']

  id, player, g = x_rt(rt)

  item = Item(ItemType.PHOTON, ItemId.PHOTON, _photons)
  try: item_cost(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_cost(rt, item)

  shots = _photons
  loc: Loc = v_i2f(g.players[get_rival(id)].loc)
  phi = loc2phi(loc)
  try:
    freq = teleport(phi, shots)
  except HttpConnectionError:
    # NOTE: use classical simulation when Docker is not available
    prob = [abs(e)**2 for e in phi]
    results = np.random.choice([0, 1], size=shots, p=prob)
    cntr = Counter(results)
    freq = [cntr.get(0, 0), cntr.get(1, 0)]

  return resp_ok({'freq': freq})


def handle_loc_sync(payload:Payload, rt:Runtime) -> HandlerRet:
  if rt.is_entangled(): return resp_error('invalid operation when entangled')

  id, player, g = x_rt(rt)

  return resp_ok(mk_payload_loc(g))
