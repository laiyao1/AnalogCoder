from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('NMOS Constant Current Source with Resistive Load')
# Define the MOSFET model
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supplies for the power and bias voltage
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
circuit.V('bias', 'Vbias', circuit.gnd, 1.5)  # Bias voltage (greater than V_th to ensure saturation)
# NMOS Constant Current Source Setup
circuit.M('1', 'Vout', 'Vbias', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Load Resistor
circuit.R('1', 'Vout', 'Vdd', 1@u_kΩ)  # Resistor value as 1kΩ
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
