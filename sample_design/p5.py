from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Single-Stage Cascode Amplifier')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supplies for the power and input signal
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('in', 'Vin', circuit.gnd, 1.5)
circuit.V('bias', 'Vbias', circuit.gnd, 2.5) # Bias voltage for M2, ensuring it's in saturation
# First Stage: Common-Source with NMOS M1
circuit.MOSFET('1', 'Drain1', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Cascode Stage with NMOS M2
circuit.MOSFET('2', 'Vout', 'Vbias', 'Drain1', circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Load Resistor
circuit.R('1', 'Vout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
