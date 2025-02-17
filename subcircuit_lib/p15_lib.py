from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SingleStageDiffOpamp(SubCircuitFactory):
	NAME = ('SingleStageDiffOpamp')
	NODES = ('Vinp', 'Vinn', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		self.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
		# Power Supply
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		# Input and Bias Voltages
		self.V('bias1', 'Vbias1', self.gnd, 1.5@u_V) # Bias for NMOS cascode
		self.V('bias2', 'Vbias2', self.gnd, 1.5@u_V) # Bias for NMOS cascode
		self.V('bias3', 'Vbias3', self.gnd, 3.5@u_V) # Bias for PMOS cascode
		self.V('bias4', 'Vbias4', self.gnd, 3.5@u_V) # Bias for PMOS cascode
		self.V('biasTail', 'VbiasTail', self.gnd, 1.0@u_V) # Bias for the tail current source
		# NMOS Transistors
		self.MOSFET('1', 'Drain1', 'Vinp', 'Source5', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('2', 'Drain2', 'Vinn', 'Source5', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('3', 'Voutp', 'Vbias1', 'Drain1', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('4', 'Vout', 'Vbias2', 'Drain2', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('5', 'Source5', 'VbiasTail', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		# PMOS Transistors
		self.MOSFET('6', 'Voutp', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('7', 'Voutp', 'Vbias4', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('8', 'Vout', 'Vbias3', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('9', 'Vout', 'Vbias4', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
