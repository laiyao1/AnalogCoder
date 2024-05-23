import math
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from p_lib import *
circuit = Circuit('RC Phase-Shift Oscillator')
# Define the DC operating voltage
Vdc = 2.5 @ u_V
# Add a DC voltage source for the operating point
circuit.V(1, 'Vdc', circuit.gnd, Vdc)
# Declare the subcircuit for the op-amp
circuit.subcircuit(SingleStageOpamp())
# Create the RC phase-shift network
R1 = 10 @ u_kΩ
C1 = 10 @ u_nF
R2 = 10 @ u_kΩ
C2 = 10 @ u_nF
R3 = 10 @ u_kΩ
C3 = 10 @ u_nF
# Connect the RC network
circuit.R(1, 'Vout', 'node1', R1)
circuit.C(1, 'node1', 'node2', C1)
circuit.R(2, 'node2', 'node3', R2)
circuit.C(2, 'node3', 'node4', C2)
circuit.R(3, 'node4', 'node5', R3)
circuit.C(3, 'node5', 'Vdc', C3)
# Connect node2 to ground through a resistor to avoid floating node
circuit.R(5, 'node2', circuit.gnd, 10 @ u_kΩ)
# Connect the op-amp
circuit.X('op', 'SingleStageOpamp', 'node5', 'Vdc', 'Vout')
# Connect the feedback from the output to the input of the RC network
circuit.R(4, 'node1', 'Vdc', 10 @ u_kΩ)
# Create a simulator instance
simulator = circuit.simulator()
