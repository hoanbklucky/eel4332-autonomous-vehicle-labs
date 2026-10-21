"""Generate repeatable synthetic inputs; this utility does not implement a filter."""

import argparse
from pathlib import Path

import numpy as np


def make_data(seed=4332):
    """Return paired normal/dropout tables sharing the same reference and noise."""
    t = np.arange(601, dtype=float) * 0.1
    position = np.where(t <= 30.0, 0.5 * t, 15.0 + 0.25 * (t - 30.0))
    velocity = np.where(t < 30.0, 0.5, 0.25)
    measured = position + np.random.default_rng(seed).normal(0.0, 0.25, t.size)
    normal = np.column_stack((t, measured, position, velocity))
    dropout = normal.copy()
    dropout[(t >= 25.0) & (t < 35.0), 1] = np.nan
    return normal, dropout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=4332)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output directory exists; choose a fresh path to preserve results")
    normal, dropout = make_data(args.seed)
    args.output.mkdir(parents=True)
    header = "time_s,measured_position_m,reference_position_m,reference_velocity_m_s"
    for filename, data in [("normal.csv", normal), ("dropout.csv", dropout)]:
        np.savetxt(args.output / filename, data, delimiter=",", header=header, comments="")
    (args.output / "metadata.txt").write_text(
        f"seed={args.seed}\ndt_s=0.1\nmeasurement_std_m=0.25\n"
        "dropout_start_s=25\ndropout_end_exclusive_s=35\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
