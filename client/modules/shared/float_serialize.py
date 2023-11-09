#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/9

# NOTE: DO NOT send float numbers through network

N_PREC = 5

v_i2f = lambda v: [v_i2f(e) for e in v] if isinstance(v, (list, tuple)) else       v / 10**N_PREC
v_f2i = lambda v: [v_f2i(e) for e in v] if isinstance(v, (list, tuple)) else round(v * 10**N_PREC)
