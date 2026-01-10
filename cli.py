print("CLI LOADED FROM UPDATED FILE")

import sys
import os

from dockai.parsers.vina import parse_vina_output
from dockai.interactions.distance import detect_interactions


REPORT_FILE = "dockai_report.txt"
BATCH_REPORT_FILE = "batch_report.txt"


# ---------------- ENERGY INTERPRETATION ---------------- #

def interpret_vina_energy(energy):
    if energy <= -8.0:
        return "Strong binding affinity"
    elif energy <= -6.0:
        return "Moderate binding affinity"
    else:
        return "Weak binding affinity"


def interpret_swissdock_energy(energy):
    if energy <= -9.0:
        return "Very strong binding affinity (SwissDock ΔG)"
    elif energy <= -7.0:
        return "Strong binding affinity (SwissDock ΔG)"
    elif energy <= -5.5:
        return "Moderate binding affinity (SwissDock ΔG)"
    else:
        return "Weak binding affinity (SwissDock ΔG)"


# ---------------- REPORT WRITER ---------------- #

def write_report(tool, energy, interpretation, interactions):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("DockAI – Molecular Docking Interpretation Report\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Docking Tool: {tool}\n")
        f.write(f"Best Binding Energy: {energy} kcal/mol\n")
        f.write(f"Interpretation: {interpretation}\n\n")

        if interactions:
            f.write("Interacting Residues (distance ≤ 4.0 Å):\n")
            for res, itype in interactions.items():
                f.write(f"- {res} ({itype})\n")
        else:
            f.write("Interaction analysis: Not available / skipped\n")

    print(f"\nReport saved as: {REPORT_FILE}")


# ---------------- BATCH MODE ---------------- #

def run_batch(folder):
    results = []

    for file in os.listdir(folder):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(folder, file)

        try:
            energy = parse_vina_output(path)
            results.append((file, energy))
        except Exception as e:
            print(f"Skipping {file}: {e}")

    results.sort(key=lambda x: x[1])

    print("\nBatch Docking Ranking:\n")

    with open(BATCH_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("Batch Docking Ranking (AutoDock Vina)\n")
        f.write("=" * 40 + "\n\n")

        for fname, energy in results:
            line = f"{fname}: {energy} kcal/mol\n"
            print(line.strip())
            f.write(line)

    print(f"\nBatch report saved as: {BATCH_REPORT_FILE}")


# ---------------- MAIN ---------------- #

def main():
    # -------- SwissDock mode --------
    if "--swissdock" in sys.argv:
        idx = sys.argv.index("--swissdock")

        if len(sys.argv) <= idx + 1:
            print("Usage: python cli.py --swissdock binding_modes.csv")
            sys.exit(1)

        csv_file = sys.argv[idx + 1]

        from dockai.parsers.swissdock import parse_swissdock_csv

        energy = parse_swissdock_csv(csv_file)
        interpretation = interpret_swissdock_energy(energy)

        print(f"\nBest SwissDock ΔG: {energy} kcal/mol")
        print(f"Interpretation: {interpretation}")

        write_report(
            tool="SwissDock",
            energy=energy,
            interpretation=interpretation,
            interactions={}
        )
        return

    # -------- Batch Vina mode --------
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")

        if len(sys.argv) <= idx + 1:
            print("Usage: python cli.py --batch <folder>")
            sys.exit(1)

        run_batch(sys.argv[idx + 1])
        return

    # -------- Single Vina mode --------
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python cli.py vina_output.txt")
        print("  python cli.py --batch batch_folder")
        print("  python cli.py --swissdock binding_modes.csv")
        sys.exit(1)

    vina_output = sys.argv[1]

    protein_pdb = "protein.pdb"
    ligand_pdbqt = "ligand.pdbqt"

    energy = parse_vina_output(vina_output)
    interpretation = interpret_vina_energy(energy)

    interactions = {}
    if os.path.exists(protein_pdb) and os.path.exists(ligand_pdbqt):
        interactions = detect_interactions(protein_pdb, ligand_pdbqt)

    print(f"\nBest binding energy: {energy} kcal/mol")
    print(f"Interpretation: {interpretation}")

    write_report(
        tool="AutoDock Vina",
        energy=energy,
        interpretation=interpretation,
        interactions=interactions
    )


if __name__ == "__main__":
    main()
