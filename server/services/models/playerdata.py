#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard
from typing import List, Dict, Union, Optional

int_opt = Optional[int]
str_opt = Optional[str]


@dataclass
class Player:
  dir: int_opt = None
  spd: int = 0
  loc: List[int_opt] = field(default_factory=lambda: [None, None])
  photon: int = 0
  gate: Dict[str, int] = field(default_factory=dict)


@dataclass
class Game(JSONWizard):
  me: Union[str_opt, Dict[str, str]]
  players: Dict[str, Player] = field(default_factory=dict)
  winner: str_opt = None
  startTs: int = -1
  endTs: int = -1
  noise: float = 0.0


if __name__ == '__main__':
  me = 'Alice'
  g = Game(me=me, players={me: Player()})
  print(g)
