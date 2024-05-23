from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Common-Drain Amplifier')
# Define the MOSFET model
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supply
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
# Input Signal Source
circuit.V('in', 'Vin', circuit.gnd, 4.0)
# NMOS Transistor - Common Drain Configuration
circuit.MOSFET('1', 'Vdd', 'Vin', 'Vout', circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Load Resistor
circuit.R('1', 'Vout', circuit.gnd, 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
