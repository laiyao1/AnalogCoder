import math
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *
circuit = Circuit('Opamp Differentiator')
# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
# Input voltage source
circuit.V('input', 'Vin', circuit.gnd, 2.5@u_V)
# DC operating voltage for the non-inverting input
circuit.V('dc_bias', 'Vdc', circuit.gnd, 2.5@u_V)
# Declare and use the SingleStageOpamp subcircuit
circuit.subcircuit(SingleStageOpamp())
circuit.X('op', 'SingleStageOpamp', 'Vdc', 'n1', 'Vout')
# Components for differentiator
Rf = 10@u_kΩ
C1 = 10@u_nF
# Connect the components
circuit.R('f', 'Vout', 'n1', Rf)
circuit.C('1', 'n1', 'Vin', C1)
simulator = circuit.simulator()
analysis = simulator.operating_point()
