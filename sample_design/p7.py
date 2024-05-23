from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('CMOS Inverter')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supply
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
# Input Signal
circuit.V('in', 'Vin', circuit.gnd, 2.5)  # Midpoint biasing for switching
# NMOS and PMOS for Inverter
circuit.MOSFET('1', 'Vout', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Vout', 'Vin', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
