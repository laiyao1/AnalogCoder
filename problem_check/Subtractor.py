import numpy as np
import sys

# Define the bias voltage and input voltage differences
BIAS_VOLTAGE = [BIAS_VOLTAGE]
v1_amp = BIAS_VOLTAGE*2
v2_amp = BIAS_VOLTAGE*2


vin1_name = ""
for element in circuit.elements:
    if "vin1" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin1_name = element.name

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



# print("vin1_name", vin1_name)
# print("vin2_name", vin2_name)

for element in circuit.elements:
    if element.name.lower().startswith(vin1_name.lower()):
        circuit.element(element.name).dc_value = f"dc {v1_amp}"
    elif element.name.lower().startswith(vin2_name.lower()):
        circuit.element(element.name).dc_value = f"dc {v2_amp}"

# print(str(circuit))

simulator = circuit.simulator()


params = {vin1_name: slice(BIAS_VOLTAGE*2 -2.25, BIAS_VOLTAGE*2 - 1.75, 0.05)}
# Run a DC analysis
try:
    analysis = simulator.dc(**params)
except:
    print("DC analysis failed.")
    sys.exit(2)

# Collect the simulation results
out_voltage = np.array(analysis.Vout)
vin1_voltage = np.array(analysis.Vin1)
vin2_voltage = np.array(analysis.Vin2)

# vinn_voltage = np.array(analysis.inv_input)
# print("vinn_voltage", vinn_voltage)
# print("vin1_voltage", vin1_voltage)
# print("vin2_voltage", vin2_voltage)
# vinp_voltage = np.array(analysis.non_inv_input)
# print("vinp_voltage", vinp_voltage)
# print("out_voltage", out_voltage)

# Define a tolerance for verifying the subtractor's functionality
tolerance = 0.2  # 20% Tolerance

# Iterate over the simulation results to check if the output is Vin2 - Vin1
for i, out_v in enumerate(out_voltage):
    in_v_1 = vin1_voltage[i]
    in_v_2 = v2_amp
    expected_vout = in_v_2 - in_v_1
    actual_vout = out_v
    if not np.isclose(actual_vout, expected_vout, rtol=tolerance):
        print(f"The circuit does not function correctly as a subtractor.\n"
              f"Expected Vout: {expected_vout:.2f} V, Vin1 = {in_v_1:.2f} V, Vin2 = {in_v_2:.2f} V | Actual Vout: {actual_vout:.2f} V\n")
        sys.exit(1)

print("The op-amp subtractor functions correctly.\n")
sys.exit(0)