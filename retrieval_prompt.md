I have the following implemented subcircuits you can directly call them by Python code with the Pyspice library, we list all basic information on them.

| Id | Type | Circuit | Gain (dB) | Common Mode Gain (dB) | # of inputs | # of outputs | Input Phase |
|---|---|---|---|---|---|---|---|
| 1 | Amplifier | a single-stage common-source amplifier with resistive load R | 17.03 | NA | 1 | 1 | inverting |
| 2 | Amplifier | A three-stage amplifier with single input and output (each stage is common-source with resistive load) | 44.13 | NA | 1 | 1 | inverting |
| 3 | Amplifier | A common-drain amplifier (a.k.a. a source follower) with resistive load R (output Vout at the source) | -1.15 | NA | 1 | 1 | non-inverting |
| 4 | Amplifier | A single-stage common-gate amplifier with resistive load R (input signal Vin must be applied at the source terminal) | 17.03 | NA | 1 | 1 | non-inverting |
| 5 | Amplifier | A single-stage cascode amplifier with two NMOS transistors provides a single-ended output through a resistive load R | 24.08 | NA | 1 | 1 | inverting |
| 6 | Inverter | A NMOS inverter with resistive load R | NA | NA | 1 | 1 | NA |
| 7 | Inverter | A logical inverter with 1 NMOS and 1 PMOS | NA | NA | 1 | 1 | NA |
| 8 | CurrentMirror | A simple NMOS constant current source with resistive load R | NA | NA | 1 | 1 | NA |
| 9 | Amplifier | A two-stage amplifier with a Miller compensation capacitor | 75.94 | NA | 1 | 1 | -90 degree |
| 10 | Amplifier | A single-stage amplifier (common-source with PMOS diode-connected load (gate and drain are shorted)) | 3.01 | NA | 1 | 1 | inverting |
| 11 | Opamp | A differential opamp with an active PMOS current mirror load, a tail current source, and two outputs | 200 | -40.13 | 2 | 2 | non-inverting, inverting |
| 12 | CurrentMirror | A cascode current mirror with 4 mosfets (2 stacked at input side with diode-connected, 2 stacked at output side), reference current source input Iref (connected to Vdd) and resistive load R | NA | NA | 1 | 1 | NA |
| 13 | Opamp | A single-stage differential common-source opamp with dual resistive loads, tail current, and a single output | 24.04 | 21.59 | 2 | 1 | non-inverting, inverting |
| 14 | Opamp | A two-stage differential opamp (first stage: common-source with an active load and a tail current, second stage: common-source with an active load) | 150.36 | -58.72 | 2 | 2 | non-inverting, inverting |
| 15 | Opamp | A single-stage telescopic cascode opamp with two outputs (4 nmos as cascode input pair, 4 pmos as cascode loads, and 1 tail current) | 41.62 | -135.67 | 2 | 2 | non-inverting, inverting |


Now, you need to design [TASK]. Please maximize the design success rate, thus the circuit with two inputs and the highest possible gain has greater flexibility. Please choose the subcircuits from the above table you will use and make the number of chosen subcircuits as few as possible.

Please give out the IDs of the subcircuits that you choose, and enumerate them in a Python list like ```[0]```.