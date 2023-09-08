#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07 

from isq import qpu
from isq import LocalDevice, QcisDevice, AwsDevice

# 使用模拟器运行，制备bell态
ld = LocalDevice()

@qpu(ld)
def bell_sim():
  '''
    qbit a, b;
    X(a);
    CNOT(a, b);
    M(a);
    M(b);
  '''

res = bell_sim()
print(res)
ir = ld.get_ir()
print(ir)


# 使用12bit量子硬件运行，制备bell态
qd = QcisDevice(user = "xxx", passwd = "xxx")

@qpu(qd)
def bell_qcis():
  '''
    qbit a, b;
    X(a);
    CNOT(a, b);
    M(a);
    M(b);
  '''

task = bell_qcis()
res = task.result()
print(res)
