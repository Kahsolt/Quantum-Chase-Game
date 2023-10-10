#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import random
from typing import *

import numpy as np


def seed_everything(seed:int):
  random.seed(seed)
  np.random.seed(seed)
