#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard
from typing import *


@dataclass
class Move:
  dir: float = 0.0
  spd: float = 0.0


@dataclass
class Bag:
  photon: int = 0
  gate: Dict[str, int] = field(default_factory=dict)


@dataclass
class Player:
  loc: Optional[Tuple[float, float]] = None
  mov: Move = Move()
  bag: Bag = Bag()


@dataclass
class Status:
  stage: int = 0
  winner: Optional[str] = None
  startTs: int = -1
  endTs: int = -1


@dataclass
class Const:
  cost: Dict[str, int] = field(default_factory=dict)
  noise: float = 0.0


@dataclass
class Game(JSONWizard):
  me: Optional[str] = None
  players: Dict[str, Player] = field(default_factory=dict)
  status: Status = Status()
  const: Const = Const()
