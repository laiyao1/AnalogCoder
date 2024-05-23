import math
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *
circuit = Circuit('Opamp Adder')
# Define the input voltages
circuit.V('input1', 'Vin1', circuit.gnd, 1@u_V)
circuit.V('input2', 'Vin2', circuit.gnd, 1@u_V)
# Declare the subcircuit
circuit.subcircuit(SingleStageOpamp())
# Create a subcircuit instance
circuit.X('opamp', 'SingleStageOpamp', 'Vinp', 'Vinn', 'Vout')
# Resistors for the inverting summing amplifier configuration
R1 = 10@u_kΩ
R2 = 10@u_kΩ
Rf = 10@u_kΩ
# Connect the resistors
circuit.R(1, 'Vin1', 'Vinn', R1)
circuit.R(2, 'Vin2', 'Vinn', R2)
circuit.R(3, 'Vinn', 'Vout', Rf)
# Bias the non-inverting input to 2.5V
circuit.V('bias', 'Vinp', circuit.gnd, 2.5@u_V)
# Ground the inverting input through a resistor to set the operating point
circuit.R('ground', 'Vinn', circuit.gnd, 1@u_MΩ)
simulator = circuit.simulator()
analysis = simulator.operating_point()
