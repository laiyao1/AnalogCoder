import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from subcircuits import opamp, loop_filter, logic_gates


###### Netlist #######
circuit = Circuit('Charge Pump')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class ChargePump(SubCircuitFactory):
    __name__ = 'charge_pump'
    __nodes__ = ('vdd', 'vss', 'up', 'dn', 'vctrl')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)
        self.model('nmos_m2', 'nmos', level=1, kp=kp*10, vto=vto)
        self.model('pmos_m2', 'pmos', level=1, kp=kp*10, vto=-vto)

        self.CurrentSource('1', 'vdd', 'vn1', 300@u_uA)

        self.subcircuit(logic_gates.INV(kp=kp, vto=vto))
        self.X('0', 'inv', 'vdd', 'vss', 'dn', 'dn_inv')

        self.M(1, 'vp1', 'vp1', 'vdd', 'vdd', model='pmos_m2')
        # self.M(2, 'op1_p', 'vp2', 'vdd', 'vdd', model='pmos_m')
        # self.M(3, 'op2_p', 'vp1', 'vdd', 'vdd', model='pmos_m')
        self.M(4, 'm4_d', 'dn_inv', 'vdd', 'vdd', model='pmos_m')
        # self.M(5, 'm5_d', 'dn_inv', 'vdd', 'vdd', model='pmos_m')
        self.M(6, 'vctrl', 'vp1', 'm4_d', 'vdd', model='pmos_m')
        # self.M(7, 'vctrl', 'vp2', 'm5_d', 'vdd', model='pmos_m')

        # self.subcircuit(opamp.OpAmp(kp=kp, vto=0.4))
        # self.X('1', 'op_amp', 'vdd', 'vss', 'op1_p', 'vctrl', 'vp2')

        # self.subcircuit(opamp.OpAmp(kp=kp, vto=0.4))
        # self.X('2', 'op_amp', 'vdd', 'vss', 'op2_p', 'vctrl', 'vn2')

        self.M(8, 'vn1', 'vn1', 'vss', 'vss', model='nmos_m2')
        self.M(9, 'vp1', 'vn1', 'vss', 'vss', model='nmos_m2')
        # self.M(10, 'op1_p', 'vn1', 'vss', 'vss', model='nmos_m')
        # self.M(11, 'op2_p', 'vn2', 'vss', 'vss', model='nmos_m')
        self.M(12, 'm12_d', 'up', 'vss', 'vss', model='nmos_m')
        # self.M(13, 'm13_d', 'up', 'vss', 'vss', model='nmos_m')
        self.M(14, 'vctrl', 'vn1', 'm12_d', 'vss', model='nmos_m')
        # self.M(15, 'vctrl', 'vn2', 'm13_d', 'vss', model='nmos_m')



circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.PulseVoltageSource('1', 'up', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=90@u_ns, period=200@u_ns, delay_time=10@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)
circuit.PulseVoltageSource('2', 'dn', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                           pulse_width=30@u_ns, period=200@u_ns, delay_time=70@u_ns, rise_time=0.2@u_ns, fall_time=0.2@u_ns)

circuit.subcircuit(ChargePump(400e-6, 0.4))
circuit.X('0', 'charge_pump', 'vdd', circuit.gnd, 'up', 'dn', 'vctrl')

circuit.subcircuit(loop_filter.LF_t2o3(R1=1@u_kΩ, R2=1@u_kΩ,
                                       C1=30@u_pF, C2=5@u_pF))
circuit.X('1', 'loop_filter', circuit.gnd, 'vctrl')
######################


##### Simulation #####
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# # simulator.initial_condition(vctrl=0.5@u_V, op1_p=0.5@u_V, op2_p=0.5@u_V)
# analysis = simulator.transient(step_time=100@u_ns, end_time=1@u_us)

# fig = plt.figure()
# # plt.ylim((-0.02, 1.02))
# plt.plot(list(analysis.time), list(analysis["up"]))
# plt.plot(list(analysis.time), list(analysis["dn"]))
# plt.plot(list(analysis.time), list(analysis["vctrl"]))
# # plt.plot(list(analysis.time), list(analysis["vn1"]))
# # plt.plot(list(analysis.time), list(analysis["vp1"]))
# plt.show()
# fig.savefig("./outputs/charge_pump.png")
# plt.close(fig)
######################