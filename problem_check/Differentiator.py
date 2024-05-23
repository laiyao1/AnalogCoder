vin_name = ""
for element in circuit.elements:
    if "vin" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin_name = element.name

bias_voltage = [BIAS_VOLTAGE]

# Detach the previous Vin if it exists and attach a new triangular wave source
if vin_name != "":
    circuit.element(vin_name).detach()
    circuit.V('tri', 'Vin', circuit.gnd, f"dc {bias_voltage} PULSE({bias_voltage-0.5} {bias_voltage+0.5} 0 50m 50m 1n 100m)")
else:
    circuit.V('in', 'Vin', circuit.gnd, f"dc {bias_voltage} PULSE({bias_voltage-0.5} {bias_voltage+0.5} 0 50m 50m 1n 100m)")

# Adjust R1 resistance if needed
for element in circuit.elements:
    if element.name.lower().startswith("rf") or element.name.lower().startswith("rrf") or element.name.lower().startswith("r1"):
        r_name = element.name
circuit.element(r_name).resistance = "10k"

# Adjust C1 capacitance if needed
for element in circuit.elements:
    if element.name.lower().startswith("c1") or element.name.lower().startswith("cc1"):
        c_name = element.name
circuit.element(c_name).capacitance = "3u"

# Initialize the simulator
simulator = circuit.simulator()


import sys
# Perform transient analysis
try:
    analysis = simulator.transient(step_time=1@u_us, end_time=200@u_ms)
except:
    print("analysis failed.")
    sys.exit(2)


import numpy as np
# Extract data from the analysis
time = np.array(analysis.time)
vin = np.array(analysis['vin'])
vout = np.array(analysis['vout'])

import matplotlib.pyplot as plt
# Plot the response
plt.figure()
plt.plot(time, vout)
plt.title('Response of Op-amp Differentiator')
plt.xlabel('Time [s]')
plt.ylabel('Output Voltage [V]')
plt.grid(True)
plt.savefig("[FIGURE_PATH]")


from scipy.signal import find_peaks
# Check for square wave characteristics in the output
# Calculate the mean voltage level of the peaks and troughs

# print("vout", vout)
# print("max(vout)", max(vout))
# print("min(vout)", min(vout))
min_height = (max(vout) + min(vout)) / 2
# print("min_height", min_height)
num_of_peaks = 2
min_distance = len(vout) / (2 * num_of_peaks) / 1.5 
# print("min_distance", min_distance)

peaks, _ = find_peaks(vout, height=min_height, distance=min_distance)


troughs, _ = find_peaks(-vout, height=-min_height, distance=min_distance)


average_peak_voltage = np.mean(vout[peaks])
average_trough_voltage = np.mean(vout[troughs])



if len(peaks) == 0 or len(troughs) == 0:
    print("No peaks or troughs found in output voltage. Please check the netlist.")
    sys.exit(2)

peak_voltages = vout[peaks]
trough_voltages = vout[troughs]
mean_peak = np.mean(peak_voltages)
mean_trough = np.mean(trough_voltages)


def is_square_wave(waveform, mean_peak, mean_trough, rtol=0.1):
    high_level = np.mean([x for x in waveform if x > (mean_peak + mean_trough) / 2])
    low_level = np.mean([x for x in waveform if x <= (mean_peak + mean_trough) / 2])

    is_high_close = np.isclose(high_level, mean_peak, rtol=rtol)
    is_low_close = np.isclose(low_level, mean_trough, rtol=rtol)

    return is_high_close and is_low_close

# print("mean_peak - bias_voltage", mean_peak - bias_voltage)
# print("mean_trough - bias_voltage", mean_trough - bias_voltage)
# Check if the output is approximately a square wave by comparing the mean of the peaks and troughs
if np.isclose(mean_peak - bias_voltage, -mean_trough+ bias_voltage, rtol=0.2) and \
     np.isclose(mean_peak - bias_voltage, 0.6, rtol=0.2) and \
     is_square_wave(vout, mean_peak, mean_trough):  # 20% tolerance
    # print("The op-amp differentiator functions correctly.\n")
    # sys.exit(0)
    pass
elif not np.isclose(mean_peak - bias_voltage, -mean_trough+ bias_voltage, rtol=0.2):
    print(f"The circuit does not function correctly as a differentiator.\n"
          f"When the input is a triangle wave and the output is not a square wave.\n")
    sys.exit(2)
elif not is_square_wave(vout, mean_peak, mean_trough):
    print(f"The circuit does not function correctly as a differentiator.\n"
          f"When the input is a triangle wave and the output is not a square wave.\n")
    sys.exit(2)
else:
    print(f"The circuit does not function correctly as a differentiator.\n"
          f"Output voltage peak value is wrong. Mean peak voltage: {mean_peak} V | Mean trough voltage: {mean_trough} V\n")
    sys.exit(2)


for element in circuit.elements:
    if element.name.lower().startswith("x"):
        x_name = element.name

circuit.element(x_name).detach()
simulator = circuit.simulator()
try:
    analysis = simulator.transient(step_time=1@u_us, end_time=200@u_ms)
except:
    print("The op-amp differentiator functions correctly.\n")
    sys.exit(0)

time = np.array(analysis.time)
vin = np.array(analysis['vin'])
vout = np.array(analysis['vout'])




min_height = (max(vout) + min(vout)) / 2
num_of_peaks = 2
min_distance = len(vout) / (2 * num_of_peaks) / 1.5 

peaks, _ = find_peaks(vout, height=min_height, distance=min_distance)


troughs, _ = find_peaks(-vout, height=-min_height, distance=min_distance)


average_peak_voltage = np.mean(vout[peaks])
average_trough_voltage = np.mean(vout[troughs])



if len(peaks) == 0 or len(troughs) == 0:
    print(f"The op-amp differentiator functions correctly.\n")
    sys.exit(2)

peak_voltages = vout[peaks]
trough_voltages = vout[troughs]
mean_peak = np.mean(peak_voltages)
mean_trough = np.mean(trough_voltages)


if np.isclose(mean_peak - bias_voltage, -mean_trough+ bias_voltage, rtol=0.2) and np.isclose(mean_peak - bias_voltage, 0.6, rtol=0.2):  # 20% tolerance
    print("The differentiator maybe a passive differentiator.\n")
elif not np.isclose(mean_peak - bias_voltage, -mean_trough+ bias_voltage, rtol=0.2):
    print(f"The op-amp differentiator functions correctly.\n")
    sys.exit(2)
else:
    print(f"The op-amp differentiator functions correctly.\n")
    sys.exit(2)
