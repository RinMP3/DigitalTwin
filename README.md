<p align="center">
DigitalTwin
</p>

<p align="center">
  <b>Core Micro-Benchmark & Silicon Intergrity Matrix</b>
</p>


---

### What is DigitalTwin?

**DigitalTwin** is a high-performance engineering utility designed to bridge the gap between software execution and silicon behavior. Modern GPUs are complex systems with aggressive power management, dynamic boost clocks, and intricate thermal limits. DigitalTwin acts as a direct diagnostic core that targets specific execution units on the chip—isolating workloads between **FP32 ALU** and **Tensor Cores** to test how hardware responds under extreme stress.

Instead of generic load generation, the tool creates precise **transient loads**, forcing the onboard VRM and power delivery networks to instantly jump from idle states to maximum consumption. This exposes micro-fluctuations, validates thermal headroom, and maps out the absolute operational boundaries of the silicon.

---

### Key Capabilities

* **Targeted Logic Block Stress**: Bypasses generic rendering pipelines to hammer raw arithmetic and matrix multiplication units directly.
* **Real-Time Telemetry Mapping**: Instantly captures baseline metrics, peak thermal spikes, temperature deltas ($\Delta T$), and power fluctuations ($\Delta W$).
* **Silicon Integrity Scoring**: Evaluates performance outputs and thermal behavior against configurable threshold profiles to output a definitive hardware health score.
* **Automated Stability Sweep (`Stress Sweep`)**: Incrementally scales test intensity step-by-step to find the exact breaking point where the chip or driver encounters computation errors.
* **Clean Diagnostic Reporting**: Exports professional, clutter-free technical reports detailing checksum integrity, TFLOPS performance, and sensor deltas.

---

### Architecture Breakdown

```text
DigitalTwin/
├── main.py         # CLI interface, Rich-based UI dashboards, and reporting
├── sweeper.py      # Core profiling logic and incremental stress sweep engine
├── telemetry.py    # Hardware sensor monitoring and metric collection
├── kernels.py      # Low-level compute execution blocks (ALU & Tensor routines)
├── run.bat         # bat file to run applicaton
└── config.json     # Custom silicon integrity thresholds & limits
```
---

### Quick Start Guide

1. Install Python 3.12
```sh
https://www.python.org/downloads/release/python-3120/
```
2. Install dependencies
```sh
pip install rich
```
3. Clone Repository
```sh
git clone https://github.com/RinMP3/DigitalTwin.git
cd DigitalTwin
```
4. Run application
```sh
Double-click run.bat
```
5. If bat doesn't work
```sh
python main.py
```


---

### Once launched, the interactive dashboard lets you command the profiler on the fly:

[S] Stress Sweep: Automatically ramps up iteration thresholds step-by-step up to 1,000,000 to test silicon resilience limits.

[R] Run Again: Instantly re-executes the profiling sequence with current parameters.

[D] Export Report: Dumps a clean, formatted text log containing all telemetry and structural metrics into your working directory.

[Q] Quit: Safely exits the diagnostic environment.

---

> [!NOTE]
> This Product was not sponsored by Nvidia or any other company.

> [!IMPORTANT]
> This Product was made exclusively for Blackwell Chips.

<details>
  <summary><b> Screenshots </b></summary>
  <br>
  <img width="1105" height="620" alt="Screenshot 2026-08-28 022329" src="https://github.com/user-attachments/assets/b54907ad-81cc-401c-a866-370a62d03880" />
  <img width="518" height="596" alt="Screenshot 2026-08-28 022358" src="https://github.com/user-attachments/assets/541c90f8-7c67-4f34-94b9-2a9a2c6d4205" />
</details>
