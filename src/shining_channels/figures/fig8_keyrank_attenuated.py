import argparse

from shining_channels.plotting import key_rank_figure


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 8: log2 key rank versus number of traces at -11 dBm")
    parser.add_argument("--data", default="data/sfp_attenuated")
    parser.add_argument("--out", default="results")
    parser.add_argument("--max-traces", type=int, default=100000)
    parser.add_argument("--points", type=int, default=100)
    parser.add_argument("--experiments", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    key_rank_figure(args.data, args.out, "fig8_keyrank_attenuated", args.max_traces, args.points,
                    args.experiments, seed=args.seed)


if __name__ == "__main__":
    main()
