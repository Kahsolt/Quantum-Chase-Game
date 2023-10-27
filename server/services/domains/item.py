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
  # TODO: ?
  return resp_ok(), Recp.ONE


def emit_item_spawn(sio:SocketIO, item:Item, rid:str):
  spwan_item = SpawnItem(item)
  sio.emit('item:spawn', resp_ok(spwan_item.to_dict()), to=rid)


''' utils '''

def item_gain(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')
  bag = player.bag

  if item.type == ItemType.PHOTON:
    bag.photon += item.count

  elif item.type == ItemType.GATE:
    if item.id.value not in bag.gate:
      bag.gate[item.id.value] = 0
    bag.gate[item.id.value] += item.count


def item_cost(player:Player, item:Item):
  if item.count <= 0: raise ValueError('item count must be positive')
  bag = player.bag

  if item.type == ItemType.PHOTON:
    if bag.photon < item.count: raise ValueError(f'photon not enough, has: {bag.photon}, need: {item.count}')
    bag.photon -= item.count
  
  elif item.type == ItemType.GATE:
    if bag.gate.get(item.id.value, 0) < item.count: raise ValueError(f'gate not enough, has: {bag.gate[item.id.value]}, need: {item.count}')
    bag.gate[item.id.value] -= item.count


''' tasks '''

def run_spawn_rand() -> int:
  nlen = len(SPAWN_WEIGHT)
  idx = nlen + 1
  while idx >= nlen:
    idx = shot_circuit(spawn_rand)
  return idx


def task_item_spawn(sio:SocketIO, spawns:List[SpawnItem], rid:int):
  # try spawn something
  if len(spawns) < SPAWN_LIMIT:
    idx = run_spawn_rand()
    type = ItemType.GATE if idx > 0 else ItemType.PHOTON
    count = round(random_gaussian_expect(SPAWN_COUNT_GATE if type == ItemType.GATE else SPAWN_COUNT_PHOTON, vmin=1))
    item = Item(type=type, id=ItemId(list(SPAWN_WEIGHT.keys())[idx]), count=count)
    emit_item_spawn(sio, item, rid)

  # remove expired items
  now = now_ts()
  to_delete = []
  for spawn in spawns:
    if now - spawn.ts > spawn.ttl:
      to_delete.append(spawn)
  for spawn in spawns:
    spawns.remove(spawn)
