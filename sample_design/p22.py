from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from subcircuits.diffop import *

circuit = Circuit('Schmitt Trigger')

# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)

# Set the DC supply voltage
Vdd = 5.0@u_V

# Define the DC operating voltage for Vinp/Vinn
Vop = 2.5@u_V

# Declare the subcircuit
circuit.subcircuit(SingleStageOpamp())

# Create a subcircuit instance
circuit.X('opamp', 'SingleStageOpamp', 'non_inverting', 'inverting', 'Vout')

# Define feedback resistors for hysteresis
Rf = 20@u_kΩ # Feedback resistor
R1 = 10@u_kΩ  # Input resistor

# Connect the non-inverting input to the output through the feedback resistor
circuit.R('f', 'non_inverting', 'Vout', Rf)
# Connect a resistor from the input to the non-inverting input
circuit.R('1', 'Vin', 'non_inverting', R1)

# Connect the inverting input to ground through a resistor to set the reference voltage
circuit.R('2', 'inverting', circuit.gnd, R1)

# Connect a resistor from Vdd to the inverting input to form a voltage divider with R2
# This sets the inverting input to Vdd/2 when the output is at Vdd (positive feedback condition)
circuit.R('3', 'Vdd', 'inverting', R1)
circuit.V('dd', 'Vdd', circuit.gnd, Vdd)
circuit.V('in', 'Vin', circuit.gnd, 1.0@u_V)

# Finalize the Circuit
simulator = circuit.simulator()
analysis = simulator.operating_point()