from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Differential OpAmp with Active Load')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supplies
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
circuit.V('bias', 'Vbias', circuit.gnd, 1.5)  # Bias voltage for the tail current source M3
# Input Voltage Sources for Differential Inputs
circuit.V('inp', 'Vinp', circuit.gnd, 2.5)
circuit.V('inn', 'Vinn', circuit.gnd, 2.5)
# Differential Pair and Tail Current Source
circuit.MOSFET('1', 'Voutp', 'Vinp', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Vout', 'Vinn', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('3', 'Source3', 'Vbias', circuit.gnd, circuit.gnd, model='nmos_model', w=100e-6, l=1e-6)
# Active Current Mirror Load
circuit.MOSFET('4', 'Voutp', 'Voutp', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
circuit.MOSFET('5', 'Vout', 'Voutp', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
