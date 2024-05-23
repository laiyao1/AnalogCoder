from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *


circuit = Circuit('Wien Bridge Oscillator')

# Declare and instantiate the opamp
circuit.subcircuit(SingleStageOpamp())
circuit.X('op1', 'SingleStageOpamp', 'Vinp', 'Vinn', 'Vout')

# Component values
R1 = 10@u_kΩ
R2 = 10@u_kΩ
C1 = 10@u_nF
C2 = 10@u_nF

# Wien Bridge network elements
circuit.R('1', 'Vout', 'n1', R1)  # R1 from Vout to node n1
circuit.C('1', 'n1', 'Vinp', C1)  # C1 from n1 to inverting input of opamp

circuit.R('2', 'Vinp', 'Vbias', R2)  # R2 from node n1 back to Vout, creating a series feedback
circuit.C('2', 'Vinp', 'Vbias', C2)  # C2 from Vout to ground, parallel to R2

circuit.R('f', 'Vout', 'Vinn', R1)
circuit.R('b', 'Vinn', 'Vbias', R1/10.0)

# Non-inverting input setup
circuit.V('bias', 'Vbias', circuit.gnd, 2.5@u_V)  # Bias voltage for the non-inverting input

simulator = circuit.simulator()
analysis = simulator.operating_point()
