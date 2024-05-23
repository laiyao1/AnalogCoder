bias_voltage = [BIAS_VOLTAGE]
v1_amp = bias_voltage
v2_amp = bias_voltage + 0.125

vin1_name = ""
for element in circuit.elements:
    if "vin1" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin1_name = element.name

if not vin1_name == "":
    circuit.element(vin1_name).detach()
    circuit.V('in1', 'Vin1', circuit.gnd, v1_amp)
    vin1_name = "Vin1"
else:
    circuit.V('in1', 'Vin1', circuit.gnd, v1_amp)
    vin1_name = "Vin1"


vin2_name = ""
for element in circuit.elements:
    if "vin2" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin2_name = element.name
    
if not vin2_name == "":
    circuit.element(vin2_name).detach()
    circuit.V('in2', 'Vin2', circuit.gnd, v2_amp)
    vin2_name = "Vin2"
else:
    circuit.V('in2', 'Vin2', circuit.gnd, v2_amp)
    vin2_name = "Vin2"


for element in circuit.elements:
    if element.name.lower().startswith(vin1_name):
        circuit.element(element.name).dc_value = f"dc {v1_amp}"
    elif element.name.lower().startswith(vin2_name):
        circuit.element(element.name).dc_value = f"dc {v2_amp}"

# print(str(circuit))

simulator = circuit.simulator()


params = {vin1_name: slice(bias_voltage, bias_voltage + 0.5, 0.01)}
# Run a DC analysis
try:
    analysis = simulator.dc(**params)
except:
    print("DC analysis failed.")
    sys.exit(2)

import numpy as np
out_voltage = np.array(analysis.Vout)
in_voltage = np.array(analysis.Vin1)
vin2_voltage = np.array(analysis.Vin2)


import sys


tolerance = 0.2  # 20% Tolerance
for i, out_v in enumerate(out_voltage):
    in_v_1 = in_voltage[i] - bias_voltage
    in_v_2 = v2_amp - bias_voltage
    expected_vout = bias_voltage - (in_v_1 + in_v_2)
    actual_vout = out_v
    if not np.isclose(actual_vout, expected_vout, rtol=tolerance):
        print(f"The circuit does not function correctly as an adder.\n"
            f"Expected Vout: {expected_vout:.4f} V, Vin1 = {in_v_1+bias_voltage:.4f} V, Vin2 = {in_v_2+bias_voltage:.4f} V | Actual Vout: {actual_vout:.4f} V\n")
        sys.exit(2)


print("The op-amp adder functions correctly.\n")
sys.exit(0)