#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from enum import Enum
from typing import List, Dict, Union, Optional
from dataclasses import dataclass, field

from dataclass_wizard import JSONWizard

Role = str

@dataclass
class Player:
  dir: Optional[int] = None
  spd: int = 0
  loc: List[int] = field(default_factory=lambda: [0, 0])
  photons: int = 0
  gates: Dict[str, int] = field(default_factory=dict)

@dataclass
class Game(JSONWizard):
  rid: str
  me: Union[Role, Dict[str, Role]]
  players: Dict[str, Player] = field(default_factory=dict)
  winner: Optional[Role] = None
  startTs: int = -1
  endTs: int = -1


class ItemType(Enum):
  PHOTON = 'photon'
  GATE   = 'gate'

class ItemId(Enum):
  # photon
  PHOTON = 'photon'
  # gate (non-parametrical)
  X_GATE = 'X'
  Y_GATE = 'Y'
  Z_GATE = 'Z'
  H_GATE = 'H'
  S_GATE = 'S'
  T_GATE = 'T'
  X2P_GATE = 'X2P'
  X2M_GATE = 'X2M'
  Y2P_GATE = 'Y2P'
  Y2M_GATE = 'Y2M'
  CNOT_GATE = 'CNOT'
  SWAP_GATE = 'SWAP'
  # gate (parametrical)
  RX_GATE = 'RX'
  RY_GATE = 'RY'
  RZ_GATE = 'RZ'
  # gate (virtual)
  MEASURE_GATE = 'M'

ROT_GATES: List[str] = [e.value for e in [
  ItemId.X_GATE,
  ItemId.Y_GATE,
  ItemId.Z_GATE,
  ItemId.H_GATE,
  ItemId.S_GATE,
  ItemId.T_GATE,
  ItemId.X2P_GATE,
  ItemId.X2M_GATE,
  ItemId.Y2P_GATE,
  ItemId.Y2M_GATE,
]]
P_ROT_GATES: List[str] = [e.value for e in [
  ItemId.RX_GATE,
  ItemId.RY_GATE,
  ItemId.RZ_GATE,
]]

@dataclass
class Item(JSONWizard):
  type: ItemType
  id: ItemId
  count: int = 1

@dataclass
class SpawnItem(JSONWizard):
  item: Item
  loc: List[int] = field(default_factory=lambda: [0, 0])
  ttl: int = 0
  ts: int = 0       # also use as uid


if __name__ == '__main__':
  me = 'Alice'
  g = Game(rid='test', me=me, players={me: Player()})
  print(g)
