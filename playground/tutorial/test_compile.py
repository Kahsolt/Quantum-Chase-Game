#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import LocalDevice

isq_str = '''
  qbit a, b;
  H(a);
  CNOT(a, b);
  M(a);
  M(b);
'''

'''
isQ-core -> openqasm 2.0
qreg 大小与 isQ-core 定义的量子比特数目一致
creg 大小与测量的比特数目一致
测量结果按测量顺序从 creg[0] 开始依次存储
'''
ld = LocalDevice()
ir = ld.compile_to_ir(isq_str, target='openqasm')
print(ir)

ld = LocalDevice()
ir = ld.compile_to_ir(isq_str, target='qcis')
print(ir)
