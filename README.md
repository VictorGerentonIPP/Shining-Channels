# Shining Channels: Long-Range Side-Channel Attacks over Optical Fiber - TCHES 2027, Vol.1 - Artifact

- **Paper:** Shining Channels: Long-Range Side-Channel Attacks over Optical Fiber (IACR TCHES Vol.1)
- **Data (Zenodo):** https://doi.org/10.5281/zenodo.23534084
- **License:** GNU GPL version 3 (code), CC-BY 4.0 (data)

## Abstract

This artifact reproduces the analysis of the paper: the SNR and correlation power analysis (CPA) of the optical and electromagnetic traces acquired on a commercial SFP module, the key-rank estimation as a function of the number of traces (at 0 dBm and at -11 dBm), and the simulation of the impact of concurrent NRZ communication.
The acquisition itself requires the target SFP module, a PIN photodiode and an oscilloscope; it is not reproducible without that hardware. The traces are therefore provided as three datasets on Zenodo, and the artifact downloads them automatically.

## Reproduced results

| Paper element | What it shows | Command |
|---|---|---|
| Table 2 (Section 7.2) | Per-byte CPA results on the 9 000 optical traces at 0 dBm. For each of the 16 key bytes: the correlation peak of the correct sub-key, the highest peak among the 255 wrong hypotheses, and the rank of the correct sub-key among the 256 candidates. All 16 sub-keys are ranked first, so the full AES-128 key is recovered. | `table2` |
| Figure 2 (Section 5.4) | SNR of the electromagnetic traces along the acquisition window (classes: first-round SubBytes output, key byte 5). It locates in time the data-dependent leakage of the SoC, which appears as a single peak above the noise floor. | `fig2` |
| Figure 4 (Section 6.2) | One optical trace showing the laser gating: the laser is switched on and off around the targeted operation of the first round, and the rising edge of the optical signal triggers the oscilloscope. | `fig4` |
| Figure 5 (Section 7.1) | SNR of the optical traces (classes: first-round SubBytes output, key byte 0). The peak above the noise floor shows that the data-dependent leakage reaches the emitted light. | `fig5` |
| Figure 6 (Section 7.2) | CPA correlation of the 256 hypotheses for key byte 0 over the 9 000 optical traces. The correct hypothesis (0x54) stands out clearly from the 255 others. | `fig6` |
| Figure 7 (Section 7.3) | Estimated log2 rank of the full 128-bit key versus the number of optical traces, at 0 dBm (mean over 100 independent attacks). The rank falls to 0, i.e. full recovery, after a few thousand traces. | `fig7` |
| Figure 8 (Section 7.4) | Same key-rank estimation at a received power of about -11 dBm, which emulates the loss budget of a link of about 55 km. The key is still recovered, with many more traces than at 0 dBm. | `fig8` |
| Figure 9 (Section 9.1) | Simulation of the impact of concurrent NRZ communication on the attack: log2 key rank versus number of traces for three scenarios (no communication, random NRZ bits, NRZ bits with selection of the traces in the high state). | `fig9` |

## Requirements

- Docker (recommended). A native Python installation is also possible, see [Reproduction without Docker](docs/reproduction-without-docker.md).
- Disk: about 6 GB for the three datasets (the largest archive, 5 GB, is deleted after extraction; up to about 10 GB are used temporarily). Only `sfp_0dbm` (450 MB) is needed for Table 2 and Figures 4, 5, 6 and 7.
- CPU: the key-rank figures are the longest steps and run on several cores.
- Architecture: x86_64 uses a prebuilt `scalib` wheel. On ARM (for example Apple Silicon), `scalib` is compiled from source when the Docker image is built, which adds about 2 minutes.

Dependencies are declared in `pyproject.toml` (version ranges) and `requirements.txt` (exact versions used for the paper: Python 3.13, numpy 2.4.2, matplotlib 3.10.8, scalib 0.6.4).

## Installation

### Get the artifact

```bash
git clone https://github.com/VictorGerentonIPP/Shining-Channels.git
```

```bash
cd Shining-Channels
```

### With Docker

```bash
docker build -t shining-channels .
```

To run the artifact without Docker, see [Reproduction without Docker](docs/reproduction-without-docker.md).

## Quick start (a few minutes)

This runs Table 2 and Figures 4, 5 and 6 on the smallest dataset (`sfp_0dbm`, 450 MB, downloaded automatically).

```bash
docker run --rm \
    -v "$PWD/data:/artifact/data" \
    -v "$PWD/results:/artifact/results" \
    shining-channels table2 fig4 fig5 fig6
```

Expected output:

```
byte  0: rank 1/256
...
|rho|c 0.169 0.149 0.155 ...
SNR peak: 0.069 at sample 46187
```

The figures and tables are written in `results/`.

## Full reproduction

```bash
docker run --rm \
    -v "$PWD/data:/artifact/data" \
    -v "$PWD/results:/artifact/results" \
    shining-channels
```

This downloads the three datasets (about 6 GB) and runs every step with the parameters of the paper.

| Step | Output in `results/` | Dataset | Duration (On MacBook Pro M4 Max 128 Go) |
|---|---|---|---|
| `table2` | `table2.txt`, `table2.tex` | `sfp_0dbm` | a few seconds |
| `fig2` | `fig2_snr_em.{png,pdf}` | `sfp_em` | a few seconds |
| `fig4` | `fig4_trace.{png,pdf}` | `sfp_0dbm` | a few seconds |
| `fig5` | `fig5_snr_optical.{png,pdf}` | `sfp_0dbm` | a few seconds |
| `fig6` | `fig6_cpa_byte0.{png,pdf}` | `sfp_0dbm` | a few seconds |
| `fig7` | `fig7_keyrank.{png,pdf,npz}` | `sfp_0dbm` | about 15 min |
| `fig8` | `fig8_keyrank_attenuated.{png,pdf,npz}` | `sfp_attenuated` | about 9 min |
| `fig9` | `fig9_nrz_rank.{png,pdf}`, `fig9_nrz_snr.{png,pdf}`, `fig9_nrz_results.npz`, `fig9_nrz_table.csv` | none (simulation) | about 2 min |

Any subset of steps can be selected by listing them after the image name, for example `shining-channels fig5 fig7`. Only the datasets needed by the selected steps are downloaded.

### Choosing the time and space budget

The default parameters are the ones of the paper. They can be changed on the command line, after the image name:

| Option | Steps | Meaning | Default |
|---|---|---|---|
| `--points` | `fig7`, `fig8` | number of trace counts on the x axis | 100 |
| `--experiments` | `fig7`, `fig8` | independent attacks per trace count | 100 |
| `--seed` | `fig7`, `fig8` | random seed | 0 |
| `--reps` | `fig9` | independent experiments | 10 |
| `--data` | all | directory of the datasets | `data` |
| `--out` | all | directory of the results | `results` |

For example:

```bash
docker run --rm \
    -v "$PWD/data:/artifact/data" \
    -v "$PWD/results:/artifact/results" \
    shining-channels fig7 --points 10 --experiments 10
```

takes less than a minute. With fewer experiments, the curves are noisier and the medians of Figure 9 differ slightly from the paper.
Without Docker, the same options apply to `shining-run-all`, and each figure can also be run alone (see [Reproduction without Docker](docs/reproduction-without-docker.md)).

### Assembling the results in LaTeX

`latex/results.tex` includes the table and all the figures produced in `results/`:

```bash
cd latex && pdflatex results.tex
```


## Datasets

Three datasets are hosted on Zenodo and downloaded automatically (`shining-download`) into `data/`. Each one is an uncompressed zip archive that extracts to a folder with `traces.npy` (int8, one row per trace), `plaintexts.npy`, `key.txt` and `metadata.json`.

| Dataset | Traces | Samples | Signal |
|---|---|---|---|
| `sfp_0dbm` | 9 000 | 50 002 | optical, about 0 dBm, 1 m of fiber |
| `sfp_attenuated` | 100 000 | 50 002 | optical, about -11 dBm (emulates a link of about 55 km) |
| `sfp_em` | 100 000 | 5 002 | electromagnetic, near-field probe |

Content of each archive (folder `<dataset>/`):

- `traces.npy`: `int8` array of shape `(n_traces, n_samples)`, raw oscilloscope ADC codes. The voltage of a sample is `adc * vertical_gain_v - vertical_offset_v`.
- `plaintexts.npy`: `uint8` array of shape `(n_traces, 16)`. The plaintexts are chained: each one is the AES-128 ciphertext of the previous one, starting from the same first plaintext in the three datasets.
- `key.txt`: the AES-128 key (fixed), one hexadecimal byte per line.
- `metadata.json`: number of traces and samples, sample interval (seconds), vertical gain and offset (volts).

All traces are acquired at 1 GS/s. The optical traces are aligned on the rising edge of the optical signal, produced when the laser is enabled (about sample 6200 in `sfp_0dbm` and 5300 in `sfp_attenuated`); the electromagnetic traces are triggered by the same optical edge.

The `.npy` format was chosen because the traces are about 5 GB of 8-bit samples, which would be impractical as text.

## Hardware used for the acquisition (not needed to run the artifact)

- **Target:** a commercial SFP module with a MIPS SoC at 400 MHz running Linux (FS - SKU 133619), plugged into an Ethernet switch
- **Optical chain:** a 1 m single-mode fiber from the SFP to a PIN photodiode (DXM21AF, 21 GHz bandwidth).
- **Oscilloscope:** Teledyne LeCroy, 4 GHz analog bandwidth, 8-bit vertical resolution.
- **Acquisition:** 1 GS/s over a 50 microsecond window, triggered by the rising edge of the optical signal.

See Section 6 of the paper.

## Organization of the code

```
src/shining_channels/
    attack.py        S-box, CPA, SNR and key-rank estimation (SCALib)
    data.py          dataset loading and download from Zenodo
    plotting.py      figure saving, key-rank figures
    run_all.py       command line entry point (shining-run-all)
    figures/         one module per table or figure
latex/results.tex    assembles the results
docs/                reproduction without Docker
```


## Clean

```bash
docker rmi shining-channels
rm -rf data results
```

## License

This work is licensed under the GNU General Public License version 3 (see `LICENSE`). The datasets hosted on Zenodo are licensed under CC-BY 4.0.

## Citation

Waiting for TCHES DOI.
