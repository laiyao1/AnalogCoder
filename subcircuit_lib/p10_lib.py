from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class CommonSourceAmpDiodeLoad(SubCircuitFactory):
	NAME = ('CommonSourceAmpDiodeLoad')
	NODES = ('Vin', 'Vout')
	def __init__(self):
		super().__init__()
		# Define the MOSFET models
		self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
		self.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)
		# Power Supply and Input Signal
		self.V('dd', 'Vdd', self.gnd, 5.0)  # 5V power supply
		# Single-Stage Amplifier: Common-Source with PMOS Diode-Connected Load
		# parameters: name, drain, gate, source, bulk, model, w, l
		self.MOSFET('1', 'Vout', 'Vin', self.gnd, self.gnd, model='nmos_model', w=50e-6, l=1e-6)
		self.MOSFET('2', 'Vout', 'Vin', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
		# Include the PMOS diode-connected load
		self.MOSFET('3', 'Vout', 'Vout', 'Vdd', 'Vdd', model='pmos_model', w=100e-6, l=1e-6)
