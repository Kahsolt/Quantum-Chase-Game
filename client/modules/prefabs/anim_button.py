#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from direct.gui.DirectButton import DirectButton

from .utils import *


def anim_button(btn:DirectButton) -> Sequence:
  scale_orig = btn['scale']
  anim = Parallel(
    Sequence(
      LerpScaleInterval(btn, duration=0.1, scale=scale_orig*1.2),
      LerpScaleInterval(btn, duration=0.1, scale=scale_orig),
    ),
    Sequence(
      LerpColorInterval(btn, duration=0.1, color=RED),
      LerpColorInterval(btn, duration=0.1, color=WHITE),
    ),
  )
  return anim
