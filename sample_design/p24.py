from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from subcircuits import charge_pump, divider, loop_filter, pfd, ring_vco

###### Netlist #######
circuit = Circuit('Phase Locked Loop')
circuit.model('nmos_model', 'nmos', level=1, kp=400e-6, vto=0.4)
circuit.model('pmos_model', 'pmos', level=1, kp=400e-6, vto=-0.4)

class PLL(SubCircuitFactory):
    __name__ = 'pll'
    __nodes__ = ('vdd', 'vss', 'clk_ref', 'UP', 'DN', 'vctrl',
                 'clk_p', 'clk_n', 'clk_p_45', 'clk_n_45',
                 'clk_p_90', 'clk_n_90', 'clk_p_135', 'clk_n_135')
    def __init__(self, kp, vto):
        SubCircuit.__init__(self, self.__name__, *self.__nodes__)
        # super.__init__()
        self.model('nmos_m', 'nmos', level=1, kp=kp, vto=vto)
        self.model('pmos_m', 'pmos', level=1, kp=kp, vto=-vto)

        self.subcircuit(pfd.PFD(kp=5*kp, vto=vto))
        self.X('0', 'pfd', 'vdd', 'vss', 'clk_ref', 'clk_p', 'UP', 'DN')

        self.subcircuit(charge_pump.ChargePump(kp=3*kp, vto=vto))
        self.X('1', 'charge_pump', 'vdd', 'vss', 'UP', 'DN', 'vctrl')

        self.subcircuit(loop_filter.LF_t2o3(R1=0.1@u_kΩ, R2=3@u_kΩ,
                                            C1=50@u_pF, C2=0.5@u_pF))
        self.X('2', 'loop_filter', 'vss', 'vctrl', 'vctrl_delay')

        self.subcircuit(ring_vco.RingVCO(kp=kp, vto=vto))
        self.X('3', 'ring_vco', 'vdd', 'vss', 'vctrl_delay', 'clk_p', 'clk_n',
                                                             'clk_p_45', 'clk_n_45',
                                                             'clk_p_90', 'clk_n_90',
                                                             'clk_p_135', 'clk_n_135')



circuit.V('VDD', 'vdd', circuit.gnd, 1@u_V)



circuit.subcircuit(PLL(400e-6, 0.4))
circuit.X('0', 'pll', 'vdd', circuit.gnd, 'clk_ref', 'UP', 'DN', 'vctrl',
          'clk_p', 'clk_n', 'clk_p_45', 'clk_n_45',
          'clk_p_90', 'clk_n_90', 'clk_p_135', 'clk_n_135')

##### Simulation #####
simulator = circuit.simulator()
