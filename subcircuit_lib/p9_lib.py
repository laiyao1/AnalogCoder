from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class TwoStageOpampMiller(SubCircuitFactory):
	NAME = ('TwoStageOpampMiller')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		self.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
		# Power Supplies
		self.V('dd', 'Vdd', self.gnd, 5@u_V) # 5V power supply
		self.V('bias1', 'Vbias1', self.gnd, 4@u_V) # Bias for M2
		self.V('bias2', 'Vbias2', self.gnd, 4@u_V) # Bias for M4
		# First Stage: Common-Source with Active Load
		self.MOSFET('1', 'Drain1', 'Vin', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('2', 'Drain1', 'Vbias1', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		# Second Stage: Common-Source with Active Load
		self.MOSFET('3', 'Vout', 'Drain1', self.gnd, self.gnd, model='nmos_model', w=100e-6, l=1e-6)
		self.MOSFET('4', 'Vout', 'Vbias2', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		# Miller Compensation Capacitor
		self.C('c', 'Drain1', 'Vout', 10@u_pF)
