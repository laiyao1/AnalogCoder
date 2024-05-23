vin_name = ""
for element in circuit.elements:
    if "vin" in [str(pin.node).lower() for pin in element.pins] and element.name.lower().startswith("v"):
        vin_name = element.name


bias_voltage = [BIAS_VOLTAGE]

if vin_name != "":
    circuit.element(vin_name).detach()
    circuit.V('pulse', 'Vin', circuit.gnd, f"dc {bias_voltage} PULSE({bias_voltage-0.5} {bias_voltage+0.5} 1u 1u 1u 10m 20m)")
else:
    circuit.V('in', 'Vin', circuit.gnd, f"dc {bias_voltage} PULSE({bias_voltage-0.5} {bias_voltage+0.5} 1u 1u 1u 10m 20m)")

for element in circuit.elements:
    if element.name.lower().startswith("r1") or element.name.lower().startswith("rr1"):
        r_name = element.name
circuit.element(r_name).resistance = "10k"

for element in circuit.elements:
    # print("element.name", element.name)
    if element.name.lower().startswith("cf") or element.name.lower().startswith("ccf") or element.name.lower().startswith("c1"):
        c_name = element.name
circuit.element(c_name).capacitance = "3u"

simulator = circuit.simulator()

try:
    analysis = simulator.transient(step_time=1@u_us, end_time=200@u_ms)
except:
    print("analysis failed.")
    sys.exit(2)


import numpy as np
import matplotlib.pyplot as plt
# Plot the step response
time = np.array(analysis.time)
vin = np.array(analysis['vin'])
vout = np.array(analysis['vout'])


plt.figure()
plt.plot(time, vout)
plt.title('Step Response of Op-amp Integrator')
plt.xlabel('Time [s]')
plt.ylabel('Output Voltage [V]')
plt.grid(True)
plt.savefig("[FIGURE_PATH]")


expected_slope = 0.5 / 0.03


from scipy.signal import find_peaks

peaks, _ = find_peaks(vout)

troughs, _ = find_peaks(-vout)

if len(peaks) < 2 or len(troughs) < 2:
    print("No peaks or troughs found in output voltage. Please check the netlist.")
    sys.exit(2)


start = peaks[-2]
end = troughs[troughs > start][0] 

slope, intercept = np.polyfit(time[start:end], vout[start:end], 1)
slope = np.abs(slope)
from scipy.stats import linregress
_, _, r_value, p_value, std_err = linregress(time[start:end], vout[start:end])



import sys
if not np.isclose(slope, expected_slope, rtol=0.3):  # 30% tolerance
    print(f"The circuit does not function correctly as an integrator.\n"
          f"Expected slope: {expected_slope} V/s | Actual slope: {slope} V/s\n")
    sys.exit(2)

if not r_value** 2 >= 0.9:
    print("The op-amp integrator does not have a linear response.\n")
    sys.exit(2)


for element in circuit.elements:
    if element.name.lower().startswith("x"):
        x_name = element.name

circuit.element(x_name).detach()
simulator = circuit.simulator()
try:
    analysis = simulator.transient(step_time=1@u_us, end_time=200@u_ms)
except:
    print("The op-amp integrator functions correctly.\n")
    sys.exit(0)

time = np.array(analysis.time)
vin = np.array(analysis['vin'])
vout = np.array(analysis['vout'])




expected_slope = 0.5 / 0.03


from scipy.signal import find_peaks

peaks, _ = find_peaks(vout)

troughs, _ = find_peaks(-vout)

if len(peaks) < 2 or len(troughs) < 2:
    print("The op-amp integrator functions correctly.\n")
    sys.exit(0)


start = peaks[-2]
end = troughs[troughs > start][0] 

slope, intercept = np.polyfit(time[start:end], vout[start:end], 1)
slope = np.abs(slope)
from scipy.stats import linregress
_, _, r_value, p_value, std_err = linregress(time[start:end], vout[start:end])


if np.isclose(slope, expected_slope, rtol=0.5):  # 50% tolerance
    print("The integrator maybe a passive integrator.\n")
    sys.exit(2)

print("The op-amp integrator functions correctly.\n")
sys.exit(0)

