import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *


###### Netlist #######
circuit = Circuit('OpAmp')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class OpAmp(SubCircuitFactory):
    __name__ = 'op_amp'
    __nodes__ = ('vdd', 'vss', 'in_p', 'in_n', 'vout_delay')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.M(1, 'v1', 'v2', 'vdd', 'vdd', model='pmos_m')
        self.M(2, 'v2', 'v2', 'vdd', 'vdd', model='pmos_m')
        self.M(3, 'vout', 'v2', 'vdd', 'vdd', model='pmos_m')
        self.M(4, 'v3', 'in_n', 'v1', 'vdd', model='pmos_m')
        self.M(5, 'v4', 'in_p', 'v1', 'vdd', model='pmos_m')

        self.M(6, 'v3', 'v3', 'vss', 'vss', model='nmos_m')
        self.M(7, 'v4', 'v3', 'vss', 'vss', model='nmos_m')
        self.M(8, 'v2', 'vdd', 'vss', 'vss', model='nmos_m')
        self.M(9, 'vout', 'v4', 'vss', 'vss', model='nmos_m')

        self.R(1, 'vout', 'vout_delay', 1@u_kΩ)
        self.C(1, 'vout_delay', 'vss', 1@u_pF)


circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.V('INP', 'vinp', circuit.gnd, 0.54@u_V)
circuit.V('INN', 'vinn', circuit.gnd, 0.55@u_V)

circuit.subcircuit(OpAmp(400e-6, 0.4))
circuit.X('1', 'op_amp', 'vdd', circuit.gnd, 'vinp', 'vinn', 'vout')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=1@u_us, end_time=500@u_us)

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# # plt.plot(list(analysis.time), list(analysis["vinp"]))
# # plt.plot(list(analysis.time), list(analysis["vinn"]))
# plt.plot(list(analysis.time), list(analysis["vout"]))
# plt.show()
# fig.savefig("./outputs/opamp.png")
# plt.close(fig)
######################