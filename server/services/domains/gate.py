#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from modules.qbloch import phi2loc, eliminate_gphase, Loc
from modules.qlocal import run_circuit_state, shot_circuit, dec2bin
from modules.qcircuit import Operation, convert_circuit
from services.handler import *
from services.domains.item import item_cost, emit_item_cost

Ops = Union[Operation, List[Operation]]


''' handlers & emitters '''

def handle_gate_rot(payload:Payload, rt:Runtime) -> HandlerRet:
  try:
    check_payload(payload, [('gate', str), ('theta?', float)])
    assert payload['gate'] in ROT_GATES + P_ROT_GATES
  except Exception as e: return resp_error(e.args[0])

  id, player, g = x_rt(rt)

  item = Item(ItemType.GATE, ItemId(payload['gate']), 1)
  try: item_cost(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_cost(rt, item)

  _gate: str = payload['gate']
  _theta: float = payload.get('theta', None)

  if rt.is_entangled():
    qid = QUBIT_MAP[id]
    state = entgl_evolve(rt,
      (_gate, _theta, qid)
    )
    return resp_ok({'state': v_f2i(state)}), Recp.ROOM
  else:
    tht, psi = v_i2f(player.loc)
    loc = run_single_evolve([
      ('RY',   tht, 0),
      ('RZ',   psi, 0),
      (_gate, _theta, 0),
    ])
    player.loc = v_f2i(loc)
    return resp_ok(mk_payload_loc(g, id)), Recp.ROOM


def handle_gate_swap(payload:Payload, rt:Runtime) -> HandlerRet:
  id0, player, g = x_rt(rt)

  item = Item(ItemType.GATE, ItemId.SWAP_GATE, 1)
  try: item_cost(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_cost(rt, item)

  if rt.is_entangled():
    id1 = get_rival(id0)
    qid0 = QUBIT_MAP[id0]
    qid1 = QUBIT_MAP[id1]
    state = entgl_evolve(rt, [
      # isQ-open has no native SWAP impl, decompose it using CNOTs
      ('CNOT', None, (qid0, qid1)),
      ('CNOT', None, (qid1, qid0)),
      ('CNOT', None, (qid0, qid1)),
    ])
    return resp_ok({'state': v_f2i(state)}), Recp.ROOM
  else:
    # TODO: replace with qunatum impl :)
    g.players[ALICE].loc, g.players[BOB].loc = g.players[BOB].loc, g.players[ALICE].loc
    return resp_ok(mk_payload_loc(g)), Recp.ROOM


def handle_gate_cnot(payload:Payload, rt:Runtime) -> HandlerRet:
  id0, player, g = x_rt(rt)

  item = Item(ItemType.GATE, ItemId.CNOT_GATE, 1)
  try: item_cost(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_cost(rt, item)

  id1 = get_rival(id0)
  qid0 = QUBIT_MAP[id0]
  qid1 = QUBIT_MAP[id1]
  tht0, psi0 = v_i2f(g.players[id0].loc)
  tht1, psi1 = v_i2f(g.players[id1].loc)
  state = entgl_evolve(rt, [
    ('RY',   tht0,  qid0),
    ('RZ',   psi0,  qid0),
    ('RY',   tht1,  qid1),
    ('RZ',   psi1,  qid1),
    ('CNOT', None, (qid1, qid0)),
  ])
  return resp_ok({'state': v_f2i(state)}), Recp.ROOM


def handle_gate_meas(payload:Payload, rt:Runtime) -> HandlerRet:
  id, player, g = x_rt(rt)

  item = Item(ItemType.GATE, ItemId.MEASURE_GATE, 1)
  try: item_cost(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_cost(rt, item)

  if rt.is_entangled():
    entgl_break(rt)
    return resp_ok(mk_payload_loc(g)), Recp.ROOM
  else:
    tht, psi = v_i2f(player.loc)
    loc = run_single_mesaure([
      ('RY', tht, 0),
      ('RZ', psi, 0),
    ])
    player.loc = v_f2i(loc)
    return resp_ok(mk_payload_loc(g, id)), Recp.ROOM


def emit_entgl_enter(rt:Runtime):
  rt.sio.emit('entgl:enter', resp_ok(), to=rt.rid)


def emit_entgl_break(rt:Runtime):
  rt.sio.emit('entgl:break', resp_ok(), to=rt.rid)


''' utils '''

def cbit_to_loc(b:int) -> Loc:
  assert b in [0, 1]
  if b == 0: return phi2loc([1, 0])   # |0>
  if b == 1: return phi2loc([0, 1])   # |1>


def run_single_evolve(ops:Ops) -> Loc:
  circ, _ = convert_circuit(ops, nq=1)
  phi = run_circuit_state((circ, []))
  print('>> phi:', phi)
  return phi2loc(eliminate_gphase(phi))


def run_single_mesaure(ops:Ops) -> Loc:
  circ, _ = convert_circuit(ops, nq=1)
  b = shot_circuit((circ, []))
  print('>> b:', b)
  return cbit_to_loc(b)


def entgl_evolve(rt:Runtime, op:Ops) -> List[float]:
  # freeze movloc & entangle
  if not rt.is_entangled():
    for id, player in rt.game.players.items():
      player.dir = None
    emit_entgl_enter(rt)

  # continue state evolution
  if isinstance(op, list):
    rt.circuit.extend(op)
  else:
    rt.circuit.append(op)
  circ, _ = convert_circuit(rt.circuit, nq=2)
  state: List[complex] = run_circuit_state((circ, [])).tolist()
  print('>> state:', state)   # 4*complex
  amps = []                   # 8*float
  for c in state:
    amps.extend([c.real, c.imag])
  return amps


def entgl_break(rt:Runtime):
  assert rt.is_entangled()

  # measure & relocate
  circ, _ = convert_circuit(rt.circuit, nq=2)
  r = shot_circuit((circ, []))
  bits = [int(e) for e in dec2bin(r).rjust(2, '0')]
  for id, player in rt.game.players.items():
    player.loc = v_f2i(cbit_to_loc(bits[QUBIT_MAP[id]]))

  # unfreeze movloc & disentangle
  rt.circuit.clear()
  emit_entgl_break(rt)
