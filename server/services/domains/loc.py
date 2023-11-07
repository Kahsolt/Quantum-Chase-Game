#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from modules.xtele import teleport, loc2phi, HttpConnectionError
from services.models import *
from services.packets import *
from services.domains.item import item_cost


''' handlers & emitters '''

def handle_loc_query(payload:Payload, rt:Runtime) -> HandlerRet:
  try:
    check_payload(payload, [('photon', int), ('basis', str)])
    assert payload['photon'] > 0
    assert payload['basis'] in ['Z', 'X']
  except Exception as e: return resp_error(e.args[0])

  _photon: int = payload['photon']
  if payload['basis'] != 'Z': return resp_error('only support basis Z measure')

  g = rt.game
  id, player = get_me(g)

  try: item_cost(player, Item(ItemType.PHOTON, ItemId.PHOTON, _photon))
  except Exception as e: return resp_error(e.args[0])

  shots = _photon * 10
  loc = g.players[get_rival(id)].loc
  phi = loc2phi(v_i2f(loc))
  try:
    freq = teleport(phi, shots)
  except HttpConnectionError:
    # NOTE: use classical simulation when Docker is not available
    prob = [abs(e)**2 for e in phi]
    results = np.random.choice([0, 1], size=shots, p=prob)
    cntr = Counter(results)
    freq = [cntr.get(0, 0), cntr.get(1, 0)]

  return resp_ok({'freq': freq}), Recp.ONE


def handle_loc_sync(payload:Payload, rt:Runtime) -> HandlerRet:
  resp = mk_payload_loc(g)

  return resp_ok(resp), Recp.ONE
