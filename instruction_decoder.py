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

def max_pressure_and_cycle(pressure):
    if not pressure:
        return 0, None
    mx = max(pressure)
    cycle = pressure.index(mx)  # first occurrence
    return mx, cycle

def min_pressure(pressure):
    return min(pressure) if pressure else 0

def main():
    trace = parse_trace("HW1_trace_rv32i.txt")
    pressure = compute_pressure(trace)

    avg = average_pressure(pressure)
    mx, mx_idx = max_pressure_and_cycle(pressure)
    mn = min_pressure(pressure)

    mx_cycle = trace[mx_idx]["Cycle"] if mx_idx is not None else None
    mx_pc = trace[mx_idx]["PC"] if mx_idx is not None else None

    print(f"Average pressure: {avg:.6f}")
    print(f"Max pressure: {mx} at cycle {mx_cycle} (pc={mx_pc})")
    print(f"Min pressure: {mn}")

if __name__ == "__main__":
    main()