from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('NMOS Inverter')
# Define the NMOS model
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supply for the circuit
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
# Input signal source
circuit.V('in', 'Vin', circuit.gnd, 1.0)  # 1V input for bias voltage
# NMOS Inverter Configuration
circuit.MOSFET('1', 'Vout', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Load Resistor
circuit.R('1', 'Vout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
