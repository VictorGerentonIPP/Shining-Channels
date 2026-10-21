import argparse
import os

import numpy as np

from shining_channels.attack import cpa_correlations
from shining_channels.data import load_dataset


def to_latex(rows):
    bytes_row = " & ".join(str(byte) for byte, *_ in rows)
    correct_row = " & ".join(f"{correct:.3f}" for _, correct, _, _ in rows)
    wrong_row = " & ".join(f"{wrong:.3f}" for _, _, wrong, _ in rows)
    rank_row = " & ".join(rf"$\tfrac{{{rank}}}{{256}}$" for *_, rank in rows)
    return "\n".join([
        r"\begin{tabular}{l" + "c" * len(rows) + "}",
        r"\toprule",
        rf"Byte & {bytes_row} \\",
        r"\midrule",
        rf"$|\rho|_{{\mathrm{{c}}}}$ & {correct_row} \\",
        rf"$|\rho|_{{\mathrm{{w}}}}$ & {wrong_row} \\",
        rf"Rank & {rank_row} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Table 2: per-byte CPA results on the optical traces")
    parser.add_argument("--data", default="data/sfp_0dbm")
    parser.add_argument("--out", default="results")
    args = parser.parse_args(argv)

    traces, plaintexts, key = load_dataset(args.data)

    rows = []
    for byte in range(16):
        peaks = np.nanmax(np.abs(cpa_correlations(traces, plaintexts, byte)), axis=1)
        correct = peaks[key[byte]]
        wrong = np.delete(peaks, key[byte]).max()
        rank = int((peaks > correct).sum()) + 1
        rows.append((byte, correct, wrong, rank))
        print(f"byte {byte:2d}: rank {rank}/256", flush=True)

    lines = [
        "Byte " + " ".join(f"{b:5d}" for b, *_ in rows),
        "|rho|c " + " ".join(f"{c:5.3f}" for _, c, _, _ in rows),
        "|rho|w " + " ".join(f"{w:5.3f}" for _, _, w, _ in rows),
        "Rank " + " ".join(f"{r:5d}" for *_, r in rows),
    ]

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "table2.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(args.out, "table2.tex"), "w") as f:
        f.write(to_latex(rows))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
