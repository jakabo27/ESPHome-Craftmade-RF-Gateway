#!/usr/bin/env python3
"""
analyze_signals.py
Analyzes logged raw RF pulses, groups them by packet length, filters outliers,
and computes mean pulse timing arrays ready for ESPHome remote_transmitter.transmit_raw.
"""

import sys
import re
import numpy as np

def analyze_logfile(filepath, target_length=26):
    packets = []
    line_pattern = re.compile(r"Count=(\d+):\s*(\[.*?\])")

    with open(filepath, "r") as f:
        for line in f:
            match = line_pattern.search(line)
            if match:
                count = int(match.group(1))
                if count == target_length:
                    raw_str = match.group(2)
                    arr = eval(raw_str)
                    packets.append(arr)

    if not packets:
        print(f"No packets found matching target length {target_length}.")
        return

    print(f"Loaded {len(packets)} packets of length {target_length}.\n")
    arr = np.array(packets)
    means = np.mean(arr, axis=0).astype(int)
    stds = np.std(arr, axis=0).astype(int)

    print("Index | Mean Timing (µs) | Std Dev (µs)")
    print("-" * 40)
    for i, (m, s) in enumerate(zip(means, stds)):
        sign = "+" if m > 0 else "-"
        print(f"{i:5d} | {sign}{abs(m):6d} µs      | ±{s:4d} µs")

    print("\nESPHome transmit_raw YAML code format:")
    print("---------------------------------------")
    print(f"code: {list(means)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_signals.py <captured_signals.log> [target_length=26]")
        sys.exit(1)
    
    target_len = int(sys.argv[2]) if len(sys.argv) > 2 else 26
    analyze_logfile(sys.argv[1], target_len)
