import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

###### Netlist #######
circuit = Circuit('NAND Gate')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class INV(SubCircuitFactory):
    __name__ = 'inv'
    __nodes__ = ('vdd', 'vss', 'I', 'O_delay')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.M(0, 'O', 'I', 'vdd', 'vdd', model='pmos_m')
        self.M(1, 'O', 'I', 'vss', 'vss', model='nmos_m')

        self.R(0, 'O', 'O_delay', 0.01@u_kΩ)
        self.C(0, 'O_delay', 'vss', 0.1@u_pF)


class TINV(SubCircuitFactory):
    __name__ = 'tinv'
    __nodes__ = ('vdd', 'vss', 'I', 'EN', 'O_delay')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.subcircuit(INV(kp, vto))
        self.X('0', 'inv', 'vdd', 'vss', 'EN', 'ENB')

        self.M(0, 'vp', 'I', 'vdd', 'vdd', model='pmos_m')
        self.M(1, 'vn', 'I', 'vss', 'vss', model='nmos_m')
        self.M(2, 'O', 'ENB', 'vp', 'vdd', model='pmos_m')
        self.M(3, 'O', 'EN', 'vn', 'vss', model='nmos_m')

        self.R(0, 'O', 'O_delay', 0.02@u_kΩ)
        self.C(0, 'O_delay', 'vss', 0.2@u_pF)


class NAND(SubCircuitFactory):
    __name__ = 'nand'
    __nodes__ = ('vdd', 'vss', 'A', 'B', 'O_delay')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.M(0, 'O', 'A', 'vdd', 'vdd', model='pmos_m')
        self.M(1, 'O', 'B', 'vdd', 'vdd', model='pmos_m')
        self.M(2, 'O', 'A', 'v1', 'vss', model='nmos_m')
        self.M(3, 'v1', 'B', 'vss', 'vss', model='nmos_m')

        self.R(0, 'O', 'O_delay', 0.04@u_kΩ)
        self.C(0, 'O_delay', 'vss', 0.4@u_pF)


circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.PulseVoltageSource('0', 'A', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=150@u_ns, period=300@u_ns, delay_time=30@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.PulseVoltageSource('1', 'B', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=100@u_ns, period=200@u_ns, delay_time=100@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)

circuit.subcircuit(NAND(400e-6, 0.4))
circuit.X('0', 'nand', 'vdd', circuit.gnd, 'A', 'B', 'O')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=10@u_ns, end_time=1500@u_ns)

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# # plt.plot(list(analysis.time), list(analysis["A"]))
# # plt.plot(list(analysis.time), list(analysis["B"]))
# plt.plot(list(analysis.time), list(analysis["O"]))
# plt.show()
# fig.savefig("./outputs/nand.png")
# plt.close(fig)
######################