#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

from isqtools import compile, simulate

# compile "vqe.isq" and generate the qir file "vqe.so"
compile('vqe.isq', target='qir')


import numpy as np 

shots = 100
learning_rate = 1.
energy_list = []
epochs = 20
theta = np.array([0.0])

coeffs = [-0.4804, +0.3435, -0.4347, +0.5716, +0.0910, +0.0910]
gates_group =  [
    ((0, "Z"),),
    ((1, "Z"),),
    ((0, "Z"), (1, "Z")),
    ((0, "Y"), (1, "Y")),
    ((0, "X"), (1, "X")),
]

def get_expectation(theta):
    measure_results = np.zeros(len(gates_group) + 1)
    measure_results[0] = 1.0
    # The first does not require quantum measurement, which is constant
    # As a result, the other 5 coefficients need to be measured
    for idx in range(len(gates_group)):
        result_dict = simulate(
            "h2.so",
            shots=shots,
            int_param=idx,
            double_param=theta,
        )
        result = 0
        for res_index, frequency in result_dict.items():
            parity = (-1) ** (res_index.count("1") % 2)
            # parity checking to get expectation value
            result += parity * frequency / shots
            # frequency instead of probability
        measure_results[idx + 1] = result
        # to accumulate every expectation result
        # The result is multiplied by coefficient
    return np.dot(measure_results, coeffs)

def parameter_shift(theta):
    # to get gradients
    theta = theta.copy()
    theta += np.pi / 2
    forwards = get_expectation(theta)
    theta -= np.pi
    backwards = get_expectation(theta)
    return 0.5 * (forwards - backwards)


import time

energy = get_expectation(theta)
energy_list.append(energy)
print(f"Initial VQE Energy: {energy_list[0]} Hartree")

start_time = time.time()
for epoch in range(epochs):
    theta -= learning_rate * parameter_shift(theta)
    energy = get_expectation(theta)
    energy_list.append(energy)
    print(f"Epoch {epoch+1}: {energy} Hartree")

print(f"Final VQE Energy: {energy_list[-1]} Hartree")
print("Time:", time.time() - start_time)
