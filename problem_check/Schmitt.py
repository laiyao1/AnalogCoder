vin_name = "Vin"
for element in circuit.elements:
    if "vin" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin_name = element.name

params = {vin_name: slice(0, 5, 0.1)}

try:
    analysis = simulator.dc(**params)
except:
    print("DC analysis failed.")
    sys.exit(2)

params2 = {vin_name: slice(5, 0, -0.1)}

simulator2 = circuit.simulator()

try:
    analysis2 = simulator2.dc(**params2)
except:
    print("DC analysis failed.")
    sys.exit(2)

import numpy as np
import matplotlib.pyplot as plt


vin = np.array(analysis[vin_name])
vout = np.array(analysis['Vout'])
vin2 = np.flip(np.array(analysis2[vin_name]))
vout2 = np.flip(np.array(analysis2['Vout']))

threshold = 2.5


try:
    trigger_index = np.where(vout > threshold)[0][0]
except:
    print("The circuit does not function correctly. The output voltage does not cross the Vdd/2.")
    sys.exit(2)

trigger_vin = vin[trigger_index]

try:
    trigger_index2 = np.where(vout2 > threshold)[0][0]
except:
    print("The circuit does not function correctly. The output voltage does not cross the Vdd/2.")
    sys.exit(2)

trigger_vin2 = vin2[trigger_index2]


# Plot the input and output waveforms
plt.figure()
plt.plot(vin, vin, label='Vin')
plt.plot(vin, vout, label='Vout')
plt.plot(vin2, vout2, label='Vout2')
plt.title('Schmitt Trigger Input and Output Waveforms')
plt.xlabel('vin [V]')
plt.ylabel('Voltage [V]')
plt.legend()
plt.grid(True)
plt.savefig("[FIGURE_PATH].png")

if abs(trigger_vin - trigger_vin2) <= 0.05:
    print("The circuit does not function correctly. Trigger points are too close.")
    print(f"Trigger points: {trigger_vin:.5f}V and {trigger_vin2:.5f}V are not sufficiently different. Please use the positive feedback which the Rf should connect to the non-inverting input of the op-amp.")
    sys.exit(2)
elif vout[-1] - vout[0] < 2.5 or vout2[-1] - vout2[0] < 2.5:
    print("The circuit does not function correctly. The output voltage does not vary more than Vdd/2.")
    sys.exit(2)
elif not np.all(np.diff(vout)>=0) or not np.all(np.diff(vout2)>=0):
    print("The circuit does not function correctly. The output voltage variation does not monotonically increase with increasing input voltage.")
    sys.exit(2)

print("The circuit functions correctly with different trigger points.")
sys.exit(0)