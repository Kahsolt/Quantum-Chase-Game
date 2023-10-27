#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from modules.qbloch import phi2loc, eliminate_gphase
from modules.qlocal import *
from modules.qcircuit import Operation, convert_circuit
from services.models import *
from services.packets import *
from services.domains.item import *
from services.domains.movloc import emit_mov_freeze, emit_mov_unfreeze

Ops = Union[Operation, List[Operation]]


''' handlers & emitters '''

def handle_gate_rot(payload:Payload, rt:Runtime) -> HandlerRet:
  try:
    check_payload(payload, [('gate', str)])
    assert payload['gate'] in ROT_GATES
  except Exception as e: return resp_error(e.args[0])

  g = rt.game
  id, player = get_me(g)
  qid = QUBIT_MAP[id]

  try: item_cost(player, Item(ItemType.GATE, ItemId(payload['gate']), 1))
  except Exception as e: return resp_error(e.args[0])

  _gate: str = payload['gate']

  if rt.is_entangled():
    state = entgl_continue(rt,
      Operation(_gate, None, qid)
    )
    return resp_ok({'state': state}), Recp.ROOM
  else:
    tht, psi = v_i2f(player.loc)
    loc = run_single_evolve([
      Operation('RY',   tht, qid),
      Operation('RZ',   psi, qid),
      Operation(_gate, None, qid),
    ])
    player.loc = v_f2i(loc)
    return resp_ok(mk_payload_loc(g, id)), Recp.ROOM if rt.is_visible() else Recp.ONE


def handle_gate_swap(payload:Payload, rt:Runtime) -> HandlerRet:
  g = rt.game
  id, player = get_me(g)

  try: item_cost(player, Item(ItemType.GATE, ItemId.SWAP_GATE, 1))
  except Exception as e: return resp_error(e.args[0])

  if rt.is_entangled():
    state = entgl_continue(rt,
      Operation('SWAP', None, QUBIT_MAP[id])
    )
    return resp_ok({'state': state}), Recp.ROOM
  else:
    g.players[ALICE].loc, g.players[BOB].loc = g.players[BOB].loc, g.players[ALICE].loc
    return resp_ok(mk_payload_loc(g)), Recp.ROOM


def handle_gate_cnot(payload:Payload, rt:Runtime) -> HandlerRet:
  g = rt.game
  id0, player = get_me(g)

  try: item_cost(player, Item(ItemType.GATE, ItemId.CNOT_GATE, 1))
  except Exception as e: return resp_error(e.args[0])

  id1 = get_rival(id0)
  qid0 = QUBIT_MAP[id0]
  qid1 = QUBIT_MAP[id1]
  tht0, psi0 = v_i2f(g.players[id0].loc)
  tht1, psi1 = v_i2f(g.players[id1].loc)
  state = entgl_continue(rt, [
    Operation('RY',   tht0,  qid0),
    Operation('RZ',   psi0,  qid0),
    Operation('RY',   tht1,  qid1),
    Operation('RZ',   psi1,  qid1),
    Operation('CNOT', None, (qid1, qid0)),
  ])
  return resp_ok({'state': state}), Recp.ROOM


def handle_gate_meas(payload:Payload, rt:Runtime) -> HandlerRet:
  g = rt.game
  id, player = get_me(g)

  try: item_cost(player, Item(ItemType.GATE, ItemId.MEASURE_GATE, 1))
  except Exception as e: return resp_error(e.args[0])

  if rt.is_entangled():
    entgl_break()
    return resp_ok(mk_payload_loc(g)), Recp.ROOM
  else:
    qid = QUBIT_MAP[id]
    tht, psi = v_i2f(player.loc)
    loc = run_single_mesaure([
      Operation('RY', tht, qid),
      Operation('RZ', psi, qid),
    ])
    player.loc = v_f2i(loc)
    return resp_ok(mk_payload_loc(g, id)), Recp.ROOM if rt.is_visible() else Recp.ONE


''' utils '''

def cbit_to_loc(b:str) -> Loc:
  assert b in ['0', '1']
  if b == '0': return phi2loc([1, 0])
  if b == '1': return phi2loc([0, 1])


def run_single_evolve(ops:Ops) -> Loc:
  circ = convert_circuit(ops, nq=1)
  phi = run_circuit_state((circ, []))
  return phi2loc(eliminate_gphase(phi))


def run_single_mesaure(ops:Ops) -> Loc:
  circ = convert_circuit(ops, nq=1)
  b = shot_circuit((circ, []))
  return cbit_to_loc(b)


def entgl_continue(rt:Runtime, op:Ops) -> State:
  # freeze move & entangle
  if not rt.is_entangled():
    for id, player in g.players.items():
      player.dir = None
    emit_mov_freeze()

  # continue state evolution
  if isinstance(op, list):
    rt.circuit.extend(op)
  else:
    rt.circuit.append(op)
  circ = convert_circuit(rt.circuit, nq=2)
  state = run_circuit_state((circ, []))
  return state.tolist()   # TODO: this is complex number??


def entgl_break(rt:Runtime):
  assert rt.is_entangled()
  players = rt.game.players

  # measure & relocate
  circ = convert_circuit(rt.circuit, nq=2)
  bits = shot_circuit((circ, []))
  for id in players.keys():
    players[id].loc = v_f2i(cbit_to_loc(bits[QUBIT_MAP[id]]))

  # unfreeze move & disentangle
  rt.circuit.clear()
  emit_mov_unfreeze()
