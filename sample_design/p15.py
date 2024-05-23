from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Telescopic Cascode Opamp')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Power Supply
circuit.V('dd', 'Vdd', circuit.gnd, 5.0)  # 5V power supply
# Bias Voltages
circuit.V('bias1', 'Vbias1', circuit.gnd, 1.5)  # Bias voltage for NMOS cascode
circuit.V('bias2', 'Vbias2', circuit.gnd, 3.5)  # Bias voltage for PMOS cascode load
circuit.V('bias3', 'Vbias3', circuit.gnd, 4.0)  # Additional bias for PMOS cascode load
circuit.V('bias4', 'Vbias4', circuit.gnd, 1.0)  # Bias voltage for tail current source
# Input Signals
circuit.V('inp', 'Vinp', circuit.gnd, 1.48)
circuit.V('inn', 'Vinn', circuit.gnd, 1.48)
# Input Differential Pair
circuit.MOSFET('1', 'Drain1', 'Vinp', 'Source1', 'Source1', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Drain2', 'Vinn', 'Source1', 'Source1', model='nmos_model', w=50e-6, l=1e-6)
# Cascode Devices
circuit.MOSFET('3', 'Voutp', 'Vbias1', 'Drain1', 'Drain1', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('4', 'Vout', 'Vbias1', 'Drain2', 'Drain2', model='nmos_model', w=50e-6, l=1e-6)
# Cascode Loads
circuit.MOSFET('5', 'Voutp', 'Vbias2', 'Source3', 'Source3', model='pmos_model', w=100e-6, l=1e-6)
circuit.MOSFET('6', 'Vout', 'Vbias2', 'Source4', 'Source4', model='pmos_model', w=100e-6, l=1e-6)
# Additional Cascode Loads
circuit.MOSFET('7', 'Source3', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
circuit.MOSFET('8', 'Source4', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
# Tail Current Source
circuit.MOSFET('9', 'Source1', 'Vbias4', circuit.gnd, circuit.gnd, model='nmos_model', w=50e-6, l=1e-6)
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
