import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
from scalib.attacks import Cpa
from scalib.metrics import SNR
from scalib.postprocessing import rank_nbin

from shining_channels.attack import HW_SBOX, SBOX
from shining_channels.plotting import save_figure

NOISE_STD = 4.49
HIGH_LEVEL = 64.0
SAMPLES_PER_BIT = 4
N_BITS = 128
N_SAMPLES = N_BITS * SAMPLES_PER_BIT
LEAK_SAMPLE = N_SAMPLES // 2
REFERENCE_N = 500000

MODEL = np.broadcast_to(HW_SBOX[None, :, None], (16, 256, N_SAMPLES)).copy()

CASES = {
    "(i) No communication": (False, False),
    "(ii) NRZ communication": (True, False),
    "(iii) NRZ subset": (True, True),
}
STYLES = [dict(color="C0", ls="-"), dict(color="C3", ls="--"), dict(color="C2", ls="-.")]


def make_traces(n, key, communication, rng, noise_std=NOISE_STD):
    words = rng.integers(0, 256, (n, 16), dtype=np.uint8)
    bits = rng.integers(0, 2, (n, N_BITS)) if communication else np.ones((n, N_BITS), dtype=int)
    traces = HIGH_LEVEL * np.repeat(bits, SAMPLES_PER_BIT, axis=1)
    traces[:, LEAK_SAMPLE] *= HW_SBOX[words ^ key].sum(axis=1) / 64
    traces += rng.normal(0, noise_std, traces.shape)
    return np.round(traces).astype(np.int16), words


def measure_snr(noise_std, n=9000, reps=20):
    peaks, floors = [], []
    for seed in range(reps):
        rng = np.random.default_rng(seed)
        key = rng.integers(0, 256, 16, dtype=np.uint8)
        traces, words = make_traces(n, key, False, rng, noise_std)
        snr = SNR(nc=256)
        snr.fit_u(traces, SBOX[words[:, :1] ^ key[0]].astype(np.uint16))
        values = np.nan_to_num(snr.get_snr()[0])
        peaks.append(values[LEAK_SAMPLE])
        floors.append(np.median(np.delete(values, LEAK_SAMPLE)))
    return np.mean(peaks), np.mean(floors)


def calibrate_noise(target_peak, n):
    low, high = 0.0, 50.0
    for _ in range(25):
        mid = (low + high) / 2
        if measure_snr(mid, n)[0] > target_peak:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def key_rank_log2(scores, key):
    costs = -np.log(np.clip(scores, 1e-12, 1.0))
    _, rank, _ = rank_nbin(costs, key.astype(np.int64), 1 << 16, method="hist")
    return np.log2(max(1.0, rank))


def run_once(communication, seed, checkpoints, noise_std=NOISE_STD, select_high=False):
    rng = np.random.default_rng(seed)
    key = rng.integers(0, 256, 16, dtype=np.uint8)
    cpa = Cpa(nc=256, kind=Cpa.Xor)
    snr = SNR(nc=256)

    result = {name: [] for name in ("snr", "rho_true", "rho_wrong", "rank")}
    done = 0
    for n in checkpoints:
        traces, words = make_traces(n - done, key, communication, rng, noise_std)
        done = n
        if select_high:
            keep = traces[:, LEAK_SAMPLE] > HIGH_LEVEL / 2
            traces, words = traces[keep], words[keep]
        cpa.fit_u(traces, words.astype(np.uint16))
        snr.fit_u(traces, SBOX[words[:, :1] ^ key[0]].astype(np.uint16))
        snr_values = np.nan_to_num(snr.get_snr()[0])
        result["snr"].append(snr_values[LEAK_SAMPLE] - np.median(np.delete(snr_values, LEAK_SAMPLE)))
        corr = np.nan_to_num(cpa.get_correlation(MODEL))
        result["rho_true"].append(np.mean([corr[j, key[j], LEAK_SAMPLE] for j in range(16)]))
        wrong = np.abs(corr)
        wrong[np.arange(16), key, :] = 0
        result["rho_wrong"].append(wrong.max(axis=(1, 2)).mean())
        result["rank"].append(key_rank_log2(np.abs(corr).max(axis=2), key))
    return {name: np.array(values) for name, values in result.items()}


def traces_to_recover(rank, checkpoints):
    for i in range(len(rank)):
        if (rank[i:] <= 1e-9).all():
            return checkpoints[i]
    return np.inf


def plot_rank(checkpoints, ranks, needed_median, n_max, out):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for (name, rank), style in zip(ranks.items(), STYLES):
        ax.plot(checkpoints, rank.mean(axis=0), lw=1.8, label=name, **style)
        ax.fill_between(checkpoints, rank.min(axis=0), rank.max(axis=0), alpha=0.15, color=style["color"], lw=0)
        n = needed_median[name]
        ax.plot(n, 0, "v", color=style["color"], clip_on=False, zorder=5)
        ax.annotate(f"{n:.0f}", (n, 0), xytext=(-15, 8), textcoords="offset points", ha="left",
                    color=style["color"], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(200, n_max)
    ax.set_ylim(-3, 132)
    ax.set_xlabel("Number of traces")
    ax.set_ylabel(r"$\log_2$ key rank")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, fontsize=8, frameon=False)
    ax.grid(alpha=0.3)
    save_figure(fig, out, "fig9_nrz_rank")


def plot_snr(checkpoints, snrs, n_max, out):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for (name, snr), style in zip(snrs.items(), STYLES):
        ax.plot(checkpoints, snr.mean(axis=0), lw=1.8, label=name, **style)
        ax.fill_between(checkpoints, snr.min(axis=0), snr.max(axis=0), alpha=0.15, color=style["color"], lw=0)
    ax.axhline(0.069 - 0.03, color="k", ls=":", lw=1, label="paper (0.069 - 0.03)")
    ax.set_xscale("log")
    ax.set_xlim(2000, n_max)
    ax.set_ylim(-0.005, 0.07)
    ax.set_xlabel("number of traces")
    ax.set_ylabel("SNR (peak - floor)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, fontsize=8, frameon=False)
    ax.grid(alpha=0.3)
    save_figure(fig, out, "fig9_nrz_snr")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 9: impact of concurrent NRZ communication on the attack (simulation)")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--n-max", type=int, default=200000)
    parser.add_argument("--out", default="results")
    parser.add_argument("--noise", type=float, default=NOISE_STD)
    parser.add_argument("--replot", action="store_true")
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--target-snr", type=float, default=0.069)
    parser.add_argument("--calibrate-n", type=int, default=9000)
    args = parser.parse_args(argv)

    if args.calibrate:
        noise = calibrate_noise(args.target_snr, args.calibrate_n)
        peak, floor = measure_snr(noise, args.calibrate_n)
        print(f"noise_std = {noise:.3f} -> SNR peak = {peak:.4f}, floor = {floor:.4f} (paper: {args.target_snr}, ~0.03)")
        return

    os.makedirs(args.out, exist_ok=True)
    results_path = os.path.join(args.out, "fig9_nrz_results.npz")

    if args.replot:
        saved = np.load(results_path)
        ranks = dict(zip(CASES, saved["ranks"]))
        needed_median = dict(zip(CASES, saved["needed_median"]))
        snrs = dict(zip(CASES, saved["snrs"]))
        plot_rank(saved["checkpoints"], ranks, needed_median, int(saved["n_max"]), args.out)
        plot_snr(saved["checkpoints"], snrs, int(saved["n_max"]), args.out)
        return

    checkpoints = np.unique(np.concatenate([
        np.round(np.geomspace(100, args.n_max, 20)).astype(int), [REFERENCE_N]]))
    reference = int(np.where(checkpoints == REFERENCE_N)[0][0])

    rows = []
    ranks = {}
    snrs = {}
    needed_median = {}
    for name, (communication, select_high) in CASES.items():
        runs = []
        for seed in range(args.reps):
            print(f"{name}: experiment {seed + 1}/{args.reps}", flush=True)
            runs.append(run_once(communication, seed, checkpoints, args.noise, select_high))
        ranks[name] = np.array([r["rank"] for r in runs])
        snrs[name] = np.array([r["snr"] for r in runs])
        needed = np.array([traces_to_recover(r["rank"], checkpoints) for r in runs])
        row = (name,
               np.mean([r["snr"][reference] for r in runs]),
               np.mean([r["rho_true"][reference] for r in runs]),
               np.mean([r["rho_wrong"][reference] for r in runs]),
               np.median(needed),
               np.isfinite(needed).mean())
        rows.append(row)
        needed_median[name] = row[4]
        print(f"{row[0]:>24} | {row[1]:>7.4f} | {row[2]:>8.3f} {row[3]:>9.3f} | {row[4]:>7.0f} | {row[5]:>6.0%}")

    np.savetxt(os.path.join(args.out, "fig9_nrz_table.csv"), np.array(rows, dtype=object),
               fmt="%s", delimiter=",", header="case,snr,rho_true,rho_wrong,traces_needed,success", comments="")
    np.savez(results_path, checkpoints=checkpoints, names=list(ranks), ranks=np.array(list(ranks.values())),
             snrs=np.array(list(snrs.values())),
             needed_median=[needed_median[name] for name in ranks], n_max=args.n_max)
    plot_rank(checkpoints, ranks, needed_median, args.n_max, args.out)
    plot_snr(checkpoints, snrs, args.n_max, args.out)


if __name__ == "__main__":
    main()
