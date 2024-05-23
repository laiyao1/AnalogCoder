from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SingleStageOpamp(SubCircuitFactory):
	NAME = ('SingleStageOpamp')
	NODES = ('Vinp', 'Vinn', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		self.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
		# Power Supplies
		self.V('dd', 'Vdd', self.gnd, 5.0)  # 5V power supply
		self.V('bias', 'Vbias', self.gnd, 1.5)  # Bias voltage for the tail current source M3
		# Input Voltage Sources for Differential Inputs
		# Differential Pair and Tail Current Source
		self.MOSFET('1', 'Voutp', 'Vinp', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('2', 'Vout', 'Vinn', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('3', 'Source3', 'Vbias', self.gnd, self.gnd, model='nmos_model', w=100e-6, l=1e-6)
		# Active Current Mirror Load
		self.MOSFET('4', 'Voutp', 'Voutp', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		self.MOSFET('5', 'Vout', 'Voutp', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
