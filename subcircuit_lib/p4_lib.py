from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class CommonGateAmp(SubCircuitFactory):
	NAME = ('CommonGateAmp')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET model
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supply and Bias Voltage
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		self.V('bias', 'Vbias', self.gnd, 1.5) # Bias voltage for the gate of M1, ensuring it's above threshold
		# Input Signal
		# NMOS Transistor
		self.MOSFET('1', 'Vout', 'Vbias', 'Vin', 'Vin', model='nmos_model', w=50e-6, l=1e-6)
		# Load Resistor
		self.R('1', 'Vout', 'Vdd', 1@u_kΩ)
