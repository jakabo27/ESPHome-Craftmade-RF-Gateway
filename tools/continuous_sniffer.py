#!/usr/bin/env python3
"""
continuous_sniffer.py
Connects to an ESPHome device over its native API and captures raw RF pulse timings
from remote_receiver dumps into a timestamped log file for protocol reverse-engineering.
"""

import asyncio
import logging
import re
import sys
from datetime import datetime
from aioesphomeapi import APIClient

ESPHOME_HOST = "ceiling-fan-rf.local"
ESPHOME_PORT = 6053
OUTPUT_FILE = "captured_signals.log"

RAW_PULSE_PATTERN = re.compile(r"Received Raw:\s*([0-9\s,\-]+)")

async def main():
    print(f"Connecting to ESPHome device at {ESPHOME_HOST}:{ESPHOME_PORT}...")
    client = APIClient(ESPHOME_HOST, ESPHOME_PORT, password="")

    await client.connect(login=True)
    device_info = await client.device_info()
    print(f"Connected to: {device_info.name} (ESPHome version {device_info.esphome_version})")

    def on_log(msg):
        text = msg.message
        match = RAW_PULSE_PATTERN.search(text)
        if match:
            raw_str = match.group(1).strip()
            # Clean up comma/spaces into integers
            try:
                pulses = [int(p.strip()) for p in raw_str.replace("\n", " ").split(",") if p.strip()]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                entry = f"[{now}] Count={len(pulses)}: {pulses}\n"
                print(f"Captured: {len(pulses)} pulses -> {pulses[:8]} ... {pulses[-3:]}")
                with open(OUTPUT_FILE, "a") as f:
                    f.write(entry)
            except ValueError:
                pass

    await client.subscribe_logs(on_log, log_level=logging.DEBUG)
    print(f"Listening for RF signals... Press Ctrl+C to exit. Output will be saved to '{OUTPUT_FILE}'.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nStopping sniffer...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
