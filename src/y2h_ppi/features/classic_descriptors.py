import itertools
import numpy as np
import pandas as pd
from typing import Dict, List
from y2h_ppi.logger import logger

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
AA_TO_INDEX = {aa: i for i, aa in enumerate(AMINO_ACIDS)}

# Shen et al. 2007 Conjoint Triad 7 amino acid groups:
# Group 1: Aliphatic (Ala, Val, Leu, Ile, Pro, Phe, Met) -> A, V, L, I, P, F, M
# Group 2: Neutral / Small (Gly, Ser, Thr, Cys, Asn, Gln, Tyr) -> G, S, T, C, N, Q, Y
# Group 3: Basic (Lys, Arg, His) -> K, R, H
# Group 4: Acidic (Asp, Glu) -> D, E
# Group 5: Aromatic / Special (Trp) -> W
# Group 6: (Disulfide/Cys - in standard 7-class grouping, mapped as follows):
# Verified Grouping Table:
CT_GROUP_MAP = {
    'A': 1, 'V': 1, 'L': 1, 'I': 1, 'P': 1, 'F': 1, 'M': 1,
    'G': 2, 'S': 2, 'T': 2, 'Y': 2,
    'H': 3, 'K': 3, 'R': 3,
    'D': 4, 'E': 4,
    'N': 5, 'Q': 5,
    'C': 6,
    'W': 7
}

def compute_aac(sequence: str) -> np.ndarray:
    """Amino Acid Composition (AAC): 20-dimensional relative residue frequency."""
    seq_len = len(sequence)
    if seq_len == 0:
        return np.zeros(20, dtype=np.float32)
    counts = np.zeros(20, dtype=np.float32)
    for char in sequence:
        if char in AA_TO_INDEX:
            counts[AA_TO_INDEX[char]] += 1.0
    return counts / seq_len

def compute_dpc(sequence: str) -> np.ndarray:
    """Dipeptide Composition (DPC): 400-dimensional relative 2-mer frequency."""
    dpc = np.zeros(400, dtype=np.float32)
    seq_len = len(sequence)
    if seq_len < 2:
        return dpc
    for i in range(seq_len - 1):
        di = sequence[i:i+2]
        if di[0] in AA_TO_INDEX and di[1] in AA_TO_INDEX:
            idx = AA_TO_INDEX[di[0]] * 20 + AA_TO_INDEX[di[1]]
            dpc[idx] += 1.0
    return dpc / (seq_len - 1)

def compute_conjoint_triad(sequence: str) -> np.ndarray:
    """Conjoint Triad (CT): 343-dimensional 3-mer frequency vector over 7 amino acid groups."""
    ct = np.zeros(343, dtype=np.float32)
    seq_len = len(sequence)
    if seq_len < 3:
        return ct
    
    # Map sequence to group numbers (0..6)
    grouped_seq = []
    for char in sequence:
        g = CT_GROUP_MAP.get(char, 1) - 1  # 0-indexed group
        grouped_seq.append(g)
        
    for i in range(seq_len - 2):
        g1, g2, g3 = grouped_seq[i], grouped_seq[i+1], grouped_seq[i+2]
        idx = g1 * 49 + g2 * 7 + g3
        ct[idx] += 1.0
        
    return ct / (seq_len - 2)

def compute_ctd(sequence: str) -> np.ndarray:
    """Composition-Transition-Distribution (CTD): 21-dimensional simplified physicochemical descriptor."""
    # Simplified CTD Composition across Hydrophobicity, Charge, Polarity (7 properties x 3 classes = 21 dim)
    ctd = np.zeros(21, dtype=np.float32)
    seq_len = len(sequence)
    if seq_len == 0:
        return ctd
        
    # Property 1: Hydrophobicity (Polar, Neutral, Hydrophobic)
    hydro = {'R':0,'K':0,'E':0,'D':0,'Q':0,'N':0, 'G':1,'A':1,'S':1,'T':1,'P':1,'H':1,'Y':1, 'C':2,'V':2,'L':2,'I':2,'M':2,'F':2,'W':2}
    # Property 2: Charge (Positive, Neutral, Negative)
    charge = {'K':0,'R':0,'H':0, 'A':1,'N':1,'C':1,'Q':1,'G':1,'I':1,'L':1,'M':1,'F':1,'P':1,'S':1,'T':1,'W':1,'Y':1,'V':1, 'D':2,'E':2}
    
    for i, char in enumerate(sequence):
        if char in hydro:
            ctd[hydro[char]] += 1.0
        if char in charge:
            ctd[3 + charge[char]] += 1.0
            
    ctd[:6] /= seq_len
    return ctd

def extract_classical_descriptors(sequence: str) -> np.ndarray:
    """Extract concatenated classical sequence descriptor vector (AAC + DPC + CTD + Conjoint Triad)."""
    aac = compute_aac(sequence)
    dpc = compute_dpc(sequence)
    ctd = compute_ctd(sequence)
    ct = compute_conjoint_triad(sequence)
    return np.concatenate([aac, dpc, ctd, ct])  # 20 + 400 + 21 + 343 = 784 dimensions
