import sys

# opcode to instruction type
R_TYPE = 0b0110011
I_TYPE_ALU = 0b0010011
I_TYPE_LW = 0b0000011
I_TYPE_JALR = 0b1100111
S_TYPE = 0b0100011
B_TYPE = 0b1100011
U_TYPE_LUI = 0b0110111
U_TYPE_AUIPC = 0b0010111
J_TYPE = 0b1101111

# parse file
def parse_trace(file):
    inst = []
    with open(file, "r") as f:
        for line in f:
            line_arr = line.strip().split()
            line_dict = {"Cycle": int(line_arr[0]), "PC": line_arr[1], "Instruction": line_arr[2]}
            inst.append(line_dict)
    return inst

# decode instruction, extract register dependency sets 
def decode_fields(inst_bin: str):
    x = int(inst_bin, 2)

    # bits [6:0]
    opcode = x & 0x7F
    # bits [11:7]   
    rd  = (x >> 7)  & 0x1F
    # bits [19:15]
    rs1 = (x >> 15) & 0x1F
    # bits [24:20]     
    rs2 = (x >> 20) & 0x1F     

    uses = set()
    defs = set()

    # decode instruction based on opcode
    if opcode == R_TYPE:
        defs.add(rd)
        uses.add(rs1); uses.add(rs2)

    elif opcode == I_TYPE_ALU:
        defs.add(rd)
        uses.add(rs1)

    elif opcode == I_TYPE_LW:
        defs.add(rd)
        uses.add(rs1)

    elif opcode == I_TYPE_JALR:
        defs.add(rd)
        uses.add(rs1)

    elif opcode == S_TYPE:
        uses.add(rs1); uses.add(rs2)

    elif opcode == B_TYPE:
        uses.add(rs1); uses.add(rs2)

    elif opcode == U_TYPE_LUI:
        defs.add(rd)

    elif opcode == U_TYPE_AUIPC:
        defs.add(rd)

    elif opcode == J_TYPE:
        defs.add(rd)

    else:
        raise ValueError(f"Unsupported opcode {opcode:07b} for inst {inst_bin}")

    return uses, defs

def compute_pressure(trace_rows):
    LIVE = set()
    pressure = [0] * len(trace_rows)

    # walk backward
    for i in range(len(trace_rows) - 1, -1, -1):
        inst_bin = trace_rows[i]["Instruction"]
        uses, defs = decode_fields(inst_bin)

        LIVE = (LIVE - defs) | uses

        # exclude x0 from pressure count
        pressure[i] = len(LIVE - {0})

    return pressure

def average_pressure(pressure):
    return sum(pressure) / len(pressure) if pressure else 0.0

def find_max_pressure(pressure):
    if not pressure:
        return 0, None
    mx = max(pressure)
    # note this is the first occurence of the max pressure
    cycle = pressure.index(mx)
    return mx, cycle

def find_min_pressure(pressure):
    if not pressure:
        return 0, None
    mn = min(pressure)
    # first occurence
    cycle = pressure.index(mn) 
    return mn, cycle

# file output for per cycle register pressure in CSV format 
def write_pressure_csv(trace_rows, pressure, filename):
    with open(filename, "w") as f:
        f.write("cycle,pressure\n")

        for i in range(len(pressure)):
            cycle = trace_rows[i]["Cycle"]
            f.write(f"{cycle},{pressure[i]}\n")

# plot pressure vs cycle for visualization
def plot_pressure(pressure):
    import matplotlib.pyplot as plt

    cycles = list(range(len(pressure)))

    plt.figure()
    plt.plot(cycles, pressure)
    plt.xlabel("Cycle")
    plt.ylabel("Register Pressure")
    plt.title("Register Pressure per Cycle")
    plt.show()

def main():
    if len(sys.argv) < 2:
        print("Usage: python reg_pressure.py <trace_file_path>")
        sys.exit(1)

    trace_path = sys.argv[1]

    trace = parse_trace(trace_path)
    pressure = compute_pressure(trace)

    # output per cycle pressure to CSV
    write_pressure_csv(trace, pressure, "per_cycle_pressure.csv")

    # average pressure over all instructions
    avg = average_pressure(pressure)

    # max pressure + where it occurs
    mx, mx_idx = find_max_pressure(pressure)
    mx_cycle = trace[mx_idx]["Cycle"] if mx_idx is not None else None
    mx_pc = trace[mx_idx]["PC"] if mx_idx is not None else None

    # min pressure + where it occurs
    mn, mn_idx = find_min_pressure(pressure)
    mn_cycle = trace[mn_idx]["Cycle"] if mn_idx is not None else None
    mn_pc = trace[mn_idx]["PC"] if mn_idx is not None else None

    # optional: plot pressure vs cycle for report statistic
    # plot_pressure(pressure)

    print(f"Average pressure: {avg:.6f}")
    print(f"Max pressure: {mx} at cycle {mx_cycle} (pc={mx_pc})")
    print(f"Min pressure: {mn} at cycle {mn_cycle} (pc={mn_pc})")

if __name__ == "__main__":
    main()