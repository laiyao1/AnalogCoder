from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Single-Stage Amplifier with PMOS Diode-Connected Load')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supplies for the power and input signal
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('in', 'Vin', circuit.gnd, 2.5)
# Amplifier Stage: Common-Source with PMOS Diode-Connected Load
# parameters: name, drain, gate, source, bulk, model, w, l
circuit.MOSFET('1', 'Vout', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Vout', 'Vout', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
