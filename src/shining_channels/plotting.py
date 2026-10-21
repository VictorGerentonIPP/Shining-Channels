import os

import matplotlib.pyplot as plt
import numpy as np

from shining_channels.attack import key_rank_curve
from shining_channels.data import load_dataset


def save_figure(fig, out, name):
    os.makedirs(out, exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{name}.{extension}"), dpi=200, bbox_inches="tight")


def key_rank_figure(data, out, name, max_traces, points, experiments, seed=0, locate=True):
    traces, plaintexts, key = load_dataset(data)
    counts = np.linspace(max_traces / points, max_traces, points).astype(int)
    ranks = key_rank_curve(traces, plaintexts, key, counts, experiments, seed=seed, locate=locate)
    os.makedirs(out, exist_ok=True)
    np.savez(os.path.join(out, f"{name}.npz"), counts=counts, ranks=ranks)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(counts, ranks.mean(axis=1), color="tab:blue")
    ax.set_xlabel("# Traces")
    ax.set_ylabel("log2(key rank)")
    ax.set_ylim(bottom=0)
    save_figure(fig, out, name)
