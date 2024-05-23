from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
circuit = Circuit('Single-Stage Differential Common-Source Opamp')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
# Power Supplies for the power and input signal
circuit.V('dd', 'Vdd', circuit.gnd, 5.0) # 5V power supply
circuit.V('bias', 'Vbias', circuit.gnd, 1.0) # 1V input for bias voltage (= V_th + 0.5 = 0.5 + 0.5 = 1.0)
circuit.V('inp', 'Vinp', circuit.gnd, 0.93)
circuit.V('inn', 'Vinn', circuit.gnd, 0.93)
# Differential Pair: M1 and M2
circuit.MOSFET('1', 'Drain1', 'Vinp', 'SourceCommon', 'SourceCommon', model='nmos_model', w=50e-6, l=1e-6)
circuit.MOSFET('2', 'Drain2', 'Vinn', 'SourceCommon', 'SourceCommon', model='nmos_model', w=50e-6, l=1e-6)
# Tail Current Source: M3
circuit.MOSFET('3', 'SourceCommon', 'Vbias', circuit.gnd, circuit.gnd, model='nmos_model', w=100e-6, l=1e-6)
# Load Resistors
circuit.R('1', 'Drain1', 'Vdd', 10@u_kΩ) # Load resistor for M1
circuit.R('2', 'Drain2', 'Vdd', 10@u_kΩ) # Load resistor for M2
# Output
circuit.R('load', 'Vout', 'Drain1', 1@u_Ω) # Ideal wire for output node
# Analysis Part
simulator = circuit.simulator()
analysis = simulator.operating_point()
