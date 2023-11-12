#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from modules.utils import BASE_PATH

ASSETS_PATH  = BASE_PATH  / 'assets'
MODEL_PATH   = ASSETS_PATH / 'model'
TEXTURE_PATH = ASSETS_PATH / 'texture'
IMAGE_PATH   = ASSETS_PATH / 'image'
AUDIO_PATH   = ASSETS_PATH / 'audio'

# external assets
MO_SPHERE = MODEL_PATH / 'Sphere.egg'
MO_SPHERE_HIGHPOLY = MODEL_PATH / 'Sphere_HighPoly.egg'
MO_CUBE = MODEL_PATH / 'Cube.egg'
MO_DODEC = MODEL_PATH / 'Dodecahedron.egg'
MO_TETRA = MODEL_PATH / 'Tetrahedron.egg'
MO_TRIA_PRISM = MODEL_PATH / 'trianglular_prism.egg'

TX_PLASMA = TEXTURE_PATH / 'plasma.png'

SCENE_BGM = {
  'Title': AUDIO_PATH / 'choose-your-player.ogg',
  'Main':  AUDIO_PATH / 'eyes.ogg',
}

# string path in unix format
_to_unix = lambda fp: str(fp).replace('\\', '/')
IMAGE_REL_PATH = IMAGE_PATH.relative_to(BASE_PATH)
IMG_AUX   = lambda name: _to_unix(IMAGE_REL_PATH / f'{name}.png')
IMG_QUBIT = lambda bit:  _to_unix(IMAGE_REL_PATH / f'qubit_{bit}.png')
IMG_GATE  = lambda name: _to_unix(IMAGE_REL_PATH / f'gate_{name}.png')

# internal assets
AU_SFX_CLICK = 'models/audio/sfx/GUI_click.wav'
AU_SFX_ROLLOVER = 'models/audio/sfx/GUI_rollover.wav'
