from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Single-Stage Common-Source Amplifier')
# Define the NMOS transistor model
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supply for the power and input signal
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
circuit.V('in', 'Vin', circuit.gnd, 1.5)
# Single-Stage Common-Source Amplifier with Resistive Load
circuit.MOSFET('1', 'Vout', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.R('1', 'Vout', 'Vdd', 1@u_kΩ)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
