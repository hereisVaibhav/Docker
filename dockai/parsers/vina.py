import re

def parse_vina_output(file_path):
    """
    Extracts best binding energy from AutoDock Vina output.
    Supports multiple output formats.
    """

    energies = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Format: REMARK VINA RESULT: -8.5 0.000 0.000
            if "REMARK VINA RESULT" in line:
                parts = line.split()
                energies.append(float(parts[3]))

            # Format: table output -> 1 -8.5 0.000
            elif re.match(r"^\s*\d+\s+-\d+\.\d+", line):
                parts = line.split()
                energies.append(float(parts[1]))

            # Format: Affinity: -8.5 (kcal/mol)
            elif "Affinity:" in line:
                match = re.search(r"-\d+\.\d+", line)
                if match:
                    energies.append(float(match.group()))

    if not energies:
        raise ValueError("No binding energy found in Vina output")

    return min(energies)  # Best (lowest) energy
