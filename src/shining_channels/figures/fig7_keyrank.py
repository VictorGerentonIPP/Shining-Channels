import argparse

from shining_channels.plotting import key_rank_figure


def main(argv=None):
    parser = argparse.ArgumentParser(description="Figure 7: log2 key rank versus number of optical traces")
    parser.add_argument("--data", default="data/sfp_0dbm")
    parser.add_argument("--out", default="results")
    parser.add_argument("--max-traces", type=int, default=9000)
    parser.add_argument("--points", type=int, default=100)
    parser.add_argument("--experiments", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--no-locate", action="store_true")
    args = parser.parse_args(argv)

    name = "fig7_keyrank_nolocate" if args.no_locate else "fig7_keyrank"
    key_rank_figure(args.data, args.out, name, args.max_traces, args.points, args.experiments,
                    seed=args.seed, locate=not args.no_locate)


if __name__ == "__main__":
    main()
