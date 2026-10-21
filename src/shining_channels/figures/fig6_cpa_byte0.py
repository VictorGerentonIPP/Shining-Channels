import argparse

import matplotlib.pyplot as plt
import numpy as np

from shining_channels.attack import cpa_correlations
from shining_channels.data import load_dataset
from shining_channels.plotting import save_figure


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 6: CPA correlation traces of key byte 0")
    parser.add_argument("--data", default="data/sfp_0dbm")
    parser.add_argument("--out", default="results")
    args = parser.parse_args(argv)

    traces, plaintexts, key = load_dataset(args.data)
    correlations = np.nan_to_num(cpa_correlations(traces, plaintexts, byte=0))
    peaks = np.abs(correlations).max(axis=1)
    best = np.argsort(peaks)[::-1][:5]

    fig, ax = plt.subplots(figsize=(8, 4))
    for hypothesis in range(256):
        ax.plot(correlations[hypothesis], color="lightgray", linewidth=0.5)
    wrong_colors = iter(["tab:orange", "tab:red", "tab:purple", "tab:blue", "tab:brown"])
    for hypothesis in best[::-1]:
        is_correct = hypothesis == key[0]
        ax.plot(
            correlations[hypothesis],
            linewidth=1.8 if is_correct else 0.8,
            color="tab:green" if is_correct else next(wrong_colors),
            label=f"0x{hypothesis:02x} (|corr|={peaks[hypothesis]:.4f})",
        )
    ax.set_xlabel("Sample")
    ax.set_ylabel("Correlation")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
    save_figure(fig, args.out, "fig6_cpa_byte0")


if __name__ == "__main__":
    main()
