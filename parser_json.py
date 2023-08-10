import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str,
                    help='SMT file name.')
args = parser.parse_args()

# Opening JSON file
f = open(args.file)
 
# returns JSON object as
# a dictionary
data = json.load(f)

gate_qubit_layers = data["layers"]
total_time_step = data["n_t"]
total_qubit = data["n_q"]
assert(total_time_step == len(gate_qubit_layers))

is_busy = [[False for j in range(total_time_step)] for i in range(total_qubit) ]
is_aod = [[False for j in range(total_time_step)] for i in range(total_qubit) ]
has_gate = [False for i in range(total_time_step)]
rydberg_laser_count = 0

for t, layer in enumerate(gate_qubit_layers):
    # check is qubit in aod or slm
    for qubit_info in layer["qubits"]:
        is_aod[qubit_info["id"]][t] = qubit_info["a"]
    
    # check the qubits involving in gate operations
    if len(layer["gates"]) > 0:
        has_gate[t] = True
        rydberg_laser_count += 1
    
    for gate_info in layer["gates"]:
        is_busy[gate_info["q0"]][t] = True
        is_busy[gate_info["q1"]][t] = True


# print("is_busy: ")
# print(is_busy)
# print("is_aod: ")
# print(is_aod)
# print("has_gate: ")
# print(has_gate)

n_r = total_qubit * rydberg_laser_count
n_r_reduction = 0

is_in_mem = [[False for j in range(total_time_step)] for i in range(total_qubit) ]

for i in range(total_qubit):
    for j in range(total_time_step):
        if has_gate[j]:
            if (is_aod[i][j] or is_in_mem[i][j]) and not is_busy[i][j]:
                is_in_mem[i][j] = 1
            if is_busy[i][j]:
                is_in_mem[i][j] = 0
            if is_in_mem[i][j]:
                n_r_reduction += 1
            if j+2 < total_time_step:
                if not is_aod[i][j] and not is_busy[i][j] and not is_busy[i][j+1]:
                    is_in_mem[i][j] = 1

print(f"n_rydberg w/o memory zone={n_r}")
print(f"n_rydberg w/ memory zone={n_r-n_r_reduction}, reduce {n_r_reduction}, ratio={n_r/(n_r-n_r_reduction)}")