from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

class OpAmp(SubCircuitFactory):
    __name__ = 'op_amp'
    __nodes__ = ('vdd', 'vss', 'in_p', 'in_n', 'vout')
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

circuit = Circuit('Voltage Controlled Oscillator with two OP Amps')
circuit.model('nmos_model', 'nmos', level=1, kp=1000e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)
circuit.V('in', 'vin', circuit.gnd, 0.7@u_V)

R1 = 15@u_kΩ
R2 = 30@u_kΩ
R3 = 1@u_kΩ
R4 = 30@u_kΩ
R5 = 3@u_kΩ
R6 = 30@u_kΩ
R7 = 30@u_kΩ
C1 = 5e-1@u_nF

opamp_kp = 400e-6; opamp_vto = 0.4

circuit.R(1, 'vin', 'op1_n', R1)
circuit.R(2, 'vin', 'op1_p', R2)
circuit.R(3, 'nmos_g', 'vout', R3)
circuit.R(4, 'op1_p', circuit.gnd, R4)
circuit.R(5, 'nmos_d', 'op1_n', R5)
circuit.R(6, 'op2_p', circuit.gnd, R6)
circuit.R(7, 'op2_p', 'vout', R7)

circuit.C(1, 'op1_n', 'vout_1', C1)

circuit.M(1, 'nmos_d', 'nmos_g', circuit.gnd, circuit.gnd, model='nmos_model')

circuit.subcircuit(OpAmp(2*opamp_kp, opamp_vto))
circuit.X('1', 'op_amp', 'vdd', circuit.gnd, 'op1_p', 'op1_n', 'vout_1')

circuit.subcircuit(OpAmp(0.7*opamp_kp, opamp_vto))
circuit.X('2', 'op_amp', 'vdd', circuit.gnd, 'op2_p', 'vout_1', 'vout')

simulator = circuit.simulator()