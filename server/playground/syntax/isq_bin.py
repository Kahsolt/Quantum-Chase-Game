#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/12

# cmdline binary usage:
# https://www.arclightquantum.com/isq-docs/latest/usage/

cmd_compile = 'isqc compile [options] <Input>'

'''
  --emit <FORMAT> : output content format, format value can be mlir, mlirqir, llvm, mlir-optimized, binary, out [default: out]
  -o, --output <OUTFILE> : output file
  -O, --opt-level <OPT_LEVEL> : llvm opt-level such as -O1, -O2, -O3 etc.
  --target <TARGET_IR> : target ir, now support qir, open-qasm3, qcis [default: qir]
  --qcis-config <MAPPING_CONFIG_FILE> : qcis mapping config file
  -I, --inc-path <INC_PATH>: library path of isQ used in the source code, a default path is $ISQ_ROOT/lib
  -i <INT>: int type paramter, which is used when compiled to qcis
  -d <DOUBLE> double type paramter, which is used when compiled to qcis
'''

cmd_simulate = 'isqc simulate [options] <Input>'

'''
  --shots <NUM>: simulate times, default is 1
  --debug: use debug mod and get the print result
  --cuda <NUM>: use gpu, NUM is the number of qubits to be simulated
  -i <INT>: int type paramter
  -d <DOUBLE> double type paramter
  --qcis simulate qcis
'''

cmd_run = 'isqc run [options] <Input>'

'''
  --shots <NUM>: simulate times, default is 1
  --debug: use debug mod and get the print result
'''
