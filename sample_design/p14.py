from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Two-Stage Differential Opamp')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supply
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('bias1', 'Vbias1', circuit.gnd, 1.0) # Bias voltage for tail current source
circuit.V('bias2', 'Vbias2', circuit.gnd, 4.0) # Bias voltage for first active load
circuit.V('bias3', 'Vbias3', circuit.gnd, 4.0) # Bias voltage for second active load
# Differential Input
circuit.V('inp', 'Vinp', circuit.gnd, 1.25)
circuit.V('inn', 'Vinn', circuit.gnd, 1.25)
# First Stage: Differential Pair with Active Load and Tail Current Source
circuit.MOSFET('1', 'Drain1', 'Vinp', 'Source1', 'Source1', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Drain2', 'Vinn', 'Source1', 'Source1', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('5', 'Source1', 'Vbias1', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('6', 'Drain1', 'Drain1', 'Vdd', 'Vdd', model='pmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('7', 'Drain2', 'Drain1', 'Vdd', 'Vdd', model='pmos_model', w=50e-6, l=1e-6)
# Second Stage: Common-Source Amplifier with Active Load
circuit.MOSFET('3', 'Voutp', 'Drain1', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('8', 'Voutp', 'Vbias2', 'Vdd', 'Vdd', model='pmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('4', 'Vout', 'Drain2', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('9', 'Vout', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=50e-6, l=1e-6)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
