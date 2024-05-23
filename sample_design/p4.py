from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Single-Stage Common-Gate Amplifier')
# Define the MOSFET model
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supply and Bias Voltage
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('bias', 'Vbias', circuit.gnd, 1.5) # Bias voltage for the gate of M1, ensuring it's above threshold
# Input Signal
circuit.V('in', 'Vin', circuit.gnd, 0.0)
# NMOS Transistor
circuit.MOSFET('1', 'Vout', 'Vbias', 'Vin', 'Vin', model='nmos_model', w=50e-6, l=1e-6)
# Load Resistor
circuit.R('1', 'Vout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
