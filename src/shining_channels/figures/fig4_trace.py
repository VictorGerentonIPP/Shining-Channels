import argparse

import matplotlib.pyplot as plt
import numpy as np

from shining_channels.data import load_dataset
from shining_channels.plotting import save_figure


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 4: one optical trace with the laser gating")
    parser.add_argument("--data", default="data/sfp_0dbm")
    parser.add_argument("--out", default="results")
    args = parser.parse_args(argv)

    traces, _, _ = load_dataset(args.data)
    trace = np.asarray(traces[0], dtype=np.int16)

    baseline = np.median(trace[:1000])
    active = np.flatnonzero(np.abs(trace - baseline) > 20)
    laser_on, laser_off = active[0], active[-1]
    print(f"laser on at sample {laser_on}, off at sample {laser_off}")

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(trace, color="tab:blue", linewidth=0.8)
    ax.axvline(laser_on, color="gray", linewidth=0.8)
    ax.axvline(laser_off, color="gray", linewidth=0.8)
    top = ax.get_ylim()[1]
    ax.annotate("Laser ON", (laser_on, top), ha="right", va="bottom")
    ax.annotate("Laser OFF", (laser_off, top), ha="left", va="bottom")
    ax.annotate("MixColumns", ((laser_on + laser_off) / 2, top), ha="center", va="bottom")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Amplitude")
    save_figure(fig, args.out, "fig4_trace")


if __name__ == "__main__":
    main()
