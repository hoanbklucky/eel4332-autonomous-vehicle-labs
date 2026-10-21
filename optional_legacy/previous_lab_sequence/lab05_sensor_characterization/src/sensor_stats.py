"""Starter sensor-statistics utility.

Expected CSV input: one numeric sample per row, optionally with a header.
Students may adapt this loader to the instructor's exported data format.
"""

from __future__ import annotations
import argparse
import numpy as np


def summarize(values: np.ndarray) -> dict:
    """Summarize a nonempty sequence of numeric sensor samples.

    Parameters:
      values: one-dimensional numeric samples in the signal's documented unit

    Returns:
      dict: required statistic names mapped to numeric summary values; statistics
      retain the input unit or its square as appropriate

    Raises:
      ValueError: if no samples are provided

    TODO: compute the summary statistics required by the lab.
    """
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        raise ValueError("No samples provided")

    # TODO: compute the required summary statistics.
    raise NotImplementedError("Implement sensor summary statistics")


def main():
    """Load the first numeric CSV column and print its summary statistics.

    Command-line parameters:
      csv: path to a CSV file containing one numeric signal, optionally headed

    Returns:
      None. Prints the dictionary returned by summarize.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()

    values = np.genfromtxt(args.csv, delimiter=",", names=True)
    if values.dtype.names:
        first = values.dtype.names[0]
        data = np.asarray(values[first], dtype=float)
    else:
        data = np.asarray(values, dtype=float)

    print(summarize(data))


if __name__ == "__main__":
    main()
