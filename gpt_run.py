from openai import OpenAI
import openai
import argparse
import re
import os
import subprocess
import time
import pandas as pd
import sys
import shutil

import signal
import json

class TimeoutException(Exception):
    pass

def signal_handler(signum, frame):
    raise TimeoutException("timeout")

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default="gpt-3.5-turbo")
parser.add_argument('--temperature', type=float, default=0.5)
parser.add_argument('--num_per_task', type=int, default=15)
parser.add_argument('--num_of_retry', type=int, default=3)
parser.add_argument("--num_of_done", type=int, default=0)
parser.add_argument("--task_id", type=int, default=1)
parser.add_argument("--ngspice", action="store_true", default=False)
parser.add_argument("--no_prompt", action="store_true", default=False)
parser.add_argument("--skill", action="store_true", default=False)
parser.add_argument("--no_context", action="store_true", default=False)
parser.add_argument("--no_chain", action="store_true", default=False)
parser.add_argument('--api_key', type=str)

args = parser.parse_args()

opensource_models = ["mistral", "wizardcoder", "deepseek-coder:33b-instruct", "codeqwen", "mixtral", "qwen"]

if any([model in args.model for model in opensource_models]):
    import ollama
if args.skill:
    args.num_of_retry = min(2, args.num_of_retry)

complex_task_type = ['Oscillator', 'Integrator', 'Differentiator', 'Adder', 'Subtractor', 'Schmitt']
bias_usage = """Due to the operational range of the op-amp being 0 to 5V, please connect the nodes that were originally grounded to a 2.5V DC power source.
Please increase the gain as much as possible to maintain oscillation.
"""


dc_sweep_template = """
import numpy as np
analysis = simulator.dc(V[IN_NAME]=slice(0, 5, 0.01))
fopen = open("[DC_PATH]", "w")
out_voltage = np.array(analysis.Vout)
in_voltage = np.array(analysis.V[IN_NAME])
print("out_voltage: ", out_voltage)
print("in_voltage: ", in_voltage)
for item in in_voltage:
    fopen.write(f"{item:.4f} ")
fopen.write("\\n")
for item in out_voltage:
    fopen.write(f"{item:.4f} ")
fopen.write("\\n")
fopen.close()
"""


pyspice_template = """
try:
    analysis = simulator.operating_point()
    fopen = open("[OP_PATH]", "w")
    for node in analysis.nodes.values(): 
        fopen.write(f"{str(node)}\\t{float(analysis[str(node)][0]):.6f}\\n")
    fopen.close()
except Exception as e:
    print("Analysis failed due to an error:")
    print(str(e))
"""


output_netlist_template = """
source = str(circuit)
print(source)
"""

import_template = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
"""


sin_voltage_source_template = """
circuit.SinusoidalVoltageSource('sin', 'Vin', circuit.gnd, 
    ac_magnitude=1@u_nV, dc_offset={0}, amplitude=1@u_nV, offset={0})
"""


global client


if "gpt" in args.model:
    client = OpenAI(api_key=args.api_key)
elif "deepseek-chat" in args.model:
    client = OpenAI(api_key=args.api_key, base_url="https://api.deepseek.com/v1")
else:
    client = None


# This function extracts the code from the generated content which in markdown format
def extract_code(generated_content):
    empty_code_error = 0
    assert generated_content != "", "generated_content is empty"
    regex = r".*?```.*?\n(.*?)```"
    matches = re.finditer(regex, generated_content, re.DOTALL)
    first_match = next(matches, None)
    try:
        code = first_match.group(1)
        print("code", code)
        code = "\n".join([line for line in code.split("\n") if len(line.strip()) > 0])
    except:
        code = ""
        empty_code_error = 1
        return empty_code_error, code
    # Add necessary libraries
    if not args.ngspice:
        if "from PySpice.Spice.Netlist import Circuit" not in code:
            code = "from PySpice.Spice.Netlist import Circuit\n" + code
        if "from PySpice.Unit import *" not in code:
            code = "from PySpice.Unit import *\n" + code
    new_code = ""
    for line in code.split("\n"):
        new_code += line + "\n"
        if "circuit.simulator()" in line:
            break

    return empty_code_error, new_code



def run_code(file):
    print("IN RUN_CODE : {}".format(file))
    simulation_error = 0
    execution_error = 0
    execution_error_info = ""
    floating_node = ""
    try:
        print("-----------------running code-----------------")
        print("file:", file)
        result = subprocess.run(["python", "-u", file], check=True, text=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        print("num of lines", len(result.stdout.split("\n")))
        print("num of error lines", len(result.stderr.split("\n")))
        if len(result.stdout.split("\n")) >= 2 and ("failed" in result.stdout.split("\n")[-2] or "failed" in result.stdout.split("\n")[-1]):
            if len(result.stdout.split("\n")) >= 2:
                if "check node" in result.stdout.split("\n")[1]:
                    simulation_error = 1
                    floating_node = result.stdout.split("\n")[1].split()[-1]
                else:
                    execution_error = 1
                    if "ERROR" in result.stdout.split("\n")[1]:
                        execution_error_info = "ERROR" + result.stdout.split("\n")[1].split("ERROR")[-1]
                    elif "Error" in result.stdout.split("\n")[1]:
                        execution_error_info = "Error" + result.stdout.split("\n")[1].split("Error")[-1]
                    if len(result.stdout.split("\n"))>=3 and "ERROR" in result.stdout.split("\n")[2]:
                        execution_error_info += "\nERROR" + result.stdout.split("\n")[2].split("ERROR")[-1]
                    elif len(result.stdout.split("\n"))>=3 and "Error" in result.stdout.split("\n")[2]:
                        execution_error_info += "\nError" + result.stdout.split("\n")[2].split("Error")[-1]
                    if len(result.stdout.split("\n"))>=4 and "ERROR" in result.stdout.split("\n")[3]:
                        execution_error_info += "\nERROR" + result.stdout.split("\n")[3].split("ERROR")[-1]
                    elif len(result.stdout.split("\n"))>=4 and "Error" in result.stdout.split("\n")[3]:
                        execution_error_info += "\nError" + result.stdout.split("\n")[3].split("Error")[-1]
            if len(result.stderr.split("\n")) >= 2:
                if "check node" in result.stderr.split("\n")[1]:
                    simulation_error = 1
                    floating_node = result.stderr.split("\n")[1].split()[-1]
                else:
                    execution_error = 1
                    if "ERROR" in result.stderr.split("\n")[1]:
                        execution_error_info = "ERROR" + result.stderr.split("\n")[1].split("ERROR")[-1]
                    elif "Error" in result.stderr.split("\n")[1]:
                        execution_error_info = "Error" + result.stderr.split("\n")[1].split("Error")[-1]
                    if len(result.stdout.split("\n"))>=3 and "ERROR" in result.stderr.split("\n")[2]:
                        execution_error_info += "\nERROR" + result.stderr.split("\n")[2].split("ERROR")[-1]
                    elif len(result.stdout.split("\n"))>=3 and "Error" in result.stdout.split("\n")[2]:
                        execution_error_info += "\nError" + result.stdout.split("\n")[2].split("Error")[-1]
                    if len(result.stdout.split("\n"))>=4 and "ERROR" in result.stderr.split("\n")[3]:
                        execution_error_info += "\nERROR" + result.stderr.split("\n")[3].split("ERROR")[-1]
                    elif len(result.stdout.split("\n"))>=4 and "Error" in result.stderr.split("\n")[3]:
                        execution_error_info += "\nError" + result.stderr.split("\n")[3].split("Error")[-1]
            if simulation_error == 1:
                execution_error = 0
            if execution_error_info == "" and execution_error == 1:
                execution_error_info = "Simulation failed."
        code_content = open(file, "r").read()
        if "circuit.X" in code_content:
            execution_error_info += "\nPlease avoid using the subcircuit (X) in the code."
        if "error" in result.stdout.lower() and not "<<NAN, error".lower() in result.stdout.lower() and simulation_error == 0:
            execution_error = 1
            execution_error_info = result.stdout + result.stderr
        return execution_error, simulation_error, execution_error_info, floating_node
    except subprocess.CalledProcessError as e:
        print(f"error when running: {e}")
        print("stderr", e.stderr, file=sys.stderr)
        if "failed" in e.stdout:
            if len(e.stderr.split("\n")) >= 2:
                if "check node" in e.stderr.split("\n")[1]:
                    simulation_error = 1
                    floating_node = e.stderr.split("\n")[1].split()[-1]
        execution_error = 1
        
        execution_error_info = e.stdout + e.stderr
        if simulation_error == 1:
            execution_error = 0
            execution_error_info = "Simulation failed."
        return execution_error, simulation_error, execution_error_info, floating_node
    except subprocess.TimeoutExpired:
        print(f"Time out error when running code.")
        execution_error = 1
        execution_error_info = "Time out error when running code.\n"
        execution_error_info = "Suggestion: Avoid letting users input in Python code.\n"
        return execution_error, simulation_error, execution_error_info, floating_node




def check_netlist(netlist_path, operating_point_path, input, output, task_id, task_type):
    warning = 0
    warning_message = ""
    # Check all the input and output nodes are in the netlist
    if not os.path.exists(operating_point_path):
        return 0, ""
    fopen_op = open(operating_point_path, 'r').read()
    for input_node in input.split(", "):
        if input_node.lower() not in fopen_op.lower():
            warning_message += "The given input node ({}) is not found in the netlist.\n".format(input_node)
            warning = 1
    for output_node in output.split(", "):
        if output_node.lower() not in fopen_op.lower():
            warning_message += "The given output node ({}) is not found in the netlist.\n".format(output_node)
            warning = 1

    if warning == 1:
        warning_message += "Suggestion: You can replace the nodes actually used for input/output with the given names. Please rewrite the corrected complete code.\n"

    if task_type == "Inverter":
        return warning, warning_message
    vdd_voltage = 5.0
    vinn_voltage = 1.0
    vinp_voltage = 1.0
    for line in fopen_op.split("\n"):
        line = line.lower()
        if line.startswith("vdd"):
            vdd_voltage = float(line.split("\t")[-1])
        if line.startswith("vinn"):
            vinn_voltage = float(line.split("\t")[-1])
        if line.startswith("vinp"):
            vinp_voltage = float(line.split("\t")[-1])
    
    if vinn_voltage != vinp_voltage:
        warning_message += "The given input voltages of Vinn and Vinp are not equal.\n"
        warning = 1
        warning_message += "Suggestion: Please make sure the input voltages are equal.\n"
    
    fopen_netlist = open(netlist_path, 'r')
    voltages = {}
    for line in fopen_op.split("\n"):
        if line.strip() == "":
            continue
        node, voltage = line.split()
        voltages[node] = float(voltage)
    voltages["0"] = 0
    voltages["gnd"] = 0

    vthn = 0.5
    vthp = 0.5
    miller_node_1 = None
    miller_node_2 = None
    resistance_exist = 0
    has_diodeload = 0
    first_stage_out = None
    for line in fopen_netlist.readlines():
        if line.startswith('.'):
            continue
        if line.startswith("C"):
            if task_id == 9:
                miller_node_1 = line.split()[1].lower()
                miller_node_2 = line.split()[2].lower()
        if line.startswith("R"):
            resistance_exist = 1
        if line.startswith("M"):
            name, drain, gate, source, bulk, model = line.split()[:6]
            name = name[1:]
            drain = drain.lower()
            source = source.lower()
            bulk = bulk.lower()
            gate = gate.lower()
            mos_type = "NMOS" if "nmos" in model.lower() else "PMOS"
            ## Common-gate
            if task_id == 4:
                if drain == "vin" or gate == "vin":
                    warning_message += (f"For a common-gate amplifier, the vin should be connected to source.\n")
                    warning_message += (f"Suggestion: Please connect the vin to the source node.\n")
                    warning = 1
            elif task_id == 3:
                if drain == "vout" or gate == "vout":
                    warning_message += (f"For a common-drain amplifier, the vout should be connected to source.\n")
                    warning_message += (f"Suggestion: Please connect the vout to the source node.\n")
                    warning = 1
            elif task_id == 10:
                if gate == drain:
                    has_diodeload = 1
                    
            elif task_id == 9:
                if gate == "vin":
                    first_stage_out = drain
            
            if mos_type == "NMOS":
                # VDS
                vds_error = 0
                if voltages[drain] == 0.0:
                    if drain.lower() == "0" or drain.lower() == "gnd":
                        warning_message += (f"Suggetions: Please avoid connect {mos_type} {name} drain to the ground.\n")
                    else:
                        vds_error = 1
                        warning_message += (f"For {mos_type} {name}, the drain node ({drain}) voltage is 0.\n")
                # VDS
                elif voltages[drain] < voltages[source]:
                    vds_error = 1
                    warning_message += (f"For {mos_type} {name}, the drain node ({drain}) voltage is lower than the source node ({source}) voltage.\n")
                if vds_error == 1:
                    warning_message += (f"Suggestion: Please set {mos_type} {name} with an activated state and make sure V_DS > V_GS - V_TH.\n")
                # VGS
                vgs_error = 0
                if voltages[gate] == voltages[source]:
                    # vgs_error = 1
                    if gate == source:
                        warning_message += (f"For {mos_type} {name}, the gate node ({gate}) is connected to the source node ({source}).\n")
                        warning_message += (f"Suggestion: Please {mos_type} {name}, please divide its gate ({gate}) and source ({source}) connection.\n")
                    else:
                        vgs_error = 1
                        warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is equal to the source node ({source}) voltage.\n")
                elif voltages[gate] < voltages[source]:
                    vgs_error = 1
                    warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is lower than the source node ({source}) voltage.\n")
                elif voltages[gate] <= voltages[source] + vthn:
                    vgs_error = 1
                    warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is lower than the source node ({source}) voltage plus the threshold voltage.\n")
                if vgs_error == 1:
                    warning_message += (f"Suggestion: Please set {mos_type} {name} with an activated state by increasing the gate voltage or decreasing the source voltage and make sure V_GS > V_TH.\n")
            if mos_type == "PMOS":
                # VDS
                vds_error = 0
                if voltages[drain] == vdd_voltage:
                    if drain.lower() == "vdd":
                        warning_message += (f"Suggestion: Please avoid connect {mos_type} {name} drain to the vdd.\n")
                    else:
                        vds_error = 1
                        warning_message += (f"For {mos_type} {name}, the drain node ({drain}) voltage is V_dd.\n")
                # VDS
                elif voltages[drain] > voltages[source]:
                    vds_error = 1
                    warning_message += (f"For {mos_type} {name}, the drain node ({drain}) voltage is higher than the source node ({source}) voltage.\n")
                if vds_error == 1:
                    warning_message += (f"Suggestion: Please set {mos_type} {name} with an activated state and make sure V_DS < V_GS - V_TH.\n")
                # VGS
                vgs_error = 0
                if voltages[gate] == voltages[source]:
                    if gate == source:
                        warning_message += (f"For {mos_type} {name}, the gate node ({gate}) is connected to the source node ({source}).\n")
                        warning_message += f"Suggestion: Please {mos_type} {name}, please divide its gate ({gate}) and source ({source}) connection.\n"
                    else:
                        vgs_error = 1
                        warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is equal to the source node ({source}) voltage.\n")
                elif voltages[gate] > voltages[source]:
                    vgs_error = 1
                    warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is higher than the source node ({source}) voltage.\n")
                elif voltages[gate] >= voltages[source] - vthp:
                    vgs_error = 1
                    warning_message += (f"For {mos_type} {name}, the gate node ({gate}) voltage is higher than the source node ({source}) voltage plus the threshold voltage.\n")
                if vgs_error == 1:
                    warning_message += (f"Suggestion: Please set {mos_type} {name} with an activated state by decreasing the gate voltage or incresing the source voltage and make sure V_GS < V_TH.\n")

    if task_id in [1, 2, 3, 4, 5, 6, 8, 13]:
        if resistance_exist == 0:
            warning_message += "There is no resistance in the netlist.\n"
            warning_message += "Suggestion: Please add a resistance load in the netlist.\n"
            warning = 1
    if task_id == 9:
        if first_stage_out == None:
            warning_message += "There is no first stage output in the netlist.\n"
            warning_message += "Suggestion: Please add a first stage output in the netlist.\n"
            warning = 1
        elif (first_stage_out == miller_node_1 and miller_node_2 == "vout") or (first_stage_out == miller_node_2 and miller_node_1 == "vout"):
            pass
        elif miller_node_1 == None:
            warning_message += "There no Miller capacitor in the netlist.\n"
            warning_message += "Suggestion: Please correctly connect the Miller compensation capacitor."
            warning = 1
        else:
            warning_message += "The Miller compensation capacitor is not correctly connected.\n"
            warning_message += "Suggestion: Please correctly connect the Miller compensation capacitor."
            warning = 1
    if task_id == 10 and has_diodeload == 0:
        warning_message += "There is no diode-connected load in the netlist.\n"
        warning_message += "Suggestion: Please add a diode-connected load in the netlist.\n"
        warning = 1
    warning_message = warning_message.strip()
    if warning_message == "":
        warning = 0
    else:
        warning = 1
        warning_message = "According to the operating point check, there are some issues, which defy the general operating principles of MOSFET devices. \n" + warning_message + "\n"
        warning_message += "\nPlease help me fix the issues and rewrite the corrected complete code.\n"
    return warning, warning_message

    
def check_function(task_id, code_path, task_type):
    fwrite_code_path = "{}_check.py".format(code_path.rsplit(".", 1)[0])
    fwrite_code = open(fwrite_code_path, 'w')
    if task_type == "CurrentMirror":
        test_code = open("problem_check/CurrentMirror.py", "r").read()
        code = open(code_path, 'r').read()
        code = code + "\n" + test_code
        fwrite_code.write(code)
        fwrite_code.close()
    elif task_type == "Amplifier" or task_type == "Opamp":
        voltage = "1.0"
        test_code = open(f"problem_check/{task_type}.py", "r").read()
        for line in open(code_path, 'r').readlines():
            if line.startswith("circuit.V") and "vin" in line.lower():
                
                parts = line.split("#")[0].strip().rstrip(")").split(",")
                raw_voltage = parts[-1].strip()
                if raw_voltage[0] == "\"" or raw_voltage[0] == "'":
                    raw_voltage = raw_voltage[1:-1]
                if "dc" in raw_voltage.lower():
                    voltage = raw_voltage.split(" ")[1]
                else:
                    voltage = raw_voltage
                new_voltage = " \"dc {} ac 1u\"".format(voltage)
                parts[-1] = new_voltage
                line = ",".join(parts) + ")\n"

            fwrite_code.write(line)
        fwrite_code.write("\n")
        fwrite_code.write(test_code)
        fwrite_code.close()
        print("voltage", voltage)
    elif task_type == "Inverter":
        test_code = open("problem_check/Inverter.py", "r").read()
        code = open(code_path, 'r').read()
        code = code + "\n" + test_code
        fwrite_code.write(code)
        fwrite_code.close()
    else:
        return 0, ""
    try:
        result = subprocess.run(["python", "-u", fwrite_code_path], check=True, text=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        print("function correct.")
        func_error = 0
        return_message = ""
    except subprocess.CalledProcessError as e:
        print("function error.")
        print("e.stdout", e.stdout)
        print("e.stderr", e.stderr)
        func_error = 1
        return_message = "\n".join(e.stdout.split("\n"))

    return func_error, return_message

import numpy as np
def get_best_voltage(dc_file_path):
    fopen = open(dc_file_path, 'r')
    vin = np.array([float(x) for x in fopen.readline().strip().split(" ")])
    vout = np.array([float(x) for x in fopen.readline().strip().split(" ")])
    if np.max(vout) - np.min(vout) < 1e-3:
        return 1, 0
    min_margin = 10.0
    for i, v in enumerate(vout):
        if np.abs(v - 2.5) < min_margin:
            min_margin = np.abs(v - 2.5)
            best_voltage = vin[i]
    return 0, best_voltage


def get_vin_name(netlist_content, task_type):
    vinn_name = "in"
    vinp_name = None
    for line in netlist_content.split("\n"):
        if not line.lower().startswith("v"):
            continue
        if len(line.lower().split()) < 2:
            continue
        if task_type == "Amplifier" and "vin" in line.lower().split()[1]:
            vinn_name = line.split()[0][1:]
        if task_type == "Opamp" and "vinp" in line.lower().split()[1]:
            vinp_name = line.split()[0][1:]
        if task_type == "Opamp" and "vinn" in line.lower().split()[1]:
            vinn_name = line.split()[0][1:]
    return vinn_name, vinp_name


def replace_voltage(raw_code, best_voltage, vinn_name, vinp_name):
    new_code = ""
    for line in raw_code.split("\n"):
        if not line.lower().startswith("circuit.v"):
            new_code += line + "\n"
            continue
        if vinn_name is not None and (line.lower().startswith(f"circuit.v('{vinn_name.lower()}'") or line.lower().startswith(f"circuit.v(\"{vinn_name.lower()}\"")):
            parts = line.split("#")[0].strip().rstrip(")").split(",")
            new_voltage = " {}".format(best_voltage)
            parts[-1] = new_voltage
            line = ",".join(parts) + ")"
        elif vinp_name is not None and (line.lower().startswith(f"circuit.v('{vinp_name.lower()}'") or line.lower().startswith(f"circuit.v(\"{vinp_name.lower()}\"")):
            parts = line.split("#")[0].strip().rstrip(")").split(",")
            new_voltage = " {}".format(best_voltage)
            parts[-1] = new_voltage
            line = ",".join(parts) + ")"
        new_code += line + "\n"
    return new_code


def connect_vinn_vinp(dc_sweep_code, vinn_name, vinp_name):
    new_code = ""
    for line in dc_sweep_code.split("\n"):
        if not line.lower().startswith("circuit.v"):
            new_code += line + "\n"
            continue
        if vinp_name is not None and (line.lower().startswith(f"circuit.v('{vinp_name.lower()}'") or line.lower().startswith(f"circuit.v(\"{vinp_name.lower()}\"")):
            new_line = "circuit.V('dc', 'Vinn', 'Vinp', 0.0)\n"
            new_code += new_line
        else:
            new_code += line + "\n"
    return new_code

def get_subcircuits_info(subcircuits, 
                    lib_data_path = "lib_info.tsv", task_data_path = "problem_set.tsv"):
    lib_df = pd.read_csv(lib_data_path, delimiter='\t')
    task_df = pd.read_csv(task_data_path, delimiter='\t')
    # New data frame
    columns = ["Id", "Circuit Type", "Gain/Differential-mode gain (dB)", "Common-mode gain (dB)", "Input", "Output"]
    subcircuits_df = pd.DataFrame(columns=columns)
    # write all the subcircuits information
    for sub_id in subcircuits:
        print("sub_id", sub_id)
        lib_df_row = lib_df.loc[lib_df['Id'] == sub_id]
        task_df_row = task_df.loc[task_df['Id'] == sub_id]
        print("task_df_row", task_df_row)
        sub_type = task_df.loc[task_df['Id'] == sub_id, 'Type'].item()
        sub_gain = float(lib_df.loc[lib_df['Id'] == sub_id, 'Av (dB)'].item())
        sub_com_gan = float(lib_df.loc[lib_df['Id'] == sub_id, 'Com Av (dB)'].item())
        sub_gain = "{:.2f}".format(sub_gain)
        sub_com_gan = "{:.2f}".format(sub_com_gan)
        print("sub_gain", sub_gain)
        print("sub_com_gan", sub_com_gan)
        print("sub_id", sub_id)
        print("sub_type", sub_type)
        sub_input = task_df.loc[task_df['Id'] == sub_id, 'Input'].item()
        input_node_list = sub_input.split(", ")
        input_node_list = [node for node in input_node_list if "bias" not in node]
        sub_input = ", ".join(input_node_list)

        sub_output = task_df.loc[task_df['Id'] == sub_id, 'Output'].item()
        output_node_list = sub_output.split(", ")
        output_node_list = [node for node in output_node_list if "outn" not in node and "outp" not in node]
        sub_output = ",".join(output_node_list)
        
        new_row = {'Id': sub_id, "Circuit Type": sub_type, "Gain/Differential-mode gain (dB)": sub_gain, "Common-mode gain (dB)": sub_com_gan, "Input": sub_input, "Output": sub_output}
        subcircuits_df = pd.concat([subcircuits_df, pd.DataFrame([new_row])], ignore_index=True)
    print("subcircuits_df")
    print(subcircuits_df)
    subcircuits_info = subcircuits_df.to_csv(sep='\t', index=False)
    return subcircuits_info


def get_note_info(subcircuits,
                    lib_data_path = "lib_info.tsv", task_data_path = "problem_set.tsv"):
    lib_df = pd.read_csv(lib_data_path, delimiter='\t')
    task_df = pd.read_csv(task_data_path, delimiter='\t')
    note_info = ""

    for sub_id in subcircuits:
        sub_type = task_df.loc[task_df['Id'] == sub_id, 'Type'].item()
        sub_name = task_df.loc[task_df['Id'] == sub_id, 'Submodule Name'].item()
        sub_bias_voltage = lib_df.loc[lib_df['Id'] == sub_id, 'Voltage Bias'].item()
        if "Amplifier" not in sub_type and "Opamp" not in sub_type:
            continue
        sub_phase = lib_df.loc[lib_df['Id'] == sub_id, 'Vin(n) Phase'].item()
        if sub_type == "Amplifier":
            if sub_phase == "inverting":
                other_sub_phase = "non-inverting"
            else:
                other_sub_phase = "inverting"
            note_info += f"The Vin of {sub_name} is the {sub_phase} input.\n"
            note_info += f"There is NO in {other_sub_phase} input in {sub_name}.\n"
            note_info += f"The DC operating voltage for Vin is {sub_bias_voltage} V.\n"
        elif sub_type == "Opamp":
            if sub_phase == "inverting":
                other_sub_phase = "non-inverting"
            else:
                other_sub_phase = "inverting"
            note_info += f"The Vinn of {sub_name} is the {sub_phase} input.\n"
            note_info += f"The Vinp of {sub_name} is the {other_sub_phase} input.\n"
            note_info += f"The DC operating voltage for Vinn/Vinp is {sub_bias_voltage} V.\n"
    print("note_info", note_info)
    return note_info, sub_bias_voltage


def get_call_info(subcircuits,
                    lib_data_path = "lib_info.tsv", task_data_path = "problem_set.tsv"):
    template = '''```python
from p[ID]_lib import *
# declare the subcircuit
circuit.subcircuit([SUBMODULE_NAME]())
# create a subcircuit instance
circuit.X('1', '[SUBMODULE_NAME]', [INPUT_OUTPUT])
```
'''
    lib_df = pd.read_csv(lib_data_path, delimiter='\t')
    task_df = pd.read_csv(task_data_path, delimiter='\t')
    call_info = ""
    for it, subcircuit in enumerate(subcircuits):
        sub_id = subcircuit
        sub_name = task_df.loc[task_df['Id'] == sub_id, 'Submodule Name'].item()
        input_nodes = task_df.loc[task_df['Id'] == sub_id, 'Input'].item()
        output_nodes = task_df.loc[task_df['Id'] == sub_id, 'Output'].item()
        sub_info = template.replace('[SUBMODULE_NAME]', sub_name)
        input_node_list = input_nodes.split(", ")
        input_node_list = [node for node in input_node_list if "bias" not in node]

        # for input_node in input_nodes.split(", "):
        input_info = ", ".join([f"'{input_node}'" for input_node in input_node_list])
        output_node_list = output_nodes.split(", ")
        output_node_list = [node for node in output_node_list if "outn" not in node and "outp" not in node]
        output_info = ", ".join([f"'{output_node}'" for output_node in output_node_list])
        if input_info !=  "" and output_info != "":
            input_output = f"{input_info}, {output_info}"
        elif input_info == "":
            input_output = f"{output_info}"
        else:
            input_output = f"{input_info}"
        sub_info = sub_info.replace('[INPUT_OUTPUT]', input_output)
        sub_info = sub_info.replace('[ID]', str(sub_id))
        call_info += sub_info
    return call_info

global generator
generator = None


def write_pyspice_code(sp_code_path, code_path, op_path):
    sp_code = open(sp_code_path, 'r')
    code = open(code_path, 'w')
    code.write(import_template)
    code.write("circuit = Circuit('circuit')\n")
    for line in sp_code.readlines():
        if line.startswith(".model"):
            parts = line.split()
            if len(parts) < 6:
                continue
            code.write(f"circuit.model('{parts[1]}', '{parts[2]}', {parts[3]}, {parts[4]}, {parts[5]})\n")
        elif line.startswith('R') or line.startswith('C') or line.startswith('V') or line.startswith('I'):
            type_name = line[0]
            parts = line.split()
            if len(parts) < 4:
                continue
            name = parts[0][1:]
            n1 = parts[1]
            n2 = parts[2]
            value = parts[3]
            code.write(f"circuit.{type_name}('{name}', '{n1}', '{n2}', '{value}')\n")
        elif line.startswith('M'):
            parts = line.split()
            if len(parts) < 8:
                continue
            name = parts[0][1:]
            drain = parts[1]
            gate = parts[2]
            source = parts[3]
            bulk = parts[4]
            model = parts[5]
            w = parts[6]
            l = parts[7]
            code.write(f"circuit.MOSFET('{name}', '{drain}', '{gate}', '{source}', '{bulk}', model='{model}', {w}, {l})\n")
    code.write("simulator = circuit.simulator()\n")
    code.write(pyspice_template.replace("[OP_PATH]", op_path))
    code.close()


def start_tmux_session(session_name, command):
    subprocess.run(['tmux', 'new-session', '-d', '-s', session_name])
    subprocess.run(['tmux', 'send-keys', '-t', session_name, command, 'C-m'])
    print(f"tmux session '{session_name}' started, running command: {command}")


def kill_tmux_session(session_name):
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True)
        print(f"tmux session '{session_name}' has been killed successfully.")
    except subprocess.CalledProcessError:
        print(f"Failed to kill tmux session '{session_name}'. Session might not exist.")


def work(task, input, output, task_id, it, background, task_type, flog, 
            money_quota = 100, subcircuits = None):

    global generator

    total_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    if task_type not in complex_task_type or args.skill == False:
        if "llama" in args.model:
            fopen = open('prompt_template.md','r')
        elif args.ngspice:
            fopen = open('prompt_template_ngspice.md','r')
        elif any(model in args.model for model in opensource_models):
            fopen = open('prompt_template.md','r')
        else:
            fopen = open('prompt_template.md','r')
        
        if args.no_prompt:
            fopen = open('prompt_template_wo_prompt.md', 'r')
        elif args.no_context:
            fopen = open('prompt_template_wo_context.md', 'r')
        elif args.no_chain:
            fopen = open('prompt_template_wo_chain_of_thought.md', 'r')
        prompt = fopen.read()

        prompt = prompt.replace('[TASK]', task)
        prompt = prompt.replace('[INPUT]', input)
        prompt = prompt.replace('[OUTPUT]', output)
        # Make the subcircuits by GPT possible
        if task_type in complex_task_type:
            prompt = prompt.replace('6. Avoid using subcircuits.', '').replace('7.', '6.').replace('8.', '7.')
            bias_voltage = 2.5

    else:
        fopen = open('prompt_template_complex.md','r')
        prompt = fopen.read()

        prompt = prompt.replace('[TASK]', task)
        prompt = prompt.replace('[INPUT]', input)
        prompt = prompt.replace('[OUTPUT]', output)
        subcircuits_info = get_subcircuits_info(subcircuits)
        note_info, bias_voltage = get_note_info(subcircuits)
        if task_type == "Oscillator":
            note_info += bias_usage
        call_info = get_call_info(subcircuits)
        prompt = prompt.replace('[SUBCIRCUITS_INFO]', subcircuits_info).replace('[NOTE_INFO]', note_info).replace('[CALL_INFO]', call_info)
        fwrite_prompt = open(f'prompt_template_complex_with_sub_{task_type}.md', 'w')
        fwrite_prompt.write(prompt)
        fwrite_prompt.close()

    # Background is not used now
    if background is not None:
        prompt += "\n\nHint Background: \n" + background + "\n## Answer \n"
    fopen.close()

    fopen_exe_error = open('execution_error.md', 'r')
    prompt_exe_error = fopen_exe_error.read()
    fopen_exe_error.close()

    fopen_sim_error = open('simulation_error.md', 'r')
    prompt_sim_error = fopen_sim_error.read()
    fopen_sim_error.close()

    messages = [
            {"role": "system", "content": "You are an analog integrated circuits expert."},
            {"role": "user", "content": prompt}
            ]
    retry = True

    if money_quota < 0:
        flog.write("Money quota is used up. Exceed quota: {}\n".format(money_quota))
        return money_quota

    while retry:
        if any(model in args.model for model in opensource_models):
            print(f"start {args.model} completion")
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(360)
            try:
                completion = ollama.chat(
                    model=args.model,
                    messages=messages,
                    options={
                        "temperature": args.temperature,
                        "top_p": 1.0,
                        # "num_predict": 16192,
                    })
                print(f"{args.model} completion finish")
                signal.alarm(0)
                break
            except TimeoutException as e:
                print(e)
                print("timeout")
                signal.alarm(0)
                print("restart ollama")
                kill_tmux_session("ollama")
                result = subprocess.run(['ollama', 'restart'], capture_output=True, text=True)
                start_tmux_session("ollama", "ollama serve")
                time.sleep(120)
        else:
            try:
                completion = client.chat.completions.create(
                    model = args.model,
                    messages = messages,
                    temperature = args.temperature
                )
                break
            except openai.APIStatusError as e:
                print("Encountered an APIStatusError. Details:")
                print(e)
                print("sleep 30 seconds")
                time.sleep(30)


    if "gpt" in args.model:
        total_tokens += completion.usage.total_tokens
        total_prompt_tokens += completion.usage.prompt_tokens
        total_completion_tokens += completion.usage.completion_tokens

    if "ft:gpt-3.5" in args.model:
        money_quota -= (completion.usage.prompt_tokens / 1e6 * 3) + (completion.usage.completion_tokens / 1e6 * 6)
    elif "gpt-3" in args.model:
        money_quota -= (completion.usage.prompt_tokens / 1e6 * 0.5) + (completion.usage.completion_tokens / 1e6 * 1.5)
    elif "gpt-4" in args.model:
        money_quota -= (completion.usage.prompt_tokens / 1e6 * 10) + (completion.usage.completion_tokens / 1e6 * 30)

    if "gpt" in args.model or "deepseek-chat" in args.model:
        answer = completion.choices[0].message.content
    else:
        answer = completion['message']['content']

    if "ft:gpt-3.5" in args.model:
        if "a:9HyyBpNI" in args.model:
            model_dir = "gpt3p5-ft-A"
        elif "b:9Hzb5l4S" in args.model:
            model_dir = "gpt3p5-ft-B"
        elif "c:9I0X557K" in args.model:
            model_dir = "gpt3p5-ft-C"
        else:
            assert False
    elif "gpt-3" in args.model:
        model_dir = 'gpt3p5'
    elif "gpt-4" in args.model:
        model_dir = 'gpt4'
    elif "deepseek-chat" in args.model:
        model_dir = "deepseek2"
    elif any(model in args.model for model in opensource_models):
        model_dir = str(args.model).replace(":", "-")
    else:
        model_dir = 'unknown'
    

    if "ft-A" in model_dir:
        assert task_id in [0, 3, 6, 9, 14, 10, 11]
    elif "ft-B" in model_dir:
        assert task_id in [1, 4, 7, 12, 10, 11]
    elif "ft-C" in model_dir:
        assert task_id in [2, 5, 8, 13, 10, 11]
    if args.ngspice:
        model_dir += '_ngspice'
    
    if args.no_prompt:
        model_dir += "_no_prompt"
    elif args.no_context:
        model_dir += "_no_context"
    elif args.no_chain:
        model_dir += "_no_chain"
    
    if args.num_of_retry > 3:
        model_dir += "_retry_{}".format(args.num_of_retry)
    
    if task_type in complex_task_type and not args.skill:
        model_dir += "_no_skill"
    
    if not os.path.exists(model_dir):
        try:
            os.mkdir(model_dir)
        except:
            pass
    if not os.path.exists('{}/p{}'.format(model_dir, task_id)):
        try:
            os.mkdir('{}/p{}'.format(model_dir, task_id))
        except:
            pass

    empty_code_error, raw_code = extract_code(answer)
    operating_point_path = "{}/p{}/{}/p{}_{}_{}_op.txt".format(model_dir, task_id, it, task_id, it, 0)
    if not args.ngspice and "simulator = circuit.simulator()" not in raw_code:
        raw_code += "\nsimulator = circuit.simulator()\n"
    if args.ngspice and ".end" in raw_code:
        raw_code = raw_code.replace(".end", "")

    code_id = 0
    if not args.ngspice:
        if task_type not in complex_task_type:
            code = raw_code + pyspice_template.replace("[OP_PATH]", operating_point_path)
        else:
            pyspice_template_complex = open(f"problem_check/{task_type}.py", "r").read()
            figure_path = "{}/p{}/{}/p{}_{}_{}_figure".format(model_dir, task_id, it, task_id, it, code_id)
            if task_type == "Oscillator":
                code = raw_code + pyspice_template_complex.replace("[FIGURE_PATH]", figure_path)
            else:
                if args.skill:
                    code = raw_code + pyspice_template_complex.replace("[FIGURE_PATH]", figure_path).replace('[BIAS_VOLTAGE]', str(bias_voltage))
                else:
                    code = raw_code + pyspice_template_complex.replace("[FIGURE_PATH]", figure_path).replace('[BIAS_VOLTAGE]', "float(circuit.element(vin_name).dc_value)")
            if "import math" not in code:
                code = "import math\n" + code
    else:
        code = raw_code

    fwrite_input = open('{}/p{}/p{}_{}_input.txt'.format(model_dir, task_id, task_id, it), 'w')
    fwrite_input.write(prompt)
    fwrite_input.flush()
    fwrite_output = open('{}/p{}/p{}_{}_output.txt'.format(model_dir, task_id, task_id, it), 'w')
    fwrite_output.write(answer)
    fwrite_output.flush()
    
    # delete files
    existing_code_files = os.listdir("{}/p{}".format(model_dir, task_id))
    for existing_code_file in existing_code_files:
        if existing_code_file.endswith(".sp"):
            os.remove("{}/p{}/{}".format(model_dir, task_id, existing_code_file))
            print("remove file: ", existing_code_file)
        if existing_code_file.endswith("_op.txt"):
            os.remove("{}/p{}/{}".format(model_dir, task_id, existing_code_file))
            print("remove file: ", existing_code_file)

    if os.path.exists("{}/p{}/{}".format(model_dir, task_id, it)):
        existing_code_files = os.listdir("{}/p{}/{}".format(model_dir, task_id, it))
        for existing_code_file in existing_code_files:
            if os.path.isfile("{}/p{}/{}/{}".format(model_dir, task_id, it, existing_code_file)):
                try:
                    os.remove("{}/p{}/{}/{}".format(model_dir, task_id, it, existing_code_file))
                except:
                    pass
                print("remove file: ", existing_code_file)
    
    
    while code_id < args.num_of_retry:
        messages.append({"role": "assistant", "content": answer})

        if not os.path.exists("{}/p{}/{}".format(model_dir, task_id, it)):
            # try:
            os.mkdir("{}/p{}/{}".format(model_dir, task_id, it))
            # except:
            #     pass

        code_path = '{}/p{}/{}/p{}_{}_{}.py'.format(model_dir, task_id, it, task_id, it, code_id)
        if args.ngspice:
            code_path = code_path.replace(".py", ".sp")
        fwrite_code = open(code_path, 'w')
        fwrite_code.write(code)
        fwrite_code.close()

        if args.ngspice:
            sp_code_path = code_path
            code_path = code_path.replace(".sp", ".py")
            write_pyspice_code(sp_code_path, code_path, operating_point_path)
            answer_code = open(code_path, 'r').read()
        else:
            answer_code = code
        
        if task_type in complex_task_type and args.skill == True:
            for subcircuit in subcircuits:
                shutil.copy(f"subcircuit_lib/p{subcircuit}_lib.py", "/".join(code_path.split("/")[:-1]))
        execution_error, simulation_error, execution_error_info, floating_node = run_code(code_path)
        print("execution_error = {}, simulation_error = {}".format(execution_error, simulation_error))


        dc_sweep_error = 0
        dc_sweep_success = 0

        if execution_error == 0 and simulation_error == 0:
            if task_type not in complex_task_type:
                _, code_netlist = None, answer_code
                code_netlist += output_netlist_template
                code_netlist_path = "{}/p{}/{}/p{}_{}_{}_netlist_gen.py".format(model_dir, task_id, it, task_id, it, code_id)
                fwrite_code_netlist = open(code_netlist_path, 'w')
                fwrite_code_netlist.write(code_netlist)
                fwrite_code_netlist.close()
                
                netlist_path = "{}/p{}/{}/p{}_{}_{}_netlist.sp".format(model_dir, task_id, it, task_id, it, code_id)
                result = subprocess.run(["python", "-u", code_netlist_path], check=True, text=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                netlist_file_path = "{}/p{}/{}/p{}_{}_{}_netlist.sp".format(model_dir, task_id, it, task_id, it, code_id)
                fwrite_netlist = open(netlist_file_path, 'w')
                fwrite_netlist.write("\n".join(result.stdout.split("\n")[1:]))
                fwrite_netlist.close()

                ## special for Opamp: dc sweep
                
                if "Opamp" in task_type or "Amplifier" in task_type:
                    vinn_name = "in"
                    vinp_name = "inp"
                    netlist_content = open(netlist_file_path, 'r').read()
                    vinn_name, vinp_name = get_vin_name(netlist_content, task_type)
                    dc_sweep_code_path = '{}/p{}/{}/p{}_{}_{}_dc_sweep.py'.format(model_dir, task_id, it, task_id, it, code_id)
                    dc_file_path = '{}/p{}/{}/p{}_{}_{}_dc.txt'.format(model_dir, task_id, it, task_id, it, code_id)
                    _, dc_sweep_code = None, answer_code
                    if "simulator = circuit.simulator()" not in dc_sweep_code:
                        dc_sweep_code += "\nsimulator = circuit.simulator()\n"
                    if task_type == "Opamp":
                        dc_sweep_code = connect_vinn_vinp(dc_sweep_code, vinn_name, vinp_name)
                    dc_sweep_code += dc_sweep_template.replace("[IN_NAME]", vinn_name).replace("[DC_PATH]", dc_file_path)
                    fwrite_dc_sweep_code = open(dc_sweep_code_path, 'w')
                    fwrite_dc_sweep_code.write(dc_sweep_code)
                    fwrite_dc_sweep_code.close()
                    try:
                        subprocess.run(["python", "-u", dc_sweep_code_path], check=True, text=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        dc_sweep_error, best_voltage = get_best_voltage(dc_file_path)
                        print("dc_sweep_error", dc_sweep_error)
                        print("best_voltage", best_voltage)
                        print("vinn_name", vinn_name)
                        print("vinp_name", vinp_name)
                        assert dc_sweep_error == 0
                        os.rename(code_path, code_path + ".bak")
                        print("code_path", code_path)
                        _, raw_code = None, answer_code
                        if "simulator = circuit.simulator()" not in raw_code:
                            raw_code += "\nsimulator = circuit.simulator()\n"
                        new_code = replace_voltage(raw_code, best_voltage, vinn_name, vinp_name)
                        # write new op analysis code
                        with open(f"{code_path}", "w") as f:
                            f.write(new_code)
                        # rerun the op test 
                        execution_error_1, simulation_error_1, execution_error_info_1, floating_node_1 = run_code(code_path)
                        # make sure the op test passed
                        assert execution_error_1 == 0
                        assert simulation_error_1 == 0
                        # All dc sweep passed
                        # generate a new netlist with the best voltage, replace _gen.py and .sp
                        new_code_netlist = new_code + output_netlist_template
                        code_netlist_path = "{}/p{}/{}/p{}_{}_{}_netlist_gen.py".format(model_dir, task_id, it, task_id, it, code_id)
                        fwrite_code_netlist = open(code_netlist_path, 'w')
                        fwrite_code_netlist.write(new_code_netlist)
                        fwrite_code_netlist.close()
                        netlist_path = "{}/p{}/{}/p{}_{}_{}_netlist.sp".format(model_dir, task_id, it, task_id, it, code_id)
                        result = subprocess.run(["python", "-u", code_netlist_path], check=True, text=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        netlist_file_path = "{}/p{}/{}/p{}_{}_{}_netlist.sp".format(model_dir, task_id, it, task_id, it, code_id)
                        fwrite_netlist = open(netlist_file_path, 'w')
                        fwrite_netlist.write("\n".join(result.stdout.split("\n")[1:]))
                        fwrite_netlist.close()
                        dc_sweep_success = 1
                    except:
                        # recover the raw file
                        if os.path.exists(code_path + ".bak"):
                            if os.path.exists(code_path):
                                os.remove(code_path)
                            os.rename(code_path + ".bak", code_path)
                # dc sweep finish
                
                warning, warning_message = check_netlist(netlist_path, operating_point_path, input, output, task_id, task_type)
                if warning == 0:
                    func_error, func_error_message = check_function(task_id, code_path, task_type)
                    func_error_message = func_error_message.replace("Unsupported Ngspice version 38", "")
                    func_error_message = func_error_message.replace("Unsupported Ngspice version 36", "")
                    if func_error ==0:
                        # completion
                        print("CODE_PATH = {}".format(code_path))
                        os.rename(code_path, code_path.rsplit(".", 1)[0] + "_success.py")
                        if any(model in args.model for model in opensource_models):
                            flog.write("task:{}\tit:{}\tcode_id:{}\tsuccess.\tcompletion_tokens:{}"
                                        "\tprompt_tokens:{}\ttotal_tokens:{}\n".format(task_id, it, code_id,
                                        completion.usage.completion_tokens,
                                        completion.usage.prompt_tokens,
                                        completion.usage.total_tokens))
                            flog.write("total_tokens\t{}\ttotal_prompt_tokens\t{}\ttotal_completion_tokens\t{}\n".format(total_tokens, total_prompt_tokens, total_completion_tokens))
                            ftmp_write = open(f'{model_dir}/p{task_id}/{it}/token_info_{total_tokens}_{total_prompt_tokens}_{total_completion_tokens}_{code_id}', 'w')
                            ftmp_write.close()
                        else:
                            flog.write("task:{}\tit:{}\tcode_id:{}\tsuccess.\n".format(task_id, it, code_id))
                        flog.write("money_quota\t{:.10f}\n".format(money_quota))
                        flog.flush()
                        break
            else:
                os.rename(code_path, code_path.rsplit(".", 1)[0]+"_success.py")
                if "llama" not in args.model and "wizard" not in args.model and "deepseek" not in args.model and "mistral" not in args.model and "qwencode" not in args.model and "mixtral" not in args.model:
                    flog.write("task:{}\tit:{}\tcode_id:{}\tsuccess.\tcompletion_tokens:{}"
                                "\tprompt_tokens:{}\ttotal_tokens:{}\n".format(task_id, it, code_id,
                                completion.usage.completion_tokens,
                                completion.usage.prompt_tokens,
                                completion.usage.total_tokens))
                    flog.write("total_tokens\t{}\ttotal_prompt_tokens\t{}\ttotal_completion_tokens\t{}\n".format(total_tokens, total_prompt_tokens, total_completion_tokens))
                    ftmp_write = open(f'{model_dir}/p{task_id}/{it}/token_info_{total_tokens}_{total_prompt_tokens}_{total_completion_tokens}_{code_id}', 'w')
                    ftmp_write.close()
                else:
                    flog.write("task:{}\tit:{}\tcode_id:{}\tsuccess.\n".format(task_id, it, code_id))
                flog.write("money_quota\t{:.10f}\n".format(money_quota))
                flog.flush()
                break
        
        # Ignore the compatible error
        execution_error_info = execution_error_info.replace("Unsupported Ngspice version 38", "")
        execution_error_info = execution_error_info.replace("Unsupported Ngspice version 36", "")

        if dc_sweep_error == 1:
            new_prompt = "According to dc sweep analysis, changing the input voltage does not change the output voltage. Please check the netlist and rewrite the complete code.\n"
            new_prompt += "Reference operating point:\n"
            op_content = open(operating_point_path, 'r').read()
            new_prompt += op_content

            flog.write("task:{}\tit:{}\tcode_id\t{}\tdc sweep error\n".format(task_id, it, code_id))
            flog.flush()
            ftmp = open("{}/p{}/{}/dc_sweep_error_{}".format(model_dir, task_id, it, code_id), "w")
            ftmp.close()
        else:
            if dc_sweep_success == 1:
                new_prompt = f"According to dc sweep analysis, the best input voltage is {best_voltage}. Please use this voltage.\n"
            else:
                new_prompt = ""
            if empty_code_error == 1:
                new_prompt += "There is no complete code in your reply. Please generate a complete code."
                flog.write("task:{}\tit:{}\tcode_id\t{}\tempty code error\n".format(task_id, it, code_id))
                flog.flush()
                ftmp = open("{}/p{}/{}/empty_error_{}".format(model_dir, task_id, it, code_id), "w")
                ftmp.close()
            elif simulation_error == 1:
                new_prompt += prompt_sim_error.replace("[NODE]", floating_node)
                flog.write("task:{}\tit:{}\tcode_id:{}\tsimulation error\n".format(task_id, it, code_id))
                flog.flush()
                ftmp = open("{}/p{}/{}/simulation_error_{}".format(model_dir, task_id, it, code_id), "w")
                ftmp.close()
            elif execution_error == 1:
                new_prompt += prompt_exe_error.replace("[ERROR]", execution_error_info)
                flog.write("task:{}\tit:{}\tcode_id:{}\texecution error\n".format(task_id, it, code_id))
                flog.flush()
                ftmp = open("{}/p{}/{}/execution_error_{}".format(model_dir, task_id, it, code_id), "w")
                ftmp.close()
            elif warning == 1:
                new_prompt += warning_message
                flog.write("task:{}\tit:{}\tcode_id:{}\tmosfet connection error\n".format(task_id, it, code_id))
                flog.flush()
                ftmp = open("{}/p{}/{}/mosfet_connection_error_{}".format(model_dir, task_id, it, code_id), "w")
                ftmp.close()
            elif func_error == 1:
                new_prompt += func_error_message
                new_prompt += "\nPlease rewrite the corrected complete code."
                flog.write("task:{}\tit:{}\tcode_id:{}\tfunction error\n".format(task_id, it, code_id))
                flog.flush()
                ftmp = open("{}/p{}/{}/function_error_{}".format(model_dir, task_id, it, code_id), "w")
                ftmp.close()
            else:
                assert False
        flog.write("total_tokens\t{}\ttotal_prompt_tokens\t{}\ttotal_completion_tokens\t{}\n".format(total_tokens, total_prompt_tokens, total_completion_tokens))
        flog.write("money_quota\t{:.10f}\n".format(money_quota))        
        ftmp_write = open(f'{model_dir}/p{task_id}/{it}/token_info_{total_tokens}_{total_prompt_tokens}_{total_completion_tokens}_{code_id}', 'w')
        ftmp_write.close()
        flog.flush()
        code_id += 1
        if code_id >= args.num_of_retry:
            break
        messages.append({"role": "user", "content": new_prompt})

        if money_quota < 0:
            flog.write("Money quota is used up. Exceed quota: {}\n".format(money_quota))
            return

        retry = True
        while retry:
            try:
                if any(model in args.model for model in opensource_models):
                    print(f"start {args.model} completion")
                    signal.signal(signal.SIGALRM, signal_handler)
                    signal.alarm(360)
                    try:
                        completion = ollama.chat(
                            model=args.model,
                            messages=messages,
                            options={
                                "temperature": args.temperature,
                                "top_p": 1.0,
                            })
                        print(f"{args.model} completion finish")
                        signal.alarm(0)
                        break
                    except TimeoutException as e:
                        print(e)
                        print("timeout")
                        signal.alarm(0)
                        print("restart ollama")
                        kill_tmux_session("ollama")
                        result = subprocess.run(['ollama', 'restart'], capture_output=True, text=True)
                        start_tmux_session("ollama", "ollama serve")
                        time.sleep(120)
                else:
                    completion = client.chat.completions.create(
                        model = args.model,
                        messages = messages,
                        temperature = args.temperature
                    )
                    break
            except openai.APIStatusError as e:
                print("Encountered an APIStatusError. Details:")
                print(e)
                print("sleep 30 seconds")
                time.sleep(30)

        if "gpt" in args.model:
            total_tokens += completion.usage.total_tokens
            total_prompt_tokens += completion.usage.prompt_tokens
            total_completion_tokens += completion.usage.completion_tokens

        if "ft:gpt-3.5" in args.model:
            money_quota -= (completion.usage.prompt_tokens / 1e6 * 3) + (completion.usage.completion_tokens / 1e6 * 6)
        elif "gpt-3" in args.model:
            money_quota -= (completion.usage.prompt_tokens / 1e6 * 0.5) + (completion.usage.completion_tokens / 1e6 * 1.5)
        elif "gpt-4" in args.model:
            money_quota -= (completion.usage.prompt_tokens / 1e6 * 10) + (completion.usage.completion_tokens / 1e6 * 30)

        fwrite_input.write("\n----------\n")
        fwrite_input.write(new_prompt)
        fwrite_input.flush()

        if "gpt" in args.model or "deepseek-chat" in args.model:
            answer = completion.choices[0].message.content
        else:
            answer = completion['message']['content']

        fwrite_output.write("\n----------\n")
        fwrite_output.write(answer)

        empty_code_error, code = extract_code(answer)


        operating_point_path = "{}/p{}/{}/p{}_{}_{}_op.txt".format(model_dir, task_id, it, task_id, it, code_id)
        if "simulator = circuit.simulator()" not in code:
            code += "\nsimulator = circuit.simulator()\n"
        if task_type not in complex_task_type:
            code += pyspice_template.replace("[OP_PATH]", operating_point_path)
        else:
            figure_path = "{}/p{}/{}/p{}_{}_{}_figure".format(model_dir, task_id, it, task_id, it, code_id)
            if task_type == "Oscillator":
                code += pyspice_template_complex.replace("[FIGURE_PATH]", figure_path)
            else:
                if args.skill:
                    code += pyspice_template_complex.replace("[FIGURE_PATH]", figure_path).replace('[BIAS_VOLTAGE]', str(bias_voltage))
                else:
                    code += pyspice_template_complex.replace("[FIGURE_PATH]", figure_path).replace('[BIAS_VOLTAGE]', "float(circuit.element(vin_name).dc_value)")
            if "import math" not in code:
                code = "import math\n" + code
    
    # save messages
    fwrite = open('{}/p{}/{}/p{}_{}_messages.txt'.format(model_dir, task_id, it, task_id, it), 'w')
    fwrite.write(str(messages))
    fwrite.close()
    fwrite_input.close()
    fwrite_output.close()
    return money_quota


def main():
    data_path = 'problem_set.tsv'
    df = pd.read_csv(data_path, delimiter='\t')
    # print(df)
    if args.task_id >= 16:
        candidate_path = 'candidate.tsv'
        df_candidate = pd.read_csv(candidate_path, delimiter='\t')
        # print(df_candidate)
    # set money cost to $2
    remaining_money = 2
    for index, row in df.iterrows():
        circuit_id = row['Id']
        if circuit_id != args.task_id:
            continue
        strftime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        if args.ngspice:
            flog = open('{}_{}_{}_ngspice_log.txt'.format(strftime, args.model, circuit_id), 'w')
        elif args.no_prompt:
            flog = open('{}_{}_{}_no_prompt_log.txt'.format(strftime, args.model, circuit_id), 'w')
        elif args.no_context:
            flog = open('{}_{}_{}_no_context_log.txt'.format(strftime, args.model, circuit_id), 'w')
        elif args.no_chain:
            flog = open('{}_{}_{}_no_chain_log.txt'.format(strftime, args.model, circuit_id), 'w')
        elif not args.skill and row['Type'] in complex_task_type:
            flog = open('{}_{}_{}_log_no_skill.txt'.format(strftime, args.model, circuit_id), 'w')
        else:
            flog = open('{}_{}_{}_log.txt'.format(strftime, args.model, circuit_id), 'w')
        for it in range(args.num_of_done, args.num_per_task):
            flog.write("task: {}, it: {}\n".format(circuit_id, it))
            flog.flush()
            if row['Type'] in complex_task_type:
                df_candidate_row = df_candidate[df_candidate['Id'] == row['Id']]
                cand_list = eval(df_candidate_row['Candidate'].values[0])
                subcircuits = cand_list[it%len(cand_list)]
            else:
                subcircuits = None
            remaining_money = work(row['Circuit'], row['Input'].strip(), row['Output'].strip(), circuit_id, it, 
                                   None, row['Type'], flog, money_quota=remaining_money,
                                   subcircuits = subcircuits)
            if remaining_money < 0:
                break
    
if __name__ == "__main__":
    main()
