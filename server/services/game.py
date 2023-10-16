#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from services.playerdata import Game


def game_init() -> Game:
  return Game()


def game_start(g:Game) -> Game:
  pass


def game_settle(g:Game) -> Game:
  pass
