from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SingleStageCascodeAmp(SubCircuitFactory):
	NAME = ('SingleStageCascodeAmp')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the NMOS transistor model
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supply for the power and input signal
		self.V('dd', 'Vdd', self.gnd, 5.0)  # 5V power supply
		self.V('bias', 'Vbias', self.gnd, 3.0)  # Bias voltage for the upper transistor
		# Cascode Amplifier Design
		# Lower NMOS transistor M1
		self.MOSFET('1', 'Drain1', 'Vin', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		# Upper NMOS transistor M2 (Cascode)
		self.MOSFET('2', 'Vout', 'Vbias', 'Drain1', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		# Resistive Load
		self.R('load', 'Vout', 'Vdd', 1@u_kΩ)
