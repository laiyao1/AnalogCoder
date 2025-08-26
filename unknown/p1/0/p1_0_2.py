
simulator = circuit.simulator()

try:
    analysis = simulator.operating_point()
    fopen = open("unknown/p1/0/p1_0_0_op.txt", "w")
    for node in analysis.nodes.values(): 
        fopen.write(f"{str(node)}\t{float(analysis[str(node)][0]):.6f}\n")
    fopen.close()
except Exception as e:
    print("Analysis failed due to an error:")
    print(str(e))
