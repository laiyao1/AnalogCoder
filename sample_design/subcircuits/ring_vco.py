import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from subcircuits import logic_gates


###### Netlist #######
circuit = Circuit('Ring Voltage Controlled Oscillator')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class StarvedInvDelayLine(SubCircuitFactory):
    __name__ = 'delay_line'
    __nodes__ = ('vdd', 'vss', 'in_p', 'in_n', 'vctrl', 'out_p', 'out_n')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()
       
        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.subcircuit(logic_gates.INV(kp, vto))
        self.X('0', 'inv', 'vp1', 'vss', 'in_p', 'out_n')
        self.M(0, 'vp1', 'vctrl', 'vdd', 'vdd', model='pmos_m')

        self.subcircuit(logic_gates.INV(kp, vto))
        self.X('1', 'inv', 'vp2', 'vss', 'in_n', 'out_p')
        self.M(1, 'vp2', 'vctrl', 'vdd', 'vdd', model='pmos_m')

        self.subcircuit(logic_gates.INV(kp, vto))
        self.X('2', 'inv', 'vdd', 'vss', 'out_p', 'out_n')
        self.subcircuit(logic_gates.INV(kp, vto))
        self.X('3', 'inv', 'vdd', 'vss', 'out_n', 'out_p')


class RingVCO(SubCircuitFactory):
    __name__ = 'ring_vco'
    __nodes__ = ('vdd', 'vss', 'vctrl', 'clk_p', 'clk_n',
                                        'clk_p_45', 'clk_n_45',
                                        'clk_p_90', 'clk_n_90',
                                        'clk_p_135', 'clk_n_135')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.subcircuit(StarvedInvDelayLine(kp, vto))
        self.X('1', 'delay_line', 'vdd', 'vss', 'clk_p', 'clk_n', 'vctrl', 'clk_p_45', 'clk_n_45')

        self.subcircuit(StarvedInvDelayLine(kp, vto))
        self.X('2', 'delay_line', 'vdd', 'vss', 'clk_p_45', 'clk_n_45', 'vctrl', 'clk_p_90', 'clk_n_90')

        self.subcircuit(StarvedInvDelayLine(kp, vto))
        self.X('3', 'delay_line', 'vdd', 'vss', 'clk_p_90', 'clk_n_90', 'vctrl', 'clk_p_135', 'clk_n_135')

        self.subcircuit(StarvedInvDelayLine(kp, vto))
        self.X('4', 'delay_line', 'vdd', 'vss', 'clk_p_135', 'clk_n_135', 'vctrl', 'clk_n', 'clk_p')



circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.V('ctrl', 'vctrl', circuit.gnd, 0@u_V)

circuit.subcircuit(RingVCO(400e-6, 0.4))
circuit.X('1', 'ring_vco', 'vdd', circuit.gnd, 'vctrl', 'clk_p', 'clk_n',
                                                        'clk_p_45', 'clk_n_45',
                                                        'clk_p_90', 'clk_n_90',
                                                        'clk_p_135', 'clk_n_135')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# simulator.initial_condition(clk_p=0.5@u_V, clk_n=0.5@u_V,
#                             clk_p_45=0.5@u_V, clk_n_45=0.5@u_V,
#                             clk_p_90=0.5@u_V, clk_n_90=0.5@u_V,
#                             clk_p_135=0.5@u_V, clk_n_135=0.5@u_V)
# analysis = simulator.transient(step_time=10@u_ns, end_time=3@u_us)


# # ### Find frequency
# import numpy as np
# time = np.array(analysis.time)  # Time points array
# vout = np.array(analysis['clk_p'])  # Output voltage array
# # Find zero-crossings
# zero_crossings = np.where(np.diff(np.sign(vout-0.5))[5:])[0]
# # Calculate periods by subtracting consecutive zero-crossing times
# periods = np.diff(time[zero_crossings])
# # Average period
# average_period = np.mean(periods)
# # Frequency is the inverse of the period
# frequency = 1 / average_period
# print()
# print(f"Frequency: {frequency*1e-6} MHz")
# print()

# fig = plt.figure()
# plt.ylim((-0.2, 1.2))
# plt.plot(list(analysis.time), list(analysis["clk_p"]))
# plt.show()
# fig.savefig("./outputs/ring_vco.png")
# plt.close(fig)
######################