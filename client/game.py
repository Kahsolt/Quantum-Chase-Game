#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/02

import uuid
from argparse import ArgumentParser

from modules.ui import GameUI


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('-H', '--host', default='127.0.0.1')
  parser.add_argument('-P', '--port', type=int, default=5000)
  parser.add_argument('-R', '--room', default='test')
  parser.add_argument('--uuid', default=uuid.uuid4())
  args = parser.parse_args()

  GameUI(args).run()
