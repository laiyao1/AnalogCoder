from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class ThreeStageAmp(SubCircuitFactory):
	NAME = ('ThreeStageAmp')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supply for the power
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		# Input Signal
		# First Stage: Common-Source with Resistor Load
		self.MOSFET('1', 'Drain1', 'Vin', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.R('1', 'Drain1', 'Vdd', 1@u_kΩ)
		# Second Stage: Common-Source with Resistor Load
		self.MOSFET('3', 'Drain2', 'Drain1', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.R('2', 'Drain2', 'Vdd', 1@u_kΩ)
		# Third Stage: Common-Source with Resistor Load
		self.MOSFET('5', 'Vout', 'Drain2', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.R('3', 'Vout', 'Vdd', 1@u_kΩ)
