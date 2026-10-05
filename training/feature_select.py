#!/usr/bin/env python3
"""Feature selection for the pre‑processed NumPy dataset.
It uses scikit‑learn's SelectKBest (ANOVA F‑value) and saves a reduced .npz.
"""
import argparse
import json
import numpy as np
from pathlib import Path
from sklearn.feature_selection import SelectKBest, f_classif

def main():
    parser = argparse.ArgumentParser(
        description="Select top‑k features from the pre‑processed dataset"
    )
    parser.add_argument("--input", required=True, help="Path to input .npz file")
    parser.add_argument("--output", required=True, help="Path to output .npz file")
    parser.add_argument("-k", type=int, default=50, help="Number of features to keep")
    args = parser.parse_args()

    data = np.load(args.input, allow_pickle=True)
    X, y = data["X"], data["y"]
    label_names = data["label_names"]
    # flatten temporal dimension for feature selection
    num_seq, seq_len, feat_dim = X.shape
    X_flat = X.reshape(num_seq, seq_len * feat_dim)
    selector = SelectKBest(score_func=f_classif, k=args.k)
    X_selected = selector.fit_transform(X_flat, y)
    # reshape back preserving sequence length (approximate)
    new_feat_dim = X_selected.shape[1] // seq_len
    X_selected = X_selected[:, : seq_len * new_feat_dim].reshape(num_seq, seq_len, new_feat_dim)

    np.savez_compressed(
        args.output,
        X=X_selected,
        y=y,
        label_names=label_names,
    )
    print(f"✅ Saved reduced dataset to {args.output} (k={args.k})")

if __name__ == "__main__":
    main()
