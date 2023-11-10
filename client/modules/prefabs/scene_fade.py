#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from .utils import *


def make_scene_fade_anims(scene:NodePath) -> Anims:
  in_anim  = LerpColorScaleInterval(scene, 1.2, ALPHA_1, ALPHA_0, blendType='easeIn')
  out_anim = LerpColorScaleInterval(scene, 1.2, ALPHA_0, ALPHA_1, blendType='easeOut')
  return in_anim, out_anim
