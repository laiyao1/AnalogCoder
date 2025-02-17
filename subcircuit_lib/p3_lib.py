from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class CommonDrainAmp(SubCircuitFactory):
	NAME = ('CommonDrainAmp')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET model
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supply for the power
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		# Common-Drain Amplifier with Resistor Load
		self.MOSFET('1', 'Vdd', 'Vin', 'Vout', self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.R('load', 'Vout', self.gnd, 1@u_kΩ)
