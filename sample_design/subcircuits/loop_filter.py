import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

###### Netlist #######
circuit = Circuit('Loop Filter')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class LF_t2o3(SubCircuitFactory):
    __name__ = 'loop_filter'
    __nodes__ = ('vss', 'i', 'o')
    def __init__(self, R1, R2, C1, C2):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()

        self.R(0, 'i', 'o', R1)
        self.R(1, 'o', 'c1_up', R2)
        self.C(1, 'c1_up', 'vss', C1)
        self.C(2, 'o', 'vss', C2)
######################