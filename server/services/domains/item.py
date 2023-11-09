#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from modules.qbloch import rand_loc
from modules.qlocal import CircuitPack, shot_circuit
from services.handler import *
from services.rand import random_gaussian_expect, random_choice
from services.utils import now_ts

''' globals '''

# set by warm_up
spawn_rand: CircuitPack = None


''' handlers & emitters '''

def handle_item_pick(payload:Payload, rt:Runtime) -> HandlerRet:
  if rt.is_entangled(): return resp_error('invalid operation when entangled')

  try:
    check_payload(payload, [('ts', int)])
  except Exception as e: return resp_error(e.args[0])

  _ts: int = payload['ts']    # use as id

  spawn = item_vanish(rt, _ts)
  if spawn is None: return resp_error('spawn not found')
  emit_item_vanish(rt, spawn.ts)
  item = spawn.item

  id, player, g = x_rt(rt.game)

  try: item_gain(player, item)
  except Exception as e: return resp_error(e.args[0])
  emit_item_gain(item)

  return resp_ok()


def emit_item_spawn(rt:Runtime, spawn:SpawnItem):
  rt.sio.emit('item:spawn', resp_ok(spawn.to_dict()), to=rt.rid)


def emit_item_vanish(rt:Runtime, ts:int):
  rt.sio.emit('item:vanish', resp_ok({'ts': ts}), to=rt.rid)


def emit_item_gain(rt:Runtime, item:Item):
  rt.sio.emit('item:gain', resp_ok(item.to_dict()), to=request.sid)


def emit_item_cost(rt:Runtime, item:Item):
  rt.sio.emit('item:cost', resp_ok(item.to_dict()), to=request.sid)


''' utils '''

def item_spawn(rt:Runtime, spawn:SpawnItem):
  rt.spawns[spawn.ts] = spawn


def item_vanish(rt:Runtime, ts:int) -> Optional[SpawnItem]:
  if ts not in rt.spawns: return None

  spawn = rt.spawns[ts]
  del rt.spawns[ts]
  return spawn


def item_gain(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')

  if item.type == ItemType.PHOTON:
    player.photons += item.count

  elif item.type == ItemType.GATE:
    item_id = item.id.value
    if item_id not in player.gates:
      player.gates[item_id] = 0
    player.gates[item_id] += item.count


def item_cost(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')

  if item.type == ItemType.PHOTON:
    if player.photons < item.count: raise ValueError(f'photons not enough, has: {player.photons}, need: {item.count}')
    player.photons -= item.count
  
  elif item.type == ItemType.GATE:
    item_id = item.id.value
    if player.gates.get(item_id, 0) < item.count: raise ValueError(f'gates not enough, has: {player.gates[item_id]}, need: {item.count}')
    player.gates[item_id] -= item.count
    if player.gates[item_id] == 0:
      del player.gates[item_id]


''' tasks '''

def run_spawn_rand() -> int:
  nlen = len(SPAWN_WEIGHT)
  idx = nlen + 1
  while idx >= nlen:
    idx = shot_circuit(spawn_rand)
  return idx


def task_item_spawn(rt:Runtime):
  # frezze ts
  now = now_ts()

  # try spawn something
  if len(rt.spawns) < SPAWN_LIMIT:
    idx = run_spawn_rand()
    type = ItemType.GATE if idx > 0 else ItemType.PHOTON
    count = round(random_gaussian_expect(SPAWN_COUNT_GATE if type == ItemType.GATE else SPAWN_COUNT_PHOTON, vmin=1))
    item = Item(type, ItemId(list(SPAWN_WEIGHT.keys())[idx]), count)
    spawn = SpawnItem(
      item,
      v_f2i(rand_loc()),
      random_gaussian_expect(SPAWN_TTL, vmin=5),
      now,
    )
    item_spawn(rt, spawn)
    emit_item_spawn(rt, spawn)

  # remove expired spawns
  to_delete: List[int] = []
  for ts, spawn in rt.spawns.items():
    if now > spawn.ts + spawn.ttl:
      to_delete.append(ts)

  for ts in to_delete:
    spawn = item_vanish(rt, ts)
    emit_item_vanish(rt, spawn.ts)
