in_frequency = 10e6
period = 1/in_frequency
circuit.PulseVoltageSource('1', 'clk_ref', circuit.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                        pulse_width=(0.48*period)@u_s, period=(period)@u_s, delay_time=30@u_ns, rise_time=(0.02*period)@u_s, fall_time=(0.02*period)@u_s)
simulator = circuit.simulator()

simulator.initial_condition(vctrl=0.5@u_V,
                            clk_p=0.5@u_V, clk_n=0.5@u_V,
                            clk_p_45=0.5@u_V, clk_n_45=0.5@u_V,
                            clk_p_90=0.5@u_V, clk_n_90=0.5@u_V,
                            clk_p_135=0.5@u_V, clk_n_135=0.5@u_V)
analysis = simulator.transient(step_time=10@u_ns, end_time=10@u_us)


### Find frequency
import numpy as np
time = np.array(analysis.time)  # Time points array
vout = np.array(analysis['clk_p'])  # Output voltage array
# Find zero-crossings
zero_crossings = np.where(np.diff(np.sign(vout-0.5))[:])[0][-5:]
# Calculate periods by subtracting consecutive zero-crossing times
periods = np.diff(time[zero_crossings])
# Average period
average_period = 2 * np.mean(periods)
# Frequency is the inverse of the period
out_frequency = 1 / average_period
print()
print(f"REF Frequency : {in_frequency*1e-6} MHz")
print(f"OUT Frequency : {out_frequency*1e-6} MHz")
print()



if np.close(in_frequency, out_frequency, rtol=0.05):
    print("The Phase-Locked Loop functions correctly.\n")
else:
    print("The Phase-Locked Loop does not function correctly.\n")
    print("When the clk_ref frequency is 10 MHz, the output frequency should be 10 MHz.\n")
    sys.exit(0)

fig = plt.figure(figsize=(14, 9))

# plt.ylim((-0.2, 1.2))

plt.subplot(321)
plt.xlim((0, 1e-6))
plt.plot(list(analysis.time), list(analysis["clk_ref"]))
plt.plot(list(analysis.time), list(analysis["clk_p"]))
plt.title('init clk')

plt.subplot(323)
plt.xlim((0, 1e-6))
plt.plot(list(analysis.time), list(analysis["UP"]))
plt.plot(list(analysis.time), list(analysis["DN"]))
plt.title('init UP/DN')

plt.subplot(325)
plt.plot(list(analysis.time), list(analysis["vctrl"]))
plt.title('overall vctrl')

plt.subplot(322)
plt.xlim((9e-6, 10e-6))
plt.plot(list(analysis.time), list(analysis["clk_ref"]))
plt.plot(list(analysis.time), list(analysis["clk_p"]))
plt.title('converged clk')

plt.subplot(324)
plt.xlim((9e-6, 10e-6))
plt.plot(list(analysis.time), list(analysis["UP"]))
plt.plot(list(analysis.time), list(analysis["DN"]))
plt.title('converged UP/DN')

plt.subplot(326)
plt.xlim((9e-6, 10e-6))
plt.plot(list(analysis.time), list(analysis["vctrl"]))
plt.title('converged vctrl')

plt.show()

fig.savefig("./outputs/pll.png")
plt.close(fig)
######################

sys.exit(0)