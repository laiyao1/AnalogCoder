load_resistances = [100, 300, 500, 750, 1000]
currents = []

import PySpice.Spice.BasicElement
for element in circuit.elements:
    if isinstance(element, PySpice.Spice.BasicElement.Resistor):
        resistor_name = element.name
        node1, node2 = element.nodes
        break


resistor = circuit[resistor_name]
for r_load in load_resistances:
    resistor.resistance = r_load
    analysis = simulator.operating_point()
    if str(node2) == "0":
        current = float(analysis[str(node1)][0]) / r_load
    elif str(node1) == "0":
        current = - float(analysis[str(node2)][0]) / r_load
    else:
        current = - (float(analysis[str(node1)][0]) - float(analysis[str(node2)][0])) / r_load
    currents.append(current)

for r_load, current in zip(load_resistances, currents):
    print(f"Load: {r_load}, Current: {current}")

tolerance = 1e-6

current_variations = []
for i in range(4):
    current_variations.append(abs(currents[i+1] - currents[i]))

import sys
if min(current_variations) < tolerance and min(currents) > 1e-5:
    pass
    # print("The circuit functions correctly as a constant current source within the given tolerance.")
    # sys.exit(0)
else:
    print("The circuit does not function correctly as a current source.")
    sys.exit(2)

iin_name = None
for element in circuit.elements:
    if "ref" in element.name.lower(): # and element.name.lower().startswith("v"):
        iin_name = element.name

# print("iin_name", iin_name)
if iin_name is None:
    print("The circuit functions correctly as a current source within the given tolerance.")
    sys.exit(0)


circuit.element(iin_name).dc_value = "0.00155"

# print(str(circuit))
simulator = circuit.simulator()
resistor.resistance = 500
analysis = simulator.operating_point()
if str(node2) == "0":
    current = float(analysis[str(node1)][0]) / r_load
elif str(node1) == "0":
    current = - float(analysis[str(node2)][0]) / r_load
else:
    current = - (float(analysis[str(node1)][0]) - float(analysis[str(node2)][0])) / r_load

# print("current", current)
# print("currents", currents)
# print("abs(current - currents[2])", abs(current - currents[2]))
if abs(current - currents[2]) < 1e-6:
    print("The circuit does not as a current source because it cannot replicate the Iref current.")
    sys.exit(2)
else:
    print("The circuit functions correctly as a current source within the given tolerance.")
    sys.exit(0)
