simulator_id = circuit.simulator()
mosfet_names = []
import PySpice.Spice.BasicElement
for element in circuit.elements:
    if isinstance(element, PySpice.Spice.BasicElement.Mosfet):
        mosfet_names.append(element.name)

mosfet_name_ids = []
for mosfet_name in mosfet_names:
    mosfet_name_ids.append(f"@{mosfet_name}[id]")

simulator_id.save_internal_parameters(*mosfet_name_ids)
analysis_id = simulator_id.operating_point()

id_correct = 1
for mosfet_name in mosfet_names:
    mosfet_id = float(analysis_id[f"@{mosfet_name}[id]"][0])
    if mosfet_id < 1e-5:
        id_correct = 0
        print("The circuit does not function correctly. "
          "the current I_D for {} is 0. ".format(mosfet_name)
          .format(mosfet_name))

if id_correct == 0:
    print("Please fix the wrong operating point.\n")
    sys.exit(2)


frequency = 100@u_Hz
analysis = simulator.ac(start_frequency=frequency, stop_frequency=frequency*10, 
    number_of_points=2, variation='dec')

import numpy as np

node = 'vout'
output_voltage = analysis[node].as_ndarray()[0]
gain = np.abs(output_voltage / (1e-6))

print(f"Common-Mode Gain (Av) at 100 Hz: {gain}")

vinn_name = ""
for element in circuit.elements:
    # print("element name", element.name)
    # for pin in element.pins:
    #     print("pin name", pin.node)
    if "vinn" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vinn_name = element.name


circuit.element(vinn_name).dc_value += " 180"

simulator2 = circuit.simulator()
analysis2 = simulator2.ac(start_frequency=frequency, stop_frequency=frequency, 
                        number_of_points=1, variation='dec')

output_voltage2 = np.abs(analysis2[node].as_ndarray()[0])
gain2 = output_voltage2 / (1e-6)

print(f"Differential-Mode Gain (Av) at 100 Hz: {gain2}")

required_gain = 1e-5
import sys

if gain < gain2 - 1e-5 and gain2 > required_gain:
    print("The circuit functions correctly at 100 Hz.\n")
    sys.exit(0)

if gain >= gain2 - 1e-5:
    print("Common-Mode gain is larger than Differential-Mode gain.\n")

if gain2 < required_gain:
    print("Differential-Mode gain is smaller than 1e-5.\n")

print("The circuit does not function correctly.\n"
    "Please fix the wrong operating point.\n")
sys.exit(2)