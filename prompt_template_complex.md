You aim to design a topology for a given circuit described in the text. 
Please ensure your designed circuit topology works properly and achieves the design requirements. 
To make the task easier, I provide you with some existing subcircuits you can directly use by calling functions in Python with the PySpice library.
Now I would like you to help me design a complex analog circuit based on them.



Here is an example:

## Question 
Design an opamp with 470 ohm resistance load.

Input node name: in

Output node name: out

You can directly use the following subcircuits.

### Subcircuits Info

Id	Circuit Type	Gain/Differential-mode gain (dB)	Common-mode gain (dB)	Input	Output
-	Opamp	20	-10	Vin	Vout


### Call Info

To use them, please insert the following codes.

```python
from example_lib import *
# declare the subcircuit
circuit.subcircuit(‘BasicOperationalAmplifier())
# create a subcircuit instance
circuit.X('1', 'BasicOperationalAmplifier', 'Vin', 'Vout')
```


## Answer


```python

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from example_lib import *

circuit = Circuit('Operational Amplifier')

# Define the MOSFET models
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=50e-6, vto=-0.5)


circuit.V('input', 'in', circuit.gnd, 2.5@u_V)
circuit.subcircuit(BasicOperationalAmplifier())
circuit.X('op', 'BasicOperationalAmplifier', 'in', circuit.gnd, 'out')
R = 470
circuit.R('load', 'out', circuit.gnd, R)

simulator = circuit.simulator()
```

As you have seen, the output of your designed topology should be in a complete Python code, describing the topology of integrated analog circuits according to the design plan. 

Please make sure your Python code is compatible with PySpice. 
Please give the runnable code without any placeholders.
Do not write other redundant codes after ```simulator = circuit.simulator()```.

There are some tips you should remember all the time:
1. For the MOSFET definition circuit.MOSFET(name, drain, gate, source, bulk, model, w=w1,l=l1), be careful about the parameter sequence. 
2. You should connect the bulk of a MOSFET to its source.
3. Please use the MOSFET threshold voltage, when setting the bias voltage.
4. Avoid giving any AC voltage in the sources, just consider the operating points.
5. Make sure the input and output node names appear in the circuit.
6. Assume the Vdd = 5.0 V. Do not need to add the power supply for subcircuits.

## Question

Design [TASK]. 

Input node name: [INPUT].

Output node name: [OUTPUT].

You can directly use the following subcircuits.

### Subcircuits Info


[SUBCIRCUITS_INFO]

#### Note

[NOTE_INFO]

### Call Info

To use them, please insert the following codes.

[CALL_INFO]


## Answer
