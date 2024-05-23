analysis = simulator.operating_point()
for node in analysis.nodes.values(): 
    print(f"{str(node)}\t{float(analysis[str(node)][0]):.6f}")
vin_name = ""
for element in circuit.elements:
    if "vin" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin_name = element.name

circuit.element(vin_name).dc_value = "5"

simulator2 = circuit.simulator()
analysis2 = simulator2.operating_point()

vout2 = float(analysis2["vout"][0])

circuit.element(vin_name).dc_value = "0"

simulator3 = circuit.simulator()
analysis3 = simulator3.operating_point()

vout3 = float(analysis3["vout"][0])

import sys
if vout2 <= 2.5 and vout3 >= 2.5 and vout3 - vout2 >= 1.0:
    print("The circuit functions correctly.\n")
    sys.exit(0)

print("The circuit does not function correctly.\n"
    "It can not invert the input voltage.\n"
    "Please fix the wrong operating point.\n")

sys.exit(2)



