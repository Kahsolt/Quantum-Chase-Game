#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from flask_socketio import emit

from services.utils import *

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


def handle_item_pick(payload:Payload, env:Env) -> HandlerRet:
  # TODO: ?
  return resp_ok(), Recp.ONE


def emit_item_spawn(env:Env, rid:str):
  if rid not in env.waits: return
  if rid in env.games: return

  # TODO: 地图上自然生成事物
  emit('item:spawn', resp_ok(), to=rid)


''' utils '''

def item_gain(player:Player, item_type:ItemType, item_id:ItemId, count:int):
  if count <= 0: raise ValueError('item count must be positive')
  bag = player.bag

  if item_type == ItemType.PHOTON:
    bag.photon += count

  elif item_type == ItemType.GATE:
    if item_id.value not in bag.gate:
      bag.gate[item_id.value] = 0
    bag.gate[item_id.value] += count

def item_cost(player:Player, item_type:ItemType, item_id:ItemId, count:int):
  if count <= 0: raise ValueError('item count must be positive')
  bag = player.bag
  
  if item_type == ItemType.PHOTON:
    if bag.photon < count: raise ValueError(f'photon not enough, has: {bag.photon}, need: {count}')
    bag.photon -= count
  
  elif item_type == ItemType.GATE:
    if bag.gate.get(item_id.value, 0) < count: raise ValueError(f'gate not enough, has: {bag.gate[item_id.value]}, need: {count}')
    bag.gate[item_id.value] -= count
