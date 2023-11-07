#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from modules.qlocal import CircuitPack, shot_circuit
from services.models import *
from services.packets import *
from services.rand import random_gaussian_expect, random_choice
from services.utils import now_ts

''' globals '''

# set by warm_up
spawn_rand: CircuitPack = None


''' handlers & emitters '''

def handle_item_pick(payload:Payload, rt:Runtime) -> HandlerRet:
  try:
    check_payload(payload, [('ts', int)])
  except Exception as e: return resp_error(e.args[0])

  _ts: int = payload['ts']

  found = None
  for spawn in rt.spawns:
    if _ts == spawn.ts:
      found = spawn
      break

  if found is None: return resp_error('not found')

  rt.spawns.remove(spawn)
  emit_item_vanish(rt.sio, spawn.ts, rt.rid)

  _, player = get_me(rt.game)
  item = spawn.item

  if item.type == ItemType.PHOTON:
    player.photon += item.count
  elif item.type == ItemType.GATE:
    item_id = item.id.value
    if item_id in player.gate:
      player.gate[item_id] += item.count
    else:
      player.gate[item_id] = item.count

  resp = {
    'item': item.to_dict(),
    'ts': _ts,
  }
  return resp_ok(resp), Recp.ONE


def emit_item_spawn(sio:SocketIO, spawn:SpawnItem, rid:str):
  sio.emit('item:spawn', resp_ok(spawn.to_dict()), to=rid)


def emit_item_vanish(sio:SocketIO, ts:int, rid:str):
  sio.emit('item:vanish', resp_ok({'ts': ts}), to=rid)


''' utils '''

def item_gain(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')

  if item.type == ItemType.PHOTON:
    player.photon += item.count

  elif item.type == ItemType.GATE:
    if item.id.value not in player.gate:
      player.gate[item.id.value] = 0
    player.gate[item.id.value] += item.count


def item_cost(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')

  if item.type == ItemType.PHOTON:
    if player.photon < item.count: raise ValueError(f'photon not enough, has: {player.photon}, need: {item.count}')
    player.photon -= item.count
  
  elif item.type == ItemType.GATE:
    if player.gate.get(item.id.value, 0) < item.count: raise ValueError(f'gate not enough, has: {player.gate[item.id.value]}, need: {item.count}')
    player.gate[item.id.value] -= item.count


''' tasks '''

def run_spawn_rand() -> int:
  nlen = len(SPAWN_WEIGHT)
  idx = nlen + 1
  while idx >= nlen:
    idx = shot_circuit(spawn_rand)
  return idx


def task_item_spawn(rt:Runtime):
  # try spawn something
  if len(rt.spawns) < SPAWN_LIMIT:
    idx = run_spawn_rand()
    type = ItemType.GATE if idx > 0 else ItemType.PHOTON
    count = round(random_gaussian_expect(SPAWN_COUNT_GATE if type == ItemType.GATE else SPAWN_COUNT_PHOTON, vmin=1))
    item = Item(type=type, id=ItemId(list(SPAWN_WEIGHT.keys())[idx]), count=count)
    spawn = SpawnItem(item)
    rt.spawns.append(spawn)
    emit_item_spawn(rt.sio, spawn, rt.rid)

  # remove expired items
  now = now_ts()
  to_delete: List[SpawnItem] = []
  for spawn in rt.spawns:
    if now > spawn.ts + spawn.ttl:
      to_delete.append(spawn)
  for spawn in to_delete:
    emit_item_vanish(rt.sio, spawn.ts, rt.rid)
    rt.spawns.remove(spawn)
