simulator.initial_condition(vout_1=0.3@u_V, vout=0.6@u_V)

try:
    analysis = simulator.transient(step_time=1@u_ns, end_time=100@u_us)
except:
    print("Transient analysis failed.")
    sys.exit(2)


import numpy as np

fig = plt.figure()
plt.ylim((-2, 2))
plt.plot(list(analysis.time), list(analysis["vout"]))
fig.savefig("[FIGURE_PATH].png")


y = np.array(analysis["vout"])
# print("y", y)
t = np.array(analysis.time)
threshold = (y.max() + y.min())/2
# print("threshold", threshold)
# print(threshold)
crossings = []
for i in range(1, len(y)):
    if y[i-1] < threshold and y[i] >= threshold:
        slope = (y[i] - y[i-1]) / (t[i] - t[i-1])
        exact_time = t[i-1] + (threshold - y[i-1]) / slope
        crossings.append(exact_time)

# print("crossings", crossings)
# print("len(crossings)", len(crossings))
periods = np.diff(crossings)
average_period = np.median(periods)
# print("average_period", average_period)

circuit.element("Vin").detach()
circuit.V('in', 'vin', circuit.gnd, 0.65@u_V)

simulator = circuit.simulator()
simulator.initial_condition(vout_1=0.3@u_V, vout=0.7@u_V)
# print("simulator2 start")

try:
    analysis = simulator.transient(step_time=1@u_ns, end_time=100@u_us)
except:
    print("Transient analysis failed.")
    sys.exit(2)
# print("simulator2 end")

plt.plot(list(analysis.time), list(analysis["vout"]))

fig.savefig("./opamp_vco.png")

y = np.array(analysis["vout"])
# print("y", y)
t = np.array(analysis.time)
threshold = (y.max() + y.min())/2
# print("threshold", threshold)
# print(threshold)
crossings = []
for i in range(1, len(y)):
    if y[i-1] < threshold and y[i] >= threshold:
        slope = (y[i] - y[i-1]) / (t[i] - t[i-1])
        exact_time = t[i-1] + (threshold - y[i-1]) / slope
        crossings.append(exact_time)

# print("crossings", crossings)
# print("len(crossings)", len(crossings))
periods = np.diff(crossings)
average_period2 = np.median(periods)
# print("average_period2", average_period2)


circuit.element("Vin").detach()
circuit.V('in', 'vin', circuit.gnd, 0.8@u_V)

simulator = circuit.simulator()
simulator.initial_condition(vout_1=0.3@u_V, vout=0.7@u_V)
# print("simulator2 start")
analysis = simulator.transient(step_time=1@u_ns, end_time=100@u_us)
# print("simulator2 end")

plt.plot(list(analysis.time), list(analysis["vout"]))

# fig.savefig("./opamp_vco.png")

y = np.array(analysis["vout"])
# print("y", y)
t = np.array(analysis.time)
threshold = (y.max() + y.min())/2
# print("threshold", threshold)
# print(threshold)
crossings = []
for i in range(1, len(y)):
    if y[i-1] < threshold and y[i] >= threshold:
        slope = (y[i] - y[i-1]) / (t[i] - t[i-1])
        exact_time = t[i-1] + (threshold - y[i-1]) / slope
        crossings.append(exact_time)

# print("crossings", crossings)
# print("len(crossings)", len(crossings))
periods = np.diff(crossings)
average_period3 = np.median(periods)
# print("average_period3", average_period3)


if average_period - 1e-5 > average_period2 and average_period - 1e-5 > average_period3:
    print("The voltage-controlled oscillator functions correctly.")
    sys.exit(0)
elif average_period + 1e-5 < average_period2 and average_period + 1e-5 < average_period3:
    print("The voltage-controlled oscillator functions correctly.")
    sys.exit(0)
else:
    print("The voltage-controlled oscillator does not function correctly.")
    print("The average period is not changing as expected when adjusting the vin.")
    sys.exit(2)