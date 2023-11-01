#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/19

from modules.xtele import teleport, loc2phi
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

  g = rt.game
  id, player = get_me(g)

  try: item_cost(player, ItemType.PHOTON, ItemId.PHOTON, payload['photon'])
  except Exception as e: return resp_error(e.args[0])

  loc = g.players[get_rival(id)].loc
  freq = teleport(loc2phi(loc))

  return resp_ok({'freq': freq}), Recp.ONE


def handle_loc_sync(payload:Payload, rt:Runtime) -> HandlerRet:
  resp = mk_payload_loc(g)

  return resp_ok(resp), Recp.ONE
