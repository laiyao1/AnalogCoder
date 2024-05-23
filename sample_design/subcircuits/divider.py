import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from subcircuits import dff

###### Netlist #######
circuit = Circuit('Frequency Divider')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class Divider_4(SubCircuitFactory):
    __name__ = 'divider_4'
    __nodes__ = ('vdd', 'vss', 'CLK', 'CLK_OUT')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.subcircuit(dff.DFF(kp, vto))
        self.X('1', 'd_flip_flop', 'vdd', 'vss', 'D1', 'CLK', 'Q1')

        self.M(1, 'D1', 'Q1', 'vdd', 'vdd', model='pmos_m')
        self.M(2, 'D1', 'Q1', 'vss', 'vss', model='nmos_m')

        self.subcircuit(dff.DFF(kp, vto))
        self.X('2', 'd_flip_flop', 'vdd', 'vss', 'D2', 'Q1', 'Q2')

        self.M(3, 'D2', 'Q2', 'vdd', 'vdd', model='pmos_m')
        self.M(4, 'D2', 'Q2', 'vss', 'vss', model='nmos_m')

        self.M(5, 'CLK_OUT_B', 'Q2', 'vdd', 'vdd', model='pmos_m')
        self.M(6, 'CLK_OUT_B', 'Q2', 'vss', 'vss', model='nmos_m')
        self.M(7, 'CLK_OUT', 'CLK_OUT_B', 'vdd', 'vdd', model='pmos_m')
        self.M(8, 'CLK_OUT', 'CLK_OUT_B', 'vss', 'vss', model='nmos_m')



circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.PulseVoltageSource('2', 'CLK', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=100@u_ns, period=200@u_ns, delay_time=100@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)

circuit.subcircuit(Divider_4(400e-6, 0.4))
circuit.X('1', 'divider_4', 'vdd', circuit.gnd, 'CLK', 'CLK_OUT')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=10@u_ns, end_time=2500@u_ns)

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# plt.plot(list(analysis.time), list(analysis["CLK"]))
# plt.plot(list(analysis.time), list(analysis["CLK_OUT"]))
# plt.show()
# fig.savefig("./outputs/divider.png")
# plt.close(fig)
######################