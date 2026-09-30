#!/usr/bin/env python3
"""
decode_bits.py
Decodes raw Craftmade 303.875 MHz pulse arrays into high-level symbols (short 's' vs long 'L'),
extracting the 6-symbol address and the 6-symbol command payload.
"""

# Reference timing arrays extracted from physical remote
COMMANDS = {
    "Fan High (Speed 3)": [338, -342, 654, -363, 648, -704, 312, -364, 646, -705, 307, -707, 308, -367, 650, -701, 308, -706, 307, -707, 311, -705, 309, -705, 310, -11904],
    "Fan Medium (Speed 2)": [336, -346, 653, -364, 647, -706, 302, -375, 639, -707, 307, -714, 300, -712, 305, -369, 646, -705, 308, -709, 306, -707, 309, -707, 309, -11911],
    "Fan Low (Speed 1)": [335, -351, 653, -361, 646, -708, 306, -366, 650, -702, 308, -710, 307, -706, 308, -706, 313, -412, 599, -703, 310, -708, 308, -704, 312, -11907],
    "Fan Reverse": [331, -353, 651, -363, 648, -706, 308, -365, 649, -703, 308, -706, 310, -705, 310, -704, 310, -705, 312, -363, 649, -702, 308, -706, 311, -11896],
    "Fan Off": [335, -347, 651, -362, 648, -708, 310, -361, 647, -708, 308, -708, 304, -707, 307, -707, 310, -708, 305, -708, 309, -363, 651, -702, 311, -11902],
    "Light 1 Toggle": [332, -352, 646, -371, 640, -712, 303, -374, 638, -713, 301, -713, 308, -705, 307, -713, 304, -366, 648, -706, 309, -707, 308, -365, 645, -11916],
    "Light 2 Toggle": [337, -341, 655, -362, 648, -701, 311, -366, 646, -705, 307, -708, 307, -707, 306, -707, 310, -707, 305, -708, 311, -702, 310, -362, 653, -11894],
}

def decode_pulse(duration):
    """Classifies a pulse duration into 's' (short ~330µs) or 'L' (long ~650-700µs)."""
    d = abs(duration)
    if d < 500:
        return 's'
    elif d < 1200:
        return 'L'
    else:
        return 'SYNC'

def main():
    print("=" * 80)
    print("Craftmade 303.875 MHz RF Protocol Symbol Decomposition")
    print("=" * 80)

    for name, code in COMMANDS.items():
        symbols = []
        for i in range(0, 24, 2):
            mark = decode_pulse(code[i])
            space = decode_pulse(code[i+1])
            symbols.append(f"{mark}{space}")
        
        last_mark = decode_pulse(code[24])
        sync_space = f"{abs(code[25])}µs"

        address = " ".join(symbols[:6])
        command = " ".join(symbols[6:])

        print(f"\nCommand: {name}")
        print(f"  Address Word (6 syms): {address}")
        print(f"  Command Word (6 syms): {command}")
        print(f"  Trailing Mark: {last_mark} | Sync Space: {sync_space}")

if __name__ == "__main__":
    main()
