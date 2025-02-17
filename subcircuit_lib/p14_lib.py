from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class OpampResistanceLoad(SubCircuitFactory):
	NAME = ('OpampResistanceLoad')
	NODES = ('Vinp', 'Vinn', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		self.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
		# Power Supplies
		self.V('dd', 'Vdd', self.gnd, 5.0)  # 5V power supply
		# Bias voltages and input signals
		self.V('bias1', 'Vbias1', self.gnd, 2.5)  # Bias for active loads
		self.V('bias2', 'Vbias2', self.gnd, 1.0)  # Bias for tail current source
		self.V('bias3', 'Vbias3', self.gnd, 2.5)  # Bias for second stage active load
		# First Stage: Differential Pair with Active Load and Tail Current Source
		self.MOSFET('1', 'Drain1', 'Vinp', 'Source5', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('2', 'Drain2', 'Vinn', 'Source5', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('3', 'Drain1', 'Vbias1', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('4', 'Drain2', 'Vbias1', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('5', 'Source5', 'Vbias2', self.gnd, self.gnd, model='nmos_model', w=100e-6, l=1e-6)
		# Second Stage: Common-Source with Active Load
		self.MOSFET('6', 'Vout', 'Drain1', self.gnd, self.gnd, model='nmos_model', w=100e-6, l=1e-6)
		self.MOSFET('7', 'Vout', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
