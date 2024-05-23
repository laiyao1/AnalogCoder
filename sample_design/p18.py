import math
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *
circuit = Circuit('Opamp Integrator')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Declare the subcircuit for the opamp
circuit.subcircuit(SingleStageOpamp())
# Create a subcircuit instance for the opamp
circuit.X('opamp', 'SingleStageOpamp', 'Vinp', 'Vinn', 'Vout')
# Define the input voltage source
circuit.V('input', 'Vin', circuit.gnd, 2.5@u_V)
# Define the resistor R1 and capacitor Cf
R1 = 1@u_kΩ  # 1k ohm resistor
Cf = 1@u_uF  # 1uF capacitor
# Connect the resistor R1 between the input voltage source and the inverting input of the opamp
circuit.R('R1', 'Vin', 'Vinn', R1)
# Connect the capacitor Cf between the inverting input and the output of the opamp
circuit.C('Cf', 'Vinn', 'Vout', Cf)
# Connect the non-inverting input of the opamp to a reference voltage (2.5 V, same as the operating point)
circuit.V('ref', 'Vinp', circuit.gnd, 2.5@u_V)
simulator = circuit.simulator()
analysis = simulator.operating_point()
