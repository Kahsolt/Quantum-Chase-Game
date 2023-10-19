#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard
from typing import *

float_opt = Optional[float]
str_opt = Optional[str]
Role = str


@dataclass
class Bag:
  photon: int = 0
  gate: Dict[str, int] = field(default_factory=dict)


@dataclass
class Player:
  dir: float_opt = None
  spd: float = 0.0
  loc: List[float_opt] = field(default_factory=lambda: [None, None])
  bag: Optional[Bag] = Bag()


@dataclass
class Status:
  stage: int = 0
  winner: str_opt = None
  startTs: int = -1
  endTs: int = -1


@dataclass
class Const:
  cost: Dict[str, int] = field(default_factory=dict)
  noise: float = 0.0


@dataclass
class Game(JSONWizard):
  me: Union[str_opt, Dict[str, str]]
  players: Dict[Role, Player] = field(default_factory=dict)
  status: Status = Status()
  const: Const = Const()


if __name__ == '__main__':
  me = 'Alice'
  g = Game(me=me, players={me: Player()})
  print(g)
