import argparse

import matplotlib.pyplot as plt

from shining_channels.attack import snr
from shining_channels.data import load_dataset
from shining_channels.plotting import save_figure


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 2: SNR of the EM traces (key byte 5)")
    parser.add_argument("--data", default="data/sfp_em")
    parser.add_argument("--out", default="results")
    args = parser.parse_args(argv)

    traces, plaintexts, key = load_dataset(args.data)
    curve = snr(traces, plaintexts, key, byte=5)
    print(f"SNR peak: {curve.max():.4f} at sample {curve.argmax()}, median {sorted(curve)[len(curve) // 2]:.4f}")

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(curve, color="tab:green", linewidth=0.8)
    ax.set_xlabel("Sample")
    ax.set_ylabel("SNR")
    save_figure(fig, args.out, "fig2_snr_em")


if __name__ == "__main__":
    main()
