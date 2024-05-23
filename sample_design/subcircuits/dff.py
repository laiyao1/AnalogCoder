import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from subcircuits import logic_gates


###### Netlist #######
circuit = Circuit('D Flip Flop')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class DFF(SubCircuitFactory):
    __name__ = 'd_flip_flop'
    __nodes__ = ('vdd', 'vss', 'D', 'CLK', 'Q')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('1', 'inv', 'vdd', 'vss', 'CLK', 'CLKB')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('2', 'tinv', 'vdd', 'vss', 'D', 'CLKB', 'v1')

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('3', 'inv', 'vdd', 'vss', 'v1', 'v1_b')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('4', 'tinv', 'vdd', 'vss', 'v1_b', 'CLK', 'v1')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('5', 'tinv', 'vdd', 'vss', 'v1_b', 'CLK', 'v2')

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('6', 'inv', 'vdd', 'vss', 'v2', 'Q')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('7', 'tinv', 'vdd', 'vss', 'Q', 'CLKB', 'v2')



class DFF_RST(SubCircuitFactory):
    __name__ = 'd_flip_flop_with_rst'
    __nodes__ = ('vdd', 'vss', 'D', 'CLK', 'RSTB', 'Q')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('0', 'inv', 'vdd', 'vss', 'CLK', 'CLKB')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('1', 'tinv', 'vdd', 'vss', 'D', 'CLKB', 'v1')

        self.M(1, 'v1', 'RSTB', 'vdd', 'vdd', model='pmos_m')

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('2', 'inv', 'vdd', 'vss', 'v1', 'v1_b')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('3', 'tinv', 'vdd', 'vss', 'v1_b', 'CLK', 'v1')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('4', 'tinv', 'vdd', 'vss', 'v1_b', 'CLK', 'v2')

        self.M(2, 'v2', 'RSTB', 'vdd', 'vdd', model='pmos_m')

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('5', 'inv', 'vdd', 'vss', 'v2', 'Q')

        self.subcircuit(logic_gates.TINV(kp=kp, vto=vto))
        self.X('6', 'tinv', 'vdd', 'vss', 'Q', 'CLKB', 'v2')




circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.PulseVoltageSource('1', 'D', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=150@u_ns, period=300@u_ns, delay_time=30@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.PulseVoltageSource('2', 'CLK', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=100@u_ns, period=200@u_ns, delay_time=100@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.PulseVoltageSource('3', 'rstb', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=800@u_ns, period=850@u_ns, delay_time=10@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)

circuit.subcircuit(DFF_RST(400e-6, 0.4))
circuit.X('1', 'd_flip_flop_with_rst', 'vdd', circuit.gnd, 'D', 'CLK', 'rstb', 'Q')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=10@u_ns, end_time=1500@u_ns)

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# # plt.plot(list(analysis.time), list(analysis["D"]))
# plt.plot(list(analysis.time), list(analysis["rstb"]))
# # plt.plot(list(analysis.time), list(analysis["CLKB"]))
# plt.plot(list(analysis.time), list(analysis["Q"]))
# plt.show()
# fig.savefig("./outputs/dff.png")
# plt.close(fig)
######################