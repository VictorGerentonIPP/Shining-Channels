import argparse
import importlib

from shining_channels.data import fetch_datasets

STEPS = {
    "table2": ("table2_cpa_16bytes", "sfp_0dbm", ()),
    "fig2": ("fig2_snr_em", "sfp_em", ()),
    "fig4": ("fig4_trace", "sfp_0dbm", ()),
    "fig5": ("fig5_snr_optical", "sfp_0dbm", ()),
    "fig6": ("fig6_cpa_byte0", "sfp_0dbm", ()),
    "fig7": ("fig7_keyrank", "sfp_0dbm", ("points", "experiments", "seed")),
    "fig8": ("fig8_keyrank_attenuated", "sfp_attenuated", ("points", "experiments", "seed")),
    "fig9": ("fig9_nrz_simulation", None, ("reps",)),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download the datasets and regenerate the figures and tables of the paper")
    parser.add_argument("steps", nargs="*", choices=list(STEPS))
    parser.add_argument("--data", default="data")
    parser.add_argument("--out", default="results")
    parser.add_argument("--points", type=int, help="fig7, fig8: number of trace counts")
    parser.add_argument("--experiments", type=int, help="fig7, fig8: independent attacks per trace count")
    parser.add_argument("--seed", type=int, help="fig7, fig8: random seed")
    parser.add_argument("--reps", type=int, help="fig9: independent experiments")
    args = parser.parse_args(argv)
    steps = args.steps or list(STEPS)

    datasets = sorted({STEPS[step][1] for step in steps if STEPS[step][1]})
    if datasets:
        fetch_datasets(datasets, args.data)

    for step in steps:
        module, dataset, options = STEPS[step]
        step_args = ["--out", args.out]
        if dataset:
            step_args += ["--data", f"{args.data}/{dataset}"]
        for option in options:
            value = getattr(args, option)
            if value is not None:
                step_args += [f"--{option}", str(value)]
        print(f"== {step}", flush=True)
        importlib.import_module(f"shining_channels.figures.{module}").main(step_args)


if __name__ == "__main__":
    main()
