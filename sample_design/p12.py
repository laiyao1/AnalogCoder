from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Cascode Current Mirror')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supply
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
# Reference Current Source
circuit.I('ref', 'Vdd', 'Iref', 1@u_mA) # 1mA reference current
# Input Side (Reference Side)
circuit.MOSFET('1', 'Iref', 'Iref', 'Source2', 'Source2', model='nmos_model', w=50e-6, l=1e-6) # Diode-connected M1
circuit.MOSFET('2', 'Source2', 'Iref', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6) # M2
# Output Side
circuit.MOSFET('3', 'Iout', 'Iref', 'Source4', 'Source4', model='nmos_model', w=50e-6, l=1e-6) # M3
circuit.MOSFET('4', 'Source4', 'Iref', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6) # M4
# Load Resistor
circuit.R('1', 'Iout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
