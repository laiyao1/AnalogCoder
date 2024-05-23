from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Two-Stage Amplifier with Miller Compensation')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supplies
circuit.V('dd', 'Vdd', circuit.gnd, 5@u_V) # 5V power supply
circuit.V('in', 'Vin', circuit.gnd, 1.0)
circuit.V('bias1', 'Vbias1', circuit.gnd, 4@u_V) # Bias for M2
circuit.V('bias2', 'Vbias2', circuit.gnd, 4@u_V) # Bias for M4
# First Stage: Common-Source with Active Load
circuit.MOSFET('1', 'Drain1', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Drain1', 'Vbias1', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Second Stage: Common-Source with Active Load
circuit.MOSFET('3', 'Vout', 'Drain1', circuit.gnd, circuit.gnd, model='nmos_model', w=100e-6, l=1e-6)
circuit.MOSFET('4', 'Vout', 'Vbias2', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Miller Compensation Capacitor
circuit.C('c', 'Drain1', 'Vout', 10@u_pF)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
