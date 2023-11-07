#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from modules.utils import BASE_PATH

ASSETS_PATH  = BASE_PATH  / 'assets'
MODEL_PATH   = ASSETS_PATH / 'model'
TEXTURE_PATH = ASSETS_PATH / 'texture'
AUDIO_PATH   = ASSETS_PATH / 'audio'

# external assets
MO_SPHERE = MODEL_PATH / 'Sphere.egg'
MO_SPHERE_HIGHPOLY = MODEL_PATH / 'Sphere_HighPoly.egg'
MO_CUBE = MODEL_PATH / 'Cube.egg'
MO_DODEC = MODEL_PATH / 'Dodecahedron.egg'
MO_TETRA = MODEL_PATH / 'Tetrahedron.egg'
MO_TRIA_PRISM = MODEL_PATH / 'trianglular_prism.egg'

TX_PLASMA = TEXTURE_PATH / 'plasma.png'


# internal assets
AU_SFX_ROLLOVER = 'audio/sfx/GUI_rollover'
AU_SFX_CLICK = 'audio/sfx/GUI_click'

MO_DIALOG_BOX = 'gui/dialog_box_gui'
MO_RADIO_BUTTON = 'gui/radio_button_gui'
