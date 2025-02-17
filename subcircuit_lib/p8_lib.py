from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class NMOSConstantCurrentSource(SubCircuitFactory):
	NAME = ('NMOSConstantCurrentSource')
	NODES = ('Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET model
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supply for the power and input signal
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		self.V('in', 'Vin', self.gnd, 1.5)
		# Common-Source Amplifier with Resistor Load
		# parameters: name, drain, gate, source, bulk, model, w, l
		self.MOSFET('1', 'Vout', 'Vin', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.R('1', 'Vout', 'Vdd', 1@u_kΩ)
