#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

import os
import json
from pathlib import Path
from re import compile as Regex
from traceback import format_exc
from typing import *

import numpy as np
from numpy import ndarray
try:
  from autograd.numpy.numpy_boxes import ArrayBox
except ImportError:
  ArrayBox = object
from isq import LocalDevice, optv, optimizer

Circuit = str
Params = List[float]
CircuitPack = Tuple[Circuit, Params]
State = ndarray
Prob = List[float]
Freq = List[int]

bin2dec = lambda x: int(x, base=2)
dec2bin = lambda x: bin(x)[2:]
freq2prob = lambda x: {k: v / sum(x.values()) for k, v in x.items()}

SHOTS = 1000
VARGS = 'theta'
REGEX_NQ = Regex('qbit q\[(\d+)\];')
REGEX_V  = Regex(f'{VARGS}\[\d+\]')
