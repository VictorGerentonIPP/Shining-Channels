import argparse
import hashlib
import json
import os
import urllib.request
import zipfile

import numpy as np

HOST = "https://zenodo.org"
RECORD = "23534084"
DATASETS = ["sfp_0dbm", "sfp_attenuated", "sfp_em"]


def load_dataset(path):
    traces = np.load(os.path.join(path, "traces.npy"), mmap_mode="r")
    plaintexts = np.load(os.path.join(path, "plaintexts.npy"))
    with open(os.path.join(path, "key.txt")) as f:
        key = np.array([int(line, 16) for line in f.read().split()], dtype=np.uint8)
    return traces, plaintexts, key


def url(name):
    return f"{HOST}/records/{RECORD}/files/{name}?download=1"


def md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def download(name, path):
    with urllib.request.urlopen(url(name)) as response, open(path, "wb") as f:
        total = int(response.headers["Content-Length"])
        done = 0
        while block := response.read(1 << 22):
            f.write(block)
            done += len(block)
            print(f"\r{name}: {done / 1e6:.0f}/{total / 1e6:.0f} MB", end="", flush=True)
    print()


def fetch_datasets(datasets, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    with urllib.request.urlopen(f"{HOST}/api/records/{RECORD}") as response:
        checksums = {f["key"]: f["checksum"].split(":", 1)[1] for f in json.load(response)["files"]}
    for dataset in datasets:
        if os.path.exists(os.path.join(data_dir, dataset, "traces.npy")):
            print(f"{dataset}: already downloaded")
            continue
        archive = os.path.join(data_dir, f"{dataset}.zip")
        download(f"{dataset}.zip", archive)
        assert md5(archive) == checksums[f"{dataset}.zip"], f"checksum mismatch for {dataset}.zip"
        with zipfile.ZipFile(archive) as z:
            z.extractall(data_dir)
        os.remove(archive)
        print(f"{dataset}: ready")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download the datasets from Zenodo")
    parser.add_argument("datasets", nargs="*", default=DATASETS)
    parser.add_argument("--data", default="data")
    args = parser.parse_args(argv)
    fetch_datasets(args.datasets, args.data)


if __name__ == "__main__":
    main()
