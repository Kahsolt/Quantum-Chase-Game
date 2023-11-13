#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from .utils import *


def make_scene_fade_anims(scene:NodePath) -> Anims:
  in_anim  = LerpColorScaleInterval(scene, 0.5, ALPHA_1, ALPHA_0, blendType=IN)
  out_anim = LerpColorScaleInterval(scene, 0.5, ALPHA_0, ALPHA_1, blendType=OUT)
  return in_anim, out_anim
