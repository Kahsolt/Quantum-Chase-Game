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
  THETA  = 'theta'
  GATE   = 'gate'

class ItemId(Enum):
  # photon
  PHOTON = 'photon'

  # theta (angle for parametrical gates)
  THETA = 'theta'

  '''
  ref: 
    - isQ-open: https://www.arclightquantum.com/isq-core/grammar/#_2
    - isQ: https://www.arclightquantum.com/isq-docs/latest/gate/
    - Qiskit: https://qiskit.org/documentation/apidoc/circuit_library.html
  '''
  # gate (native of isQ-open)
  X_GATE = 'X'
  Y_GATE = 'Y'
  Z_GATE = 'Z'
  H_GATE = 'H'
  SX_GATE = 'X2P'     # √X
  SY_GATE = 'Y2P'     # √Y
  S_GATE = 'S'        # √Z
  T_GATE = 'T'        # √S
  SXdg_GATE = 'X2M'   # √X.dagger
  SYdg_GATE = 'Y2M'   # √Y.dagger
  Sdg_GATE = 'SD'     # √Z.dagger
  Tdg_GATE = 'TD'     # √S.dagger
  CX_GATE = 'CX'
  CY_GATE = 'CY'
  CZ_GATE = 'CZ'
  CNOT_GATE = 'CNOT'  # aka. CX
  RX_GATE = 'RX'
  RY_GATE = 'RY'
  RZ_GATE = 'RZ'
  # gate (derived)
  P_GATE  = 'P'       # = e^(iλ/2)*RZ(λ)
  U1_GATE = 'U1'      # = P(λ) = U3(0,0,λ)
  U2_GATE = 'U2'      # = U3(π/2,φ,λ)
  U3_GATE = 'U3'
  CH_GATE = 'CH'
  CP_GATE = 'CP'
  SWAP_GATE = 'SWAP'
  iSWAP_GATE = 'iSWAP'
  CRX_GATE = 'CRX'
  CRY_GATE = 'CRY'
  CRZ_GATE = 'CRZ'
  RXX_GATE = 'RXX'
  RYY_GATE = 'RYY'
  RZZ_GATE = 'RZZ'
  RZX_GATE = 'RZX'
  XXpYY_GATE = 'XX+YY'
  XXmYY_GATE = 'XX-YY'
  # gate (virtual)
  MEASURE_GATE = 'M'

ROT_GATES: List[str] = [e.value for e in [
  ItemId.X_GATE,
  ItemId.Y_GATE,
  ItemId.Z_GATE,
  ItemId.H_GATE,
  ItemId.S_GATE,
  ItemId.T_GATE,
  ItemId.SX_GATE,
  ItemId.SY_GATE,
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
