import csv


def parse_swissdock_csv(csv_file):
    """
    Parses SwissDock binding_modes.csv
    Returns best (lowest) ΔG energy
    """
    energies = []

    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                for key in row:
                    if "dg" in key.lower():
                        try:
                            energies.append(float(row[key]))
                        except ValueError:
                            pass

    except FileNotFoundError:
        raise FileNotFoundError(f"SwissDock file not found: {csv_file}")

    if not energies:
        raise ValueError("No ΔG values found in SwissDock output")

    return min(energies)
