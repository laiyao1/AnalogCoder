from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Three-Stage Amplifier')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supplies for the power and input signal
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('in', 'Vin', circuit.gnd, 1.65)
# First Stage: Common-Source with Resistor Load
circuit.MOSFET('1', 'Drain1', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.R('1', 'Drain1', 'Vdd', 1@u_kΩ)
# Second Stage: Common-Source with Resistor Load
circuit.MOSFET('2', 'Drain2', 'Drain1', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.R('2', 'Drain2', 'Vdd', 1@u_kΩ)
# Third Stage: Common-Source with Resistor Load
circuit.MOSFET('3', 'Vout', 'Drain2', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.R('3', 'Vout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
