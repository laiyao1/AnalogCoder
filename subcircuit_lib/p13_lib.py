from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SingleStageDiffCommonSourceOpamp(SubCircuitFactory):
	NAME = ('SingleStageDiffCommonSourceOpamp')
	NODES = ('Vinp', 'Vinn', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		# Power Supplies for the power and tail current source
		self.V('dd', 'Vdd', self.gnd, 5.0) # 5V power supply
		# Tail Current Source Biasing (Adjusted to ensure NMOS 3 is activated properly)
		self.V('bias', 'Vbias', self.gnd, 1.5) # Adjusted bias voltage for tail current source
		# Differential Input Voltage Sources (Adjusted to ensure NMOS 1 and NMOS 2 are activated)
		# Differential Pair with adjusted source voltage for activation
		self.MOSFET('1', 'Vout', 'Vinp', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6) # Output taken from Drain1
		self.MOSFET('2', 'Drain2', 'Vinn', 'Source3', 'Source3', model='nmos_model', w=50e-6, l=1e-6)
		# Tail Current Source with adjusted parameters for proper activation
		self.MOSFET('3', 'Source3', 'Vbias', self.gnd, self.gnd, model='nmos_model', w=100e-6, l=1e-6)
		# Load Resistors
		self.R('1', 'Vout', 'Vdd', 1@u_kΩ) # Connected to Vout for correct output node identification
		self.R('2', 'Drain2', 'Vdd', 1@u_kΩ)
