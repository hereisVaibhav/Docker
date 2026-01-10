import numpy as np
from Bio.PDB import PDBParser

CHARGED_RESIDUES = {"ASP", "GLU", "LYS", "ARG"}
HBOND_ATOMS = {"N", "O"}

def detect_interactions(protein_pdb, ligand_pdbqt):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", protein_pdb)

    ligand_atoms = []
    with open(ligand_pdbqt) as f:
        for line in f:
            if line.startswith("ATOM"):
                atom_name = line[12:16].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                ligand_atoms.append((atom_name, np.array([x, y, z])))

    interactions = {}

    for model in structure:
        for chain in model:
            for residue in chain:
                resname = residue.get_resname()
                resid = residue.get_id()[1]
                res_id = f"{resname}{resid}"

                for atom in residue:
                    prot_atom = atom.get_name()
                    prot_coord = atom.get_coord()

                    for lig_atom, lig_coord in ligand_atoms:
                        dist = np.linalg.norm(prot_coord - lig_coord)

                        # Hydrogen bond
                        if prot_atom[0] in HBOND_ATOMS and lig_atom[0] in HBOND_ATOMS and dist <= 3.5:
                            interactions[res_id] = "Hydrogen bond"

                        # Electrostatic
                        elif resname in CHARGED_RESIDUES and dist <= 4.0:
                            interactions[res_id] = "Electrostatic interaction"

                        # Hydrophobic
                        elif prot_atom.startswith("C") and lig_atom.startswith("C") and dist <= 4.5:
                            interactions[res_id] = "Hydrophobic interaction"

    return interactions
