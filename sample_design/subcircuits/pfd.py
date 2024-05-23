import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
from subcircuits import logic_gates
from subcircuits import dff

###### Netlist #######
circuit = Circuit('Phase Frequency Detector')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class PFD(SubCircuitFactory):
    __name__ = 'pfd'
    __nodes__ = ('vdd', 'vss', 'clk_ref', 'clk_fb', 'UP', 'DN')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.subcircuit(dff.DFF_RST(kp=kp, vto=vto))
        self.X('0', 'd_flip_flop_with_rst', 'vdd', 'vss', 'vdd', 'clk_ref', 'rstb', 'UP')

        self.subcircuit(dff.DFF_RST(kp=kp, vto=vto))
        self.X('1', 'd_flip_flop_with_rst', 'vdd', 'vss', 'vdd', 'clk_fb', 'rstb', 'DN')

        self.subcircuit(logic_gates.NAND(kp=kp, vto=vto))
        self.X('2', 'nand', 'vdd', 'vss', 'UP', 'DN', 'rstb')

        # self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        # self.X('5', 'inv', 'vdd', 'vss', 'rstbbb', 'rstbb')
        # self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        # self.X('6', 'inv', 'vdd', 'vss', 'rstbb', 'rstb')


circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.PulseVoltageSource('1', 'clk_ref', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=5@u_ns, period=10@u_ns, delay_time=30@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.PulseVoltageSource('2', 'clk_fb', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=15@u_ns, period=30@u_ns, delay_time=100@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.subcircuit(PFD(400e-6, 0.4))
circuit.X('0', 'pfd', 'vdd', circuit.gnd, 'clk_ref', 'clk_fb', 'UP', 'DN', 'rstb')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# simulator.initial_condition(rstb=0@u_V)
# analysis = simulator.transient(step_time=1@u_us, end_time=1500@u_ns)

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# # plt.plot(list(analysis.time), list(analysis["rstb"]))
# plt.plot(list(analysis.time), list(analysis["UP"]))
# plt.plot(list(analysis.time), list(analysis["DN"]))
# plt.show()
# fig.savefig("./outputs/pfd.png")
# plt.close(fig)
######################