# Reproduction without Docker

This page describes how to run the artifact directly on your machine. The recommended way is Docker, described in the [README](../README.md); the results are the same.

## Requirements

- Python 3.10 or later. The artifact was tested with Python 3.13 (Docker image) and Python 3.14 (macOS, Apple Silicon).
- About 6 GB of disk space for the datasets (the largest archive, 5 GB, is deleted after extraction; up to about 10 GB are used temporarily). Only `sfp_0dbm` (450 MB) is needed for Table 2 and Figures 4, 5, 6 and 7.
- `scalib` provides prebuilt wheels for macOS (Intel and Apple Silicon), Linux x86_64 and Windows x86_64. On other platforms (for example Linux on ARM), `pip` compiles it from source, which needs a C compiler and a Rust toolchain ([rustup](https://rustup.rs)).

## Installation

```bash
git clone https://github.com/VictorGerentonIPP/Shining-Channels.git
```

```bash
cd Shining-Channels
```

Create a virtual environment and install the exact versions used for the paper, then the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install --no-deps .
```

`pip install .` alone also works and installs compatible versions of the dependencies (ranges declared in `pyproject.toml`).

## Quick start (a few minutes)

Table 2 and Figures 4, 5 and 6, on the smallest dataset (`sfp_0dbm`, 450 MB, downloaded automatically into `data/`):

```bash
shining-run-all table2 fig4 fig5 fig6
```

The figures and tables are written in `results/`.

## Full reproduction

```bash
shining-run-all
```

This downloads the three datasets (about 6 GB) and runs every step with the parameters of the paper. The steps, their outputs and their durations are listed in the [README](../README.md#full-reproduction).

Any subset of steps can be selected, for example `shining-run-all fig5 fig7`. Only the datasets needed by the selected steps are downloaded.

## Options

The options of the [README](../README.md#choosing-the-time-and-space-budget) apply after `shining-run-all`. For example:

```bash
shining-run-all fig7 --points 10 --experiments 10
```

takes less than a minute. With fewer experiments, the curves are noisier and the medians of Figure 9 differ slightly from the paper.

## Running one figure alone

Each table or figure is a module of the package, with its own options:

```bash
python -m shining_channels.figures.fig7_keyrank --help
python -m shining_channels.figures.fig7_keyrank --data data/sfp_0dbm --out results
```

The datasets can be downloaded separately:

```bash
shining-download                 # the three datasets
shining-download sfp_0dbm        # only one of them
```

## Headless machines

The figures are saved to files and never displayed. If your machine has no display, set `MPLBACKEND=Agg` before running.

## Clean

```bash
deactivate
rm -rf .venv data results
```
