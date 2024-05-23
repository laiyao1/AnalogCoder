del_vname = []
for element in circuit.elements:
    v_name = element.name
    if element.name.lower().startswith("v"):
        del_vname.append(v_name)


pin_name = "Vinp"
pin_name_n = "Vinn"
for element in circuit.elements:
    if element.name.lower().startswith("x"):
        opamp_element = element
        pin_name = str(opamp_element.pins[0].node)
        pin_name_n = str(opamp_element.pins[1].node)
        break


# print("pin_name", pin_name)
# print("pin_name_n", pin_name_n)

params = {pin_name: 2.51, pin_name_n: 2.5}

simulator = circuit.simulator()
simulator.initial_condition(**params)

try:
    analysis = simulator.transient(step_time=1@u_us, end_time=10@u_ms)
except:
    print("analysis failed.")
    sys.exit(2)

import numpy as np
# Get the output node voltage
vout = np.array(analysis['Vout'])
vinp = np.array(analysis[pin_name])
vinn = np.array(analysis[pin_name_n])
time = np.array(analysis.time)

from scipy.signal import find_peaks, firwin, lfilter

numtaps = 51
cutoff_hz = 10.0
sample_rate = 1000
fir_coeff = firwin(numtaps, cutoff_hz, fs=sample_rate, window="hamming")

filtered_vout = lfilter(fir_coeff, 1.0, vout)
peaks, _ = find_peaks(filtered_vout)


error = 0
import sys

# Plot the results
import matplotlib.pyplot as plt

plt.figure()
plt.plot(time, vout)
# plt.plot(time, filtered_vout)
plt.plot(time, vinp)
plt.plot(time, vinn)
plt.title('Wien Bridge Oscillator Output')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.legend(['Vout', 'Vinp', 'Vinn'])
plt.grid()
plt.savefig('[FIGURE_PATH].png')

# sys.exit(0)

troughs, _ = find_peaks(-filtered_vout)
if len(peaks) > 0 and len(troughs) > 0:
    amplitudes = []

    for peak in peaks:
        trough_index = np.argmin(np.abs(troughs - peak))
        trough = troughs[trough_index]
        amplitude = np.abs(vout[peak] - vout[trough])
        amplitudes.append(amplitude)

    amplitudes = np.array(amplitudes)

    min_amplitude_threshold = 1e-6

else:
    print("Not enough peaks were detected to determine amplitude.")
    sys.exit(2)

# print("Amplitudes: ", amplitudes)
amplitudes = np.sort(amplitudes)
num_elements_to_keep = len(amplitudes) // 2
amplitudes = amplitudes[-num_elements_to_keep:]


if not all(amplitudes > min_amplitude_threshold):
    print("The peak amplitudes are too small. (<1uV)")
    error = 1


if len(peaks) > 3:
    peak_times = time[peaks]
    periods = np.diff(peak_times)
    average_period = np.mean(periods)
    some_small_threshold = 0.2 * average_period
    period_variation = np.std(periods)
    if period_variation < some_small_threshold:
        if error == 0:
            print("The oscillator works correct and produces periodic oscillations.")
            print("The average period is: {} s".format(np.mean(periods)))
    else:
        print("Periodicity is inconsistent, oscillation may not be an ideal periodicity.")
        error = 1
else:
    print("Not enough peaks were detected to determine periodicity.")
    error = 1



if error == 1:
    sys.exit(2)
else:
    sys.exit(0)