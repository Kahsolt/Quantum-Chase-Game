#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from dataclass_wizard import JSONWizard

from modules.qbloch import Loc, rand_loc
from services.models import SPAWN_LIMIT, SPAWN_TTL
from services.rand import random_gaussian_expect, random_choice
from services.packets import *
from services.utils import now_ts

class ItemType(Enum):
  PHOTON = 'photon'
  GATE = 'gate'

class ItemId(Enum):
  PHOTON = 'photon'
  X_GATE = 'X'
  Y_GATE = 'Y'
  Z_GATE = 'Z'
  H_GATE = 'H'
  S_GATE = 'S'
  T_GATE = 'T'
  RX_GATE = 'RX'
  RY_GATE = 'RY'
  RZ_GATE = 'RZ'
  CNOT_GATE = 'CNOT'
  SWAP_GATE = 'SWAP'

@dataclass
class Item:
  type: ItemType
  id: ItemId
  count: int = 1

@dataclass
class SpawnItem(JSONWizard):
  item: Item
  loc: Loc = field(default_factory=lambda: v_f2i(rand_loc()))
  ttl: int = field(default_factory=lambda: random_gaussian_expect(SPAWN_TTL, vmin=5))
  ts: int = field(default_factory=now_ts)


def handle_item_pick(payload:Payload, env:Env) -> HandlerRet:
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


def task_item_spawn(sio:SocketIO, spawns:List[SpawnItem], rid:int):
  # try spawn something
  if len(spawns) < SPAWN_LIMIT:
    item = Item(
      type=ItemType.GATE,
      id=random_choice([e for e in ItemId if e != ItemId.PHOTON]),
      count=round(random_gaussian_expect(SPAWN_COUNT, vmin=1)),
    )
    emit_item_spawn(sio, item, rid)

  # remove expired items
  now = now_ts()
  to_delete = []
  for spawn in spawns:
    if now - spawn.ts > spawn.ttl:
      to_delete.append(spawn)
  for spawn in spawns:
    spawns.remove(spawn)
