# Craftmade 303.875 MHz RF Protocol Analysis & Reverse Engineering

This document details the reverse engineering and signal analysis of the proprietary Sub-1 GHz RF protocol used by the Craftmade ceiling fan and light wall remote control.

---

## 1. Physical Layer Characteristics

* **Carrier Frequency:** `303.875 MHz`
  * Controlled by a SAW (Surface Acoustic Wave) resonator on the physical remote's PCB.
* **Modulation:** On-Off Keying (OOK) / Amplitude Shift Keying (ASK).
* **RF Duty Cycle:** 100% carrier pulse during transmit (`carrier_duty_percent: 100%`).
* **Receiver Filter Bandwidth:** `406 kHz` (Configured in the CC1101 to compensate for SAW resonator drift and manufacturing tolerances).

---

## 2. Pulse Structure & Timing Metrics

Each transmission burst consists of:
* **24 alternating mark/space pulses** forming 12 symbols.
* **1 trailing mark pulse** (25th pulse).
* **1 trailing sync space gap** (26th pulse) lasting approximately `11.9 ms` before the packet repeats.

Total packet count = **26 items**.

### Base Units

| Symbol Type | Duration Range | Nominal Metric | Description |
| :--- | :--- | :--- | :--- |
| **Short Mark ($s$)** | $300\text{–}340\,\mu\text{s}$ | $\sim 330\,\mu\text{s}$ | High carrier pulse ($T$) |
| **Short Space ($s$)** | $340\text{–}375\,\mu\text{s}$ | $\sim 355\,\mu\text{s}$ | Low carrier pulse ($T$) |
| **Long Mark ($L$)** | $640\text{–}655\,\mu\text{s}$ | $\sim 650\,\mu\text{s}$ | High carrier pulse ($2T$) |
| **Long Space ($L$)** | $700\text{–}715\,\mu\text{s}$ | $\sim 708\,\mu\text{s}$ | Low carrier pulse ($2T$) |
| **Sync Gap** | $11,890\text{–}11,920\,\mu\text{s}$ | $\sim 11.9\,\text{ms}$ | Inter-packet repeat separation |

---

## 3. Frame Decomposition

The 12 symbols (24 mark/space intervals) divide into two 6-symbol fields:

```
[ Symbol 0 - 5 : Address Word ] [ Symbol 6 - 11 : Command Word ] [ Trailing Mark ] [ Sync Gap ]
```

### 3.1 Address Word (Fixed)

The address word is uniquely matched to the physical canopy receiver DIP/code setting and remains identical across all 7 buttons:

$$\text{Address} = \texttt{ss Ls LL ss LL sL}$$

### 3.2 Command Word (Fan Speeds & Power)

The fan control commands implement a 5-position barrel shift of the pair `ss LL` across four trailing `sL` symbols:

| Command | Symbols (6 to 11) | Trailing Mark |
| :--- | :--- | :--- |
| **Fan High (Speed 3)** | `ss LL sL sL sL sL` | `s` ($\sim 310\,\mu\text{s}$) |
| **Fan Medium (Speed 2)** | `sL ss LL sL sL sL` | `s` ($\sim 309\,\mu\text{s}$) |
| **Fan Low (Speed 1)** | `sL sL ss LL sL sL` | `s` ($\sim 312\,\mu\text{s}$) |
| **Fan Reverse** | `sL sL sL ss LL sL` | `s` ($\sim 311\,\mu\text{s}$) |
| **Fan Off** | `sL sL sL sL ss LL` | `s` ($\sim 311\,\mu\text{s}$) |

### 3.3 Command Word (Light Toggles)

Light commands terminate with a **long mark** ($L \approx 645\text{–}653\,\mu\text{s}$) on the 25th pulse instead of a short mark:

| Command | Symbols (6 to 11) | Trailing Mark |
| :--- | :--- | :--- |
| **Light 1 (L-1 Toggle)** | `sL sL ss LL sL ss` | `L` ($\sim 645\,\mu\text{s}$) |
| **Light 2 (L Toggle)** | `sL sL sL sL sL ss` | `L` ($\sim 653\,\mu\text{s}$) |

---

## 4. Full Mean Pulse Timings (Microseconds)

These exact arrays were computed from sniffer logs using `tools/analyze_signals.py`:

```yaml
# Light 1 Toggle
[332, -352, 646, -371, 640, -712, 303, -374, 638, -713, 301, -713, 308, -705, 307, -713, 304, -366, 648, -706, 309, -707, 308, -365, 645, -11916]

# Light 2 Toggle
[337, -341, 655, -362, 648, -701, 311, -366, 646, -705, 307, -708, 307, -707, 306, -707, 310, -707, 305, -708, 311, -702, 310, -362, 653, -11894]

# Fan High (Speed 3)
[338, -342, 654, -363, 648, -704, 312, -364, 646, -705, 307, -707, 308, -367, 650, -701, 308, -706, 307, -707, 311, -705, 309, -705, 310, -11904]

# Fan Medium (Speed 2)
[336, -346, 653, -364, 647, -706, 302, -375, 639, -707, 307, -714, 300, -712, 305, -369, 646, -705, 308, -709, 306, -707, 309, -707, 309, -11911]

# Fan Low (Speed 1)
[335, -351, 653, -361, 646, -708, 306, -366, 650, -702, 308, -710, 307, -706, 308, -706, 313, -412, 599, -703, 310, -708, 308, -704, 312, -11907]

# Fan Reverse
[331, -353, 651, -363, 648, -706, 308, -365, 649, -703, 308, -706, 310, -705, 310, -704, 310, -705, 312, -363, 649, -702, 308, -706, 311, -11896]

# Fan Off
[335, -347, 651, -362, 648, -708, 310, -361, 647, -708, 308, -708, 304, -707, 307, -707, 310, -708, 305, -708, 309, -363, 651, -702, 311, -11902]
```
