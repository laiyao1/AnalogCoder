import math
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *
circuit = Circuit('Opamp Subtractor')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Define input voltages
circuit.V('input1', 'Vin1', circuit.gnd, 2.75@u_V)
circuit.V('input2', 'Vin2', circuit.gnd, 5.00@u_V)
# Declare the subcircuit
circuit.subcircuit(SingleStageOpamp())
# Resistor values
R1 = 10@u_kΩ
R2 = 10@u_kΩ
# Create the subtractor circuit using the opamp and resistors
circuit.R('1', 'Vin1', 'Vinn', R1)
circuit.R('2', 'Vin2', 'Vinp', R1)
circuit.R('3', 'Vinn', 'Vout', R2)
circuit.R('4', 'Vinp', circuit.gnd, R2)
# Create a subcircuit instance
circuit.X('opamp', 'SingleStageOpamp', 'Vinp', 'Vinn', 'Vout')
simulator = circuit.simulator()
analysis = simulator.operating_point()
