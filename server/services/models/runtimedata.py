#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from enum import Enum

from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard

from modules.qbloch import Loc, rand_loc
from services.models import SPAWN_TTL
from services.rand import random_gaussian_expect
from services.utils import v_f2i, now_ts


class GameStage(Enum):
  QCF = 0   # run quantum coin flipping to decide role
  QTL = 1   # run quantum teleportation find partners location
  VQE = 2   # run vqe to solve the final location


class ItemType(Enum):
  PHOTON = 'photon'
  GATE = 'gate'


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


ROT_GATES = [e.value for e in [
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
P_GATES = [e.value for e in [
  ItemId.RX_GATE,
  ItemId.RY_GATE,
  ItemId.RZ_GATE,
]]


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
